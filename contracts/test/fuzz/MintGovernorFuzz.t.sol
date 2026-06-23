// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

import {Test} from "forge-std/Test.sol";
import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";

import {AugPocToken} from "../../src/token/AugPocToken.sol";
import {RoundRegistry} from "../../src/rounds/RoundRegistry.sol";
import {MintGovernor} from "../../src/governance/MintGovernor.sol";
import {IAugPocToken} from "../../src/interfaces/IAugPocToken.sol";
import {IRoundRegistry} from "../../src/interfaces/IRoundRegistry.sol";
import {IVotes} from "@openzeppelin/contracts/governance/utils/IVotes.sol";

/// @title  MintGovernor fuzz tests
/// @notice Fuzzes the exact quorum + majority arithmetic against random vote weights, and the
///         snapshot anti-vote-buying property, by driving the real contestation flow each run.
contract MintGovernorFuzzTest is Test {
    AugPocToken internal token;
    RoundRegistry internal registry;
    MintGovernor internal governor;

    address internal admin = makeAddr("admin");
    address internal keeper = makeAddr("keeper");
    address internal minter = makeAddr("minter");

    address internal voterFor = makeAddr("voterFor"); // also the challenger
    address internal voterAgainst = makeAddr("voterAgainst");
    address internal abstainer = makeAddr("abstainer");
    address internal dave = makeAddr("dave");

    uint256 internal constant START = 1_778_544_000;
    uint16 internal constant QUORUM_BPS = 1500;
    uint32 internal constant VOTE_DAYS = 7;           // vote duration for MintGovernor (days)
    uint32 internal constant ROUND_WINDOW_SEC = 7 days; // challenge window for registry (seconds)

    function setUp() public {
        token = new AugPocToken(admin);
        registry = new RoundRegistry(admin, IAugPocToken(address(token)));
        governor = new MintGovernor(admin, registry, IVotes(address(token)), address(0), QUORUM_BPS, 100, VOTE_DAYS);

        vm.startPrank(admin);
        token.grantRole(token.MINTER_ROLE(), address(registry));
        token.grantRole(token.MINTER_ROLE(), minter);
        registry.grantRole(registry.ROUND_PROPOSER_ROLE(), keeper);
        registry.grantRole(registry.ROUND_PROPOSER_ROLE(), address(governor));
        registry.grantRole(registry.ROUND_EXECUTOR_ROLE(), address(governor));
        registry.grantRole(registry.ROUND_CANCELLER_ROLE(), address(governor));
        registry.grantRole(registry.ROUND_CHALLENGER_ROLE(), address(governor));
        vm.stopPrank();

        vm.warp(START);
    }

    function _seed(
        address who,
        uint256 amount
    ) internal {
        if (amount == 0) return;
        vm.prank(minter);
        token.mint(who, amount);
        vm.prank(who);
        token.delegate(who);
    }

    /// @dev The original is rejected IFF quorum is reached AND against > for. Fuzz the three
    ///      weights and assert the on-chain outcome matches the exact predicate.
    /// forge-config: default.fuzz.runs = 400
    function testFuzz_VoteOutcomeMatchesRule(
        uint96 forW,
        uint96 againstW,
        uint96 abstainW
    ) public {
        // voterFor is also the challenger, so it must hold weight.
        uint256 fW = bound(uint256(forW), 1, 1_000_000 ether);
        uint256 aW = bound(uint256(againstW), 0, 1_000_000 ether);
        uint256 abW = bound(uint256(abstainW), 0, 1_000_000 ether);

        _seed(voterFor, fW);
        _seed(voterAgainst, aW);
        _seed(abstainer, abW);

        vm.warp(START + 10);
        uint256 amount = 1234 ether;
        address[] memory bens = new address[](1);
        bens[0] = dave;
        uint256[] memory amts = new uint256[](1);
        amts[0] = amount;
        string memory uri = "ipfs://fuzz";
        bytes32 h = keccak256(abi.encode(bens, amts, uri));
        vm.prank(keeper);
        registry.proposeRound(h, bens, amts, uri, ROUND_WINDOW_SEC);

        vm.warp(block.timestamp + 1);
        vm.prank(voterFor);
        governor.challenge(h, "ipfs://reason");

        vm.prank(voterFor);
        governor.castVote(h, true);
        if (aW > 0) {
            vm.prank(voterAgainst);
            governor.castVote(h, false);
        }

        vm.warp(block.timestamp + ROUND_WINDOW_SEC + 1);
        governor.resolve(h);

        uint256 total = fW + aW + abW;
        uint256 quorum = Math.ceilDiv(total * QUORUM_BPS, 10_000);
        bool quorumReached = (fW + aW) >= quorum;
        bool rejected = quorumReached && (aW > fW);

        if (rejected) {
            assertEq(uint8(registry.statusOf(h)), uint8(IRoundRegistry.RoundStatus.Challenged), "should be rejected");
            assertEq(token.balanceOf(dave), 0, "rejected: no mint");
        } else {
            assertEq(uint8(registry.statusOf(h)), uint8(IRoundRegistry.RoundStatus.Executed), "should be upheld");
            assertEq(token.balanceOf(dave), amount, "upheld: minted");
        }
    }

    /// @dev Weight acquired AFTER the proposal never counts: an attacker minted post-snapshot
    ///      cannot vote, regardless of how much they hold.
    /// forge-config: default.fuzz.runs = 200
    function testFuzz_PostProposalWeightIsPowerless(
        uint96 attackerW
    ) public {
        uint256 atW = bound(uint256(attackerW), 1, 10_000_000 ether);
        _seed(voterFor, 100 ether);

        vm.warp(START + 10);
        uint256 amount = 500 ether;
        address[] memory bens = new address[](1);
        bens[0] = dave;
        uint256[] memory amts = new uint256[](1);
        amts[0] = amount;
        string memory uri = "ipfs://fuzz2";
        bytes32 h = keccak256(abi.encode(bens, amts, uri));
        vm.prank(keeper);
        registry.proposeRound(h, bens, amts, uri, ROUND_WINDOW_SEC);

        // Attacker acquires weight strictly after the proposal.
        vm.warp(block.timestamp + 1);
        _seed(makeAddr("attacker"), atW);

        vm.prank(voterFor);
        governor.challenge(h, "ipfs://reason");

        address attacker = makeAddr("attacker");
        vm.expectRevert(MintGovernor.NoVotingPower.selector);
        vm.prank(attacker);
        governor.castVote(h, false);
    }
}
