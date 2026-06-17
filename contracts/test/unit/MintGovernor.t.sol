// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

import {Test} from "forge-std/Test.sol";
import {IAccessControl} from "@openzeppelin/contracts/access/IAccessControl.sol";

import {AugPocToken} from "../../src/token/AugPocToken.sol";
import {RoundRegistry} from "../../src/rounds/RoundRegistry.sol";
import {MintGovernor} from "../../src/governance/MintGovernor.sol";
import {IAugPocToken} from "../../src/interfaces/IAugPocToken.sol";
import {IRoundRegistry} from "../../src/interfaces/IRoundRegistry.sol";
import {IVotes} from "@openzeppelin/contracts/governance/utils/IVotes.sol";

/// @title  MintGovernor unit tests
/// @notice Covers the full Phase 2 flow on top of the unchanged RoundRegistry mint source:
///         nominal finalize, contestation → vote, reject → re-proposition → accept, concurrent
///         alternatives voted sequentially, snapshot anti-vote-buying, quorum/threshold boundaries,
///         double-execution impossibility, and keeper least-privilege.
contract MintGovernorTest is Test {
    AugPocToken internal token;
    RoundRegistry internal registry;
    MintGovernor internal governor;

    address internal admin = makeAddr("admin");
    address internal keeper = makeAddr("keeper");
    address internal minter = makeAddr("minter"); // test-only fast mint to seed balances
    address internal treasury = makeAddr("treasury");

    // Voters (seeded + self-delegated BEFORE any proposal).
    address internal whale = makeAddr("whale");
    address internal alice = makeAddr("alice");
    address internal bob = makeAddr("bob");
    address internal carol = makeAddr("carol");
    address internal attacker = makeAddr("attacker");

    // Round beneficiary (not a voter).
    address internal dave = makeAddr("dave");

    uint256 internal constant E = 1e18;
    uint256 internal constant START = 1_778_544_000; // 2026-05-09 UTC
    uint32 internal constant WINDOW_DAYS = 7;

    function setUp() public {
        token = new AugPocToken(admin);
        registry = new RoundRegistry(admin, IAugPocToken(address(token)));
        governor = new MintGovernor(admin, registry, IVotes(address(token)), address(0), 1500, 100, 7);

        vm.startPrank(admin);
        // Registry is the sole minter in production; we grant a test minter to seed voter balances
        // quickly without driving a full round (the sole-minter invariant is covered elsewhere).
        token.grantRole(token.MINTER_ROLE(), address(registry));
        token.grantRole(token.MINTER_ROLE(), minter);
        // Keeper proposes; Governor executes/cancels/challenges. Keeper holds NO role that mints
        // or changes roles.
        registry.grantRole(registry.ROUND_PROPOSER_ROLE(), keeper);
        // The Governor also proposes (to register re-proposition alternatives), and executes /
        // cancels / challenges. The keeper only proposes.
        registry.grantRole(registry.ROUND_PROPOSER_ROLE(), address(governor));
        registry.grantRole(registry.ROUND_EXECUTOR_ROLE(), address(governor));
        registry.grantRole(registry.ROUND_CANCELLER_ROLE(), address(governor));
        registry.grantRole(registry.ROUND_CHALLENGER_ROLE(), address(governor));
        vm.stopPrank();

        vm.warp(START);
    }

    /*//////////////////////////////////////////////////////////////
                                HELPERS
    //////////////////////////////////////////////////////////////*/

    function _mintAndDelegate(
        address who,
        uint256 amount
    ) internal {
        vm.prank(minter);
        token.mint(who, amount);
        vm.prank(who);
        token.delegate(who);
    }

    function _alloc(
        address ben,
        uint256 amount
    ) internal pure returns (address[] memory bens, uint256[] memory amts) {
        bens = new address[](1);
        bens[0] = ben;
        amts = new uint256[](1);
        amts[0] = amount;
    }

    function _hash(
        address[] memory bens,
        uint256[] memory amts,
        string memory uri
    ) internal pure returns (bytes32) {
        return keccak256(abi.encode(bens, amts, uri));
    }

    /// @dev Keeper proposes a round to `dave` for `amount`. Returns the round hash.
    function _propose(
        uint256 amount,
        string memory uri
    ) internal returns (bytes32 h) {
        (address[] memory bens, uint256[] memory amts) = _alloc(dave, amount);
        h = _hash(bens, amts, uri);
        vm.prank(keeper);
        registry.proposeRound(h, bens, amts, uri, WINDOW_DAYS);
    }

    /*//////////////////////////////////////////////////////////////
                          NOMINAL (UNCONTESTED)
    //////////////////////////////////////////////////////////////*/

    function test_Finalize_UncontestedMintsAfterWindow() public {
        bytes32 h = _propose(1000 * E, "ipfs://r1");

        // Before the window: finalize reverts (registry enforces the window).
        vm.expectRevert(IRoundRegistry.ChallengeWindowNotExpired.selector);
        governor.finalize(h);

        vm.warp(START + WINDOW_DAYS * 1 days);
        // Permissionless: anyone (here a random address) can finalize.
        vm.prank(makeAddr("anyone"));
        governor.finalize(h);

        assertEq(uint8(registry.statusOf(h)), uint8(IRoundRegistry.RoundStatus.Executed));
        assertEq(token.balanceOf(dave), 1000 * E);
    }

    function test_Finalize_RevertsOnChallengedRound() public {
        _mintAndDelegate(alice, 100 * E);
        vm.warp(START + 1);
        bytes32 h = _propose(1000 * E, "ipfs://r1");
        vm.warp(block.timestamp + 1);

        vm.prank(alice);
        governor.challenge(h, "ipfs://reason");

        // Even after the window, a challenged round is NOT finalizable — it must go through the vote.
        vm.warp(START + WINDOW_DAYS * 1 days + 1);
        vm.expectRevert(MintGovernor.NotFinalizable.selector);
        governor.finalize(h);
    }

    function test_Finalize_DoubleExecutionImpossible() public {
        bytes32 h = _propose(1000 * E, "ipfs://r1");
        vm.warp(START + WINDOW_DAYS * 1 days);
        governor.finalize(h);
        // Second finalize: round is Executed, not Proposed.
        vm.expectRevert(MintGovernor.NotFinalizable.selector);
        governor.finalize(h);
    }

    /*//////////////////////////////////////////////////////////////
                       CONTESTATION → VOTE OUTCOMES
    //////////////////////////////////////////////////////////////*/

    /// @dev Quorum reached AND against > for → original rejected (no mint of the original).
    function test_Challenge_RejectedWhenQuorumAndMajorityAgainst() public {
        _mintAndDelegate(whale, 700 * E);
        _mintAndDelegate(alice, 100 * E);
        // total supply at snapshot = 800; quorum = ceil(800 * 15%) = 120.
        vm.warp(START + 10);
        bytes32 h = _propose(1000 * E, "ipfs://r1");
        vm.warp(block.timestamp + 1);

        vm.prank(alice);
        governor.challenge(h, "ipfs://reason");

        // whale against (700), alice for (100): expressed 800 ≥ quorum 120, against > for → reject.
        vm.prank(whale);
        governor.castVote(h, false);
        vm.prank(alice);
        governor.castVote(h, true);

        vm.warp(block.timestamp + 7 days + 1);
        governor.resolve(h);

        assertEq(uint8(registry.statusOf(h)), uint8(IRoundRegistry.RoundStatus.Challenged), "original not executed");
        assertEq(token.balanceOf(dave), 0, "no mint of the rejected original");
        (,,,, bool originalDecided, bool resolved,,) = governor.getDispute(h);
        assertTrue(originalDecided);
        assertFalse(resolved);
    }

    /// @dev Quorum NOT reached → round validated as-is and executed (treated as uncontested).
    function test_Challenge_QuorumNotReachedValidatesRound() public {
        _mintAndDelegate(whale, 700 * E);
        _mintAndDelegate(alice, 100 * E);
        // total 800, quorum 120. Only alice (100) votes against → expressed 100 < 120 → not reached.
        vm.warp(START + 10);
        bytes32 h = _propose(1000 * E, "ipfs://r1");
        vm.warp(block.timestamp + 1);

        vm.prank(alice);
        governor.challenge(h, "ipfs://reason");
        vm.prank(alice);
        governor.castVote(h, false); // 100 against, below quorum

        vm.warp(block.timestamp + 7 days + 1);
        governor.resolve(h);

        assertEq(uint8(registry.statusOf(h)), uint8(IRoundRegistry.RoundStatus.Executed));
        assertEq(token.balanceOf(dave), 1000 * E, "validated round mints original allocation");
    }

    /// @dev Quorum reached but against == for (tie) → original upheld and executed.
    function test_Challenge_TieUpholdsRound() public {
        _mintAndDelegate(alice, 100 * E);
        _mintAndDelegate(bob, 100 * E);
        // total 200, quorum ceil(200*15%)=30. for 100 == against 100, expressed 200 ≥ 30.
        vm.warp(START + 10);
        bytes32 h = _propose(500 * E, "ipfs://r1");
        vm.warp(block.timestamp + 1);

        vm.prank(alice);
        governor.challenge(h, "ipfs://reason");
        vm.prank(alice);
        governor.castVote(h, true); // 100 for
        vm.prank(bob);
        governor.castVote(h, false); // 100 against

        vm.warp(block.timestamp + 7 days + 1);
        governor.resolve(h);

        assertEq(uint8(registry.statusOf(h)), uint8(IRoundRegistry.RoundStatus.Executed), "tie upholds");
        assertEq(token.balanceOf(dave), 500 * E);
    }

    /// @dev Boundary: expressed votes EXACTLY equal the quorum threshold → quorum reached (≥).
    function test_Challenge_ExactlyAtQuorumWithMajorityAgainstRejects() public {
        // total = 1000 → quorum = 150. Express exactly 150 with against (100) > for (50).
        _mintAndDelegate(whale, 850 * E); // abstains
        _mintAndDelegate(alice, 100 * E); // against
        _mintAndDelegate(bob, 50 * E); // for
        vm.warp(START + 10);
        bytes32 h = _propose(1000 * E, "ipfs://r1");
        vm.warp(block.timestamp + 1);

        vm.prank(alice);
        governor.challenge(h, "ipfs://reason");
        vm.prank(alice);
        governor.castVote(h, false); // 100 against
        vm.prank(bob);
        governor.castVote(h, true); // 50 for → expressed 150 == quorum

        vm.warp(block.timestamp + 7 days + 1);
        governor.resolve(h);

        assertEq(uint8(registry.statusOf(h)), uint8(IRoundRegistry.RoundStatus.Challenged), "rejected at exact quorum");
        assertEq(token.balanceOf(dave), 0);
    }

    /// @dev Boundary: one token below quorum → not reached → validated/executed even if all-against.
    function test_Challenge_JustBelowQuorumValidates() public {
        _mintAndDelegate(whale, 851 * E); // abstains
        _mintAndDelegate(alice, 149 * E); // against; total = 1000, quorum = 150
        vm.warp(START + 10);
        bytes32 h = _propose(1000 * E, "ipfs://r1");
        vm.warp(block.timestamp + 1);

        vm.prank(alice);
        governor.challenge(h, "ipfs://reason");
        vm.prank(alice);
        governor.castVote(h, false); // 149 against < 150 quorum

        vm.warp(block.timestamp + 7 days + 1);
        governor.resolve(h);

        assertEq(uint8(registry.statusOf(h)), uint8(IRoundRegistry.RoundStatus.Executed));
        assertEq(token.balanceOf(dave), 1000 * E);
    }

    /*//////////////////////////////////////////////////////////////
                       ANTI-VOTE-BUYING (SNAPSHOT)
    //////////////////////////////////////////////////////////////*/

    function test_Snapshot_TokensBoughtAfterProposalHaveNoWeight() public {
        _mintAndDelegate(alice, 100 * E);
        vm.warp(START + 10);
        bytes32 h = _propose(1000 * E, "ipfs://r1");

        // AFTER the proposal: attacker acquires a huge balance and self-delegates.
        vm.warp(block.timestamp + 1);
        _mintAndDelegate(attacker, 1_000_000 * E);

        vm.prank(alice);
        governor.challenge(h, "ipfs://reason");

        // The attacker's snapshot weight at proposedAt is zero → cannot vote.
        vm.expectRevert(MintGovernor.NoVotingPower.selector);
        vm.prank(attacker);
        governor.castVote(h, false);

        // alice (pre-proposal holder) votes against; attacker's million tokens are powerless.
        vm.prank(alice);
        governor.castVote(h, false);

        vm.warp(block.timestamp + 7 days + 1);
        governor.resolve(h);
        // Quorum base is the snapshot supply (≈100), so alice alone reaches quorum and rejects.
        assertEq(uint8(registry.statusOf(h)), uint8(IRoundRegistry.RoundStatus.Challenged));
        assertEq(token.balanceOf(dave), 0);
    }

    function test_Snapshot_SellingAfterProposalKeepsWeight() public {
        _mintAndDelegate(alice, 200 * E);
        _mintAndDelegate(bob, 100 * E);
        vm.warp(START + 10);
        bytes32 h = _propose(1000 * E, "ipfs://r1");
        vm.warp(block.timestamp + 1);

        // alice dumps her whole balance AFTER the proposal; her snapshot weight is unchanged.
        vm.prank(alice);
        token.transfer(makeAddr("sink"), 200 * E);

        vm.prank(bob);
        governor.challenge(h, "ipfs://reason");
        vm.prank(alice);
        governor.castVote(h, false); // still 200 against (frozen)
        vm.prank(bob);
        governor.castVote(h, true); // 100 for

        vm.warp(block.timestamp + 7 days + 1);
        governor.resolve(h);
        // total snapshot supply 300 → quorum 45; expressed 300 ≥ 45; against 200 > for 100 → reject.
        assertEq(uint8(registry.statusOf(h)), uint8(IRoundRegistry.RoundStatus.Challenged));
    }

    /*//////////////////////////////////////////////////////////////
                  RE-PROPOSITION + CONCURRENT ALTERNATIVES
    //////////////////////////////////////////////////////////////*/

    /// @dev Full cycle: original rejected → alternative proposed → accepted → minted; original cancelled.
    function test_ReProposition_AlternativeAcceptedMintsAndCancelsOriginal() public {
        _mintAndDelegate(whale, 700 * E);
        _mintAndDelegate(alice, 300 * E);
        vm.warp(START + 10);
        bytes32 h = _propose(1000 * E, "ipfs://original");
        vm.warp(block.timestamp + 1);

        // Contest and reject the original (whale + alice both against).
        vm.prank(alice);
        governor.challenge(h, "ipfs://reason");
        vm.prank(whale);
        governor.castVote(h, false);
        vm.warp(block.timestamp + 7 days + 1);
        governor.resolve(h);
        assertEq(uint8(registry.statusOf(h)), uint8(IRoundRegistry.RoundStatus.Challenged), "original rejected");

        // whale (700 ≥ 1% of 1000 = 10) proposes an alternative paying carol instead.
        (address[] memory bens, uint256[] memory amts) = _alloc(carol, 500 * E);
        string memory altUri = "ipfs://alt";
        bytes32 altHash = _hash(bens, amts, altUri);
        vm.prank(whale);
        governor.proposeAlternative(h, bens, amts, altUri);

        // Vote the alternative through at simple majority (whale for).
        vm.prank(whale);
        governor.castVote(altHash, true);
        vm.warp(block.timestamp + 7 days + 1);
        governor.resolve(altHash);

        assertEq(uint8(registry.statusOf(altHash)), uint8(IRoundRegistry.RoundStatus.Executed), "alt minted");
        assertEq(token.balanceOf(carol), 500 * E);
        assertEq(token.balanceOf(dave), 0, "original never minted");
        assertEq(uint8(registry.statusOf(h)), uint8(IRoundRegistry.RoundStatus.Cancelled), "original cancelled");
    }

    /// @dev Concurrent alternatives are voted sequentially by submission order; the first accepted
    ///      wins and all siblings are rejected/cancelled.
    function test_Concurrent_SequentialVotingFirstAcceptedWins() public {
        _mintAndDelegate(whale, 1000 * E);
        vm.warp(START + 10);
        bytes32 h = _propose(1000 * E, "ipfs://original");
        vm.warp(block.timestamp + 1);

        // Reject original.
        vm.prank(whale);
        governor.challenge(h, "ipfs://reason");
        vm.prank(whale);
        governor.castVote(h, false);
        vm.warp(block.timestamp + 7 days + 1);
        governor.resolve(h);

        // Two alternatives submitted in order: alt1 then alt2. alt1 is active, alt2 is queued.
        (address[] memory b1, uint256[] memory a1) = _alloc(carol, 100 * E);
        bytes32 alt1 = _hash(b1, a1, "ipfs://alt1");
        vm.prank(whale);
        governor.proposeAlternative(h, b1, a1, "ipfs://alt1");

        (address[] memory b2, uint256[] memory a2) = _alloc(bob, 200 * E);
        bytes32 alt2 = _hash(b2, a2, "ipfs://alt2");
        vm.prank(whale);
        governor.proposeAlternative(h, b2, a2, "ipfs://alt2");

        // alt2 cannot be voted while alt1 is the active ballot — alt2 is still queued (Pending).
        vm.expectRevert(MintGovernor.BallotNotVoting.selector);
        vm.prank(whale);
        governor.castVote(alt2, true);

        // alt1 is rejected → alt2 becomes active.
        vm.prank(whale);
        governor.castVote(alt1, false);
        vm.warp(block.timestamp + 7 days + 1);
        governor.resolve(alt1);
        assertEq(
            uint8(registry.statusOf(alt1)), uint8(IRoundRegistry.RoundStatus.Challenged), "alt1 rejected, not minted"
        );

        // Now alt2 accepts.
        vm.prank(whale);
        governor.castVote(alt2, true);
        vm.warp(block.timestamp + 7 days + 1);
        governor.resolve(alt2);

        assertEq(token.balanceOf(bob), 200 * E, "alt2 minted");
        assertEq(token.balanceOf(carol), 0, "alt1 never minted");
        assertEq(uint8(registry.statusOf(alt2)), uint8(IRoundRegistry.RoundStatus.Executed));
    }

    function test_ReProposition_BelowThresholdReverts() public {
        _mintAndDelegate(whale, 990 * E);
        _mintAndDelegate(alice, 10 * E); // total 1000 → 1% = 10
        _mintAndDelegate(bob, 5 * E); // 5 < 10 → below threshold (also bumps total to 1005)
        vm.warp(START + 10);
        bytes32 h = _propose(1000 * E, "ipfs://original");
        vm.warp(block.timestamp + 1);

        vm.prank(whale);
        governor.challenge(h, "ipfs://reason");
        vm.prank(whale);
        governor.castVote(h, false);
        vm.warp(block.timestamp + 7 days + 1);
        governor.resolve(h);

        (address[] memory bens, uint256[] memory amts) = _alloc(carol, 100 * E);
        vm.expectRevert(MintGovernor.BelowProposalThreshold.selector);
        vm.prank(bob); // holds 5 tokens, below 1% of circulating
        governor.proposeAlternative(h, bens, amts, "ipfs://alt");
    }

    function test_ReProposition_RevertsBeforeOriginalRejected() public {
        _mintAndDelegate(alice, 100 * E);
        vm.warp(START + 10);
        bytes32 h = _propose(1000 * E, "ipfs://original");
        vm.warp(block.timestamp + 1);
        vm.prank(alice);
        governor.challenge(h, "ipfs://reason");

        // Original still under vote (not decided) → no alternatives yet.
        (address[] memory bens, uint256[] memory amts) = _alloc(carol, 100 * E);
        vm.expectRevert(MintGovernor.OriginalNotRejected.selector);
        vm.prank(alice);
        governor.proposeAlternative(h, bens, amts, "ipfs://alt");
    }

    /*//////////////////////////////////////////////////////////////
                              VOTE GUARDS
    //////////////////////////////////////////////////////////////*/

    function test_Vote_DoubleVoteReverts() public {
        _mintAndDelegate(alice, 100 * E);
        vm.warp(START + 10);
        bytes32 h = _propose(1000 * E, "ipfs://r1");
        vm.warp(block.timestamp + 1);
        vm.prank(alice);
        governor.challenge(h, "ipfs://reason");

        vm.prank(alice);
        governor.castVote(h, true);
        vm.expectRevert(MintGovernor.AlreadyVoted.selector);
        vm.prank(alice);
        governor.castVote(h, false);
    }

    function test_Vote_AfterCloseReverts() public {
        _mintAndDelegate(alice, 100 * E);
        vm.warp(START + 10);
        bytes32 h = _propose(1000 * E, "ipfs://r1");
        vm.warp(block.timestamp + 1);
        vm.prank(alice);
        governor.challenge(h, "ipfs://reason");

        vm.warp(block.timestamp + 7 days + 1);
        vm.expectRevert(MintGovernor.VotingClosed.selector);
        vm.prank(alice);
        governor.castVote(h, true);
    }

    function test_Resolve_BeforeVoteEndReverts() public {
        _mintAndDelegate(alice, 100 * E);
        vm.warp(START + 10);
        bytes32 h = _propose(1000 * E, "ipfs://r1");
        vm.warp(block.timestamp + 1);
        vm.prank(alice);
        governor.challenge(h, "ipfs://reason");

        vm.expectRevert(MintGovernor.VotingNotEnded.selector);
        governor.resolve(h);
    }

    function test_Challenge_RevertsOutsideWindow() public {
        _mintAndDelegate(alice, 100 * E);
        vm.warp(START + 10);
        bytes32 h = _propose(1000 * E, "ipfs://r1"); // proposedAt = START + 10
        vm.warp(START + 10 + uint256(WINDOW_DAYS) * 1 days + 1); // past windowEnd
        vm.expectRevert(MintGovernor.WindowClosed.selector);
        vm.prank(alice);
        governor.challenge(h, "ipfs://reason");
    }

    function test_Challenge_RevertsForNonHolder() public {
        _mintAndDelegate(alice, 100 * E);
        vm.warp(START + 10);
        bytes32 h = _propose(1000 * E, "ipfs://r1");
        vm.warp(block.timestamp + 1);
        vm.expectRevert(MintGovernor.NoVotingPower.selector);
        vm.prank(attacker); // never held tokens at snapshot
        governor.challenge(h, "ipfs://reason");
    }

    function test_Challenge_CannotDisputeTwice() public {
        _mintAndDelegate(alice, 100 * E);
        _mintAndDelegate(bob, 100 * E);
        vm.warp(START + 10);
        bytes32 h = _propose(1000 * E, "ipfs://r1");
        vm.warp(block.timestamp + 1);
        vm.prank(alice);
        governor.challenge(h, "ipfs://reason");
        // After the first challenge the round is `Challenged`, so a second one is not contestable.
        vm.expectRevert(MintGovernor.NotContestable.selector);
        vm.prank(bob);
        governor.challenge(h, "ipfs://reason2");
    }

    function test_Resolve_DoubleResolveReverts() public {
        _mintAndDelegate(alice, 100 * E);
        vm.warp(START + 10);
        bytes32 h = _propose(1000 * E, "ipfs://r1");
        vm.warp(block.timestamp + 1);
        vm.prank(alice);
        governor.challenge(h, "ipfs://reason");
        vm.prank(alice);
        governor.castVote(h, false); // below quorum → validated
        vm.warp(block.timestamp + 7 days + 1);
        governor.resolve(h);
        // Round now Executed; re-resolve must revert (ballot no longer Voting).
        vm.expectRevert(MintGovernor.BallotNotVoting.selector);
        governor.resolve(h);
    }

    /*//////////////////////////////////////////////////////////////
                       KEEPER LEAST-PRIVILEGE
    //////////////////////////////////////////////////////////////*/

    function test_Keeper_CannotExecuteDirectly() public {
        bytes32 h = _propose(1000 * E, "ipfs://r1");
        vm.warp(START + WINDOW_DAYS * 1 days);
        // Keeper holds PROPOSER, not EXECUTOR — it cannot mint by calling the registry directly.
        vm.expectRevert(
            abi.encodeWithSelector(
                IAccessControl.AccessControlUnauthorizedAccount.selector, keeper, registry.ROUND_EXECUTOR_ROLE()
            )
        );
        vm.prank(keeper);
        registry.executeRound(h);
    }

    function test_Keeper_CannotChangeRoles() public {
        // Precompute the role getter (an external call) BEFORE expectRevert so it isn't the call
        // expectRevert latches onto.
        bytes32 execRole = registry.ROUND_EXECUTOR_ROLE();
        // Keeper holds no DEFAULT_ADMIN_ROLE on the registry, so it cannot grant itself EXECUTOR.
        vm.expectRevert(
            abi.encodeWithSelector(IAccessControl.AccessControlUnauthorizedAccount.selector, keeper, bytes32(0))
        );
        vm.prank(keeper);
        registry.grantRole(execRole, keeper);
    }

    function test_Roles_GovernorIsSoleExecutorChallengerCanceller() public view {
        assertTrue(registry.hasRole(registry.ROUND_EXECUTOR_ROLE(), address(governor)));
        assertTrue(registry.hasRole(registry.ROUND_CANCELLER_ROLE(), address(governor)));
        assertTrue(registry.hasRole(registry.ROUND_CHALLENGER_ROLE(), address(governor)));
        assertFalse(registry.hasRole(registry.ROUND_EXECUTOR_ROLE(), keeper));
        assertFalse(registry.hasRole(registry.ROUND_CHALLENGER_ROLE(), keeper));
        assertTrue(registry.hasRole(registry.ROUND_PROPOSER_ROLE(), keeper));
    }

    /*//////////////////////////////////////////////////////////////
                         TREASURY / PARAMS
    //////////////////////////////////////////////////////////////*/

    function test_Treasury_ExcludedFromCirculatingSupply() public {
        vm.prank(admin);
        governor.setTreasury(treasury);

        _mintAndDelegate(treasury, 900 * E); // treasury self-delegates so it is excluded
        _mintAndDelegate(alice, 100 * E);
        // circulating = 1000 − 900 = 100 → quorum ceil(100*15%) = 15. alice (100) against alone
        // reaches quorum and rejects, which would be impossible if treasury counted (quorum 150).
        vm.warp(START + 10);
        bytes32 h = _propose(1000 * E, "ipfs://r1");
        vm.warp(block.timestamp + 1);

        assertEq(governor.circulatingSupplyAt(START + 10), 100 * E);

        vm.prank(alice);
        governor.challenge(h, "ipfs://reason");
        vm.prank(alice);
        governor.castVote(h, false);
        vm.warp(block.timestamp + 7 days + 1);
        governor.resolve(h);
        assertEq(
            uint8(registry.statusOf(h)), uint8(IRoundRegistry.RoundStatus.Challenged), "rejected on circ-only quorum"
        );
    }

    function test_Params_OnlyAdminCanSet() public {
        vm.expectRevert(
            abi.encodeWithSelector(IAccessControl.AccessControlUnauthorizedAccount.selector, attacker, bytes32(0))
        );
        vm.prank(attacker);
        governor.setQuorumBps(2000);

        vm.prank(admin);
        governor.setQuorumBps(2000);
        assertEq(governor.quorumBps(), 2000);
    }

    function test_Constructor_RevertsOnBadParams() public {
        vm.expectRevert(MintGovernor.InvalidParam.selector);
        new MintGovernor(admin, registry, IVotes(address(token)), address(0), 0, 100, 7); // quorum 0
        vm.expectRevert(MintGovernor.InvalidParam.selector);
        new MintGovernor(admin, registry, IVotes(address(token)), address(0), 1500, 100, 0); // 0 vote days
        vm.expectRevert(MintGovernor.ZeroAddress.selector);
        new MintGovernor(address(0), registry, IVotes(address(token)), address(0), 1500, 100, 7);
    }
}
