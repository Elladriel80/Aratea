// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

import {Test} from "forge-std/Test.sol";
import {StdInvariant} from "forge-std/StdInvariant.sol";

import {AugPocToken} from "../../src/token/AugPocToken.sol";
import {RoundRegistry} from "../../src/rounds/RoundRegistry.sol";
import {MintGovernor} from "../../src/governance/MintGovernor.sol";
import {IAugPocToken} from "../../src/interfaces/IAugPocToken.sol";
import {IRoundRegistry} from "../../src/interfaces/IRoundRegistry.sol";
import {IVotes} from "@openzeppelin/contracts/governance/utils/IVotes.sol";

/// @title  MintGovernorHandler — bounded harness driving the Governor + registry through the
///         nominal and contested-original paths, tracking how much was legitimately minted.
contract MintGovernorHandler is Test {
    AugPocToken public immutable token;
    RoundRegistry public immutable registry;
    MintGovernor public immutable governor;
    address public immutable keeper;
    address internal immutable sink; // round beneficiary (kept out of the voter set)

    address[3] public voters;

    bytes32[] public rounds;
    mapping(bytes32 => uint256) public amountOf;
    mapping(bytes32 => bool) public seen;
    mapping(bytes32 => bool) public counted;
    bytes32[] public disputes; // challenged originals

    uint256 public ghost_executed; // sum of amounts of rounds that reached Executed
    uint256 internal nonce;

    constructor(
        AugPocToken _token,
        RoundRegistry _registry,
        MintGovernor _governor,
        address _keeper,
        address _minter,
        address[3] memory _voters,
        uint256[3] memory _weights,
        address _sink
    ) {
        token = _token;
        registry = _registry;
        governor = _governor;
        keeper = _keeper;
        voters = _voters;
        sink = _sink;

        // Seed + self-delegate voters once, before any proposal: their snapshot weight is fixed.
        for (uint256 i = 0; i < 3; i++) {
            vm.prank(_minter);
            token.mint(_voters[i], _weights[i]);
            vm.prank(_voters[i]);
            token.delegate(_voters[i]);
        }
    }

    function _sync() internal {
        uint256 len = rounds.length;
        for (uint256 i = 0; i < len; i++) {
            bytes32 h = rounds[i];
            if (!counted[h] && registry.statusOf(h) == IRoundRegistry.RoundStatus.Executed) {
                counted[h] = true;
                ghost_executed += amountOf[h];
            }
        }
    }

    function propose(
        uint96 amount
    ) public {
        uint256 amt = bound(uint256(amount), 1, 100_000 ether);
        nonce += 1;
        address[] memory bens = new address[](1);
        bens[0] = sink;
        uint256[] memory amts = new uint256[](1);
        amts[0] = amt;
        string memory uri = string(abi.encodePacked("ipfs://inv-", vm.toString(nonce)));
        bytes32 h = keccak256(abi.encode(bens, amts, uri));
        if (seen[h]) return;
        vm.prank(keeper);
        try registry.proposeRound(h, bens, amts, uri, 7 days) {
            seen[h] = true;
            rounds.push(h);
            amountOf[h] = amt;
        } catch {}
    }

    function finalize(
        uint256 idx
    ) public {
        if (rounds.length == 0) return;
        bytes32 h = rounds[idx % rounds.length];
        try governor.finalize(h) {} catch {}
        _sync();
    }

    function challenge(
        uint256 idx,
        uint256 vseed
    ) public {
        if (rounds.length == 0) return;
        bytes32 h = rounds[idx % rounds.length];
        address voter = voters[vseed % 3];
        vm.prank(voter); // challenger must be a token holder at the snapshot
        try governor.challenge(h, "ipfs://x") {
            disputes.push(h);
        } catch {}
    }

    function vote(
        uint256 idx,
        uint256 vseed,
        bool support
    ) public {
        if (disputes.length == 0) return;
        bytes32 h = disputes[idx % disputes.length];
        address voter = voters[vseed % 3];
        vm.prank(voter);
        try governor.castVote(h, support) {} catch {}
    }

    function resolve(
        uint256 idx
    ) public {
        if (disputes.length == 0) return;
        bytes32 h = disputes[idx % disputes.length];
        try governor.resolve(h) {} catch {}
        _sync();
    }

    function advanceTime(
        uint64 secs
    ) public {
        skip(bound(uint256(secs), 1, 10 days));
    }
}

/// @title  MintGovernorInvariantTest — global safety properties of the Phase 2 mint governance.
contract MintGovernorInvariantTest is StdInvariant, Test {
    AugPocToken internal token;
    RoundRegistry internal registry;
    MintGovernor internal governor;
    MintGovernorHandler internal handler;

    address internal admin = makeAddr("inv-admin");
    address internal keeper = makeAddr("inv-keeper");
    address internal minter = makeAddr("inv-minter");
    address internal sink = makeAddr("inv-sink");

    uint256 internal constant SEED_TOTAL = 1000 ether;

    function setUp() public {
        token = new AugPocToken(admin);
        registry = new RoundRegistry(admin, IAugPocToken(address(token)));
        governor = new MintGovernor(admin, registry, IVotes(address(token)), address(0), 1500, 100, 7);

        vm.startPrank(admin);
        token.grantRole(token.MINTER_ROLE(), address(registry));
        token.grantRole(token.MINTER_ROLE(), minter);
        registry.grantRole(registry.ROUND_PROPOSER_ROLE(), keeper);
        registry.grantRole(registry.ROUND_PROPOSER_ROLE(), address(governor));
        registry.grantRole(registry.ROUND_EXECUTOR_ROLE(), address(governor));
        registry.grantRole(registry.ROUND_CANCELLER_ROLE(), address(governor));
        registry.grantRole(registry.ROUND_CHALLENGER_ROLE(), address(governor));
        vm.stopPrank();

        vm.warp(1_778_544_000);

        address[3] memory voters = [makeAddr("v0"), makeAddr("v1"), makeAddr("v2")];
        uint256[3] memory weights = [uint256(500 ether), 300 ether, 200 ether]; // sum = SEED_TOTAL
        handler = new MintGovernorHandler(token, registry, governor, keeper, minter, voters, weights, sink);

        vm.warp(block.timestamp + 1); // snapshots strictly after seeding

        targetContract(address(handler));
        bytes4[] memory selectors = new bytes4[](6);
        selectors[0] = MintGovernorHandler.propose.selector;
        selectors[1] = MintGovernorHandler.finalize.selector;
        selectors[2] = MintGovernorHandler.challenge.selector;
        selectors[3] = MintGovernorHandler.vote.selector;
        selectors[4] = MintGovernorHandler.resolve.selector;
        selectors[5] = MintGovernorHandler.advanceTime.selector;
        targetSelector(FuzzSelector({addr: address(handler), selectors: selectors}));
    }

    /// @dev No mint bypasses the rules: total supply is exactly the seed plus the amounts of the
    ///      rounds that actually reached Executed (which only happens via finalize on an
    ///      uncontested round or resolve on an upheld/accepted vote).
    function invariant_SupplyEqualsSeedPlusExecuted() public view {
        assertEq(token.totalSupply(), SEED_TOTAL + handler.ghost_executed());
    }

    /// @dev The Governor must never hold role-admin on either contract (it cannot rewire roles).
    function invariant_GovernorNeverHoldsAdmin() public view {
        assertFalse(registry.hasRole(0x00, address(governor)));
        assertFalse(token.hasRole(0x00, address(governor)));
    }

    /// @dev Keeper least-privilege: proposer only, never executor/canceller/challenger/admin.
    function invariant_KeeperLeastPrivilege() public view {
        assertTrue(registry.hasRole(registry.ROUND_PROPOSER_ROLE(), keeper));
        assertFalse(registry.hasRole(registry.ROUND_EXECUTOR_ROLE(), keeper));
        assertFalse(registry.hasRole(registry.ROUND_CANCELLER_ROLE(), keeper));
        assertFalse(registry.hasRole(registry.ROUND_CHALLENGER_ROLE(), keeper));
        assertFalse(registry.hasRole(0x00, keeper));
    }
}
