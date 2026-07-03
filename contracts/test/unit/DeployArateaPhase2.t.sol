// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

import {Test} from "forge-std/Test.sol";

import {DeployArateaPhase1} from "../../script/DeployArateaPhase1.s.sol";
import {DeployPhase2Governor} from "../../script/DeployPhase2Governor.s.sol";
import {AugPocToken} from "../../src/token/AugPocToken.sol";
import {RoundRegistry} from "../../src/rounds/RoundRegistry.sol";
import {MintGovernor} from "../../src/governance/MintGovernor.sol";

/// @title  DeployArateaPhase2Test — integration test for the Phase 2 deployment script
/// @notice Runs Phase 1 + Phase 2 against a fresh in-memory chain and asserts that every
///         role-wiring property holds. Specifically covers REG-1 from the security audit
///         (SECURITY-AUDIT-2026-06-21.md): the admin must NOT hold ROUND_EXECUTOR_ROLE after
///         the Phase 2 rewiring so that no round can be executed bypassing the vote.
contract DeployArateaPhase2Test is Test {
    address internal constant ANVIL_ADMIN = 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266;
    address internal constant ANVIL_KEEPER = 0x70997970C51812dc3A010C7d01b50e0d17dc79C8;

    AugPocToken internal token;
    RoundRegistry internal registry;
    MintGovernor internal governor;

    function setUp() public {
        // Phase 1: deploy token + registry.
        vm.setEnv("ADMIN_ADDRESS", "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266");
        DeployArateaPhase1 deploy1 = new DeployArateaPhase1();
        DeployArateaPhase1.DeploymentResult memory r = deploy1.run();
        token = r.token;
        registry = r.registry;

        // Phase 2: deploy MintGovernor and rewire roles.
        vm.setEnv("TOKEN_ADDRESS", vm.toString(address(token)));
        vm.setEnv("REGISTRY_ADDRESS", vm.toString(address(registry)));
        vm.setEnv("KEEPER_ADDRESS", "0x70997970C51812dc3A010C7d01b50e0d17dc79C8");
        DeployPhase2Governor deploy2 = new DeployPhase2Governor();
        governor = deploy2.run();
    }

    /// @notice REG-1 (Medium): after Phase 2 rewiring the admin EOA must NOT hold
    ///         ROUND_EXECUTOR_ROLE — only the Governor may execute rounds.
    function test_Phase2_AdminLosesExecutorRole() public view {
        assertFalse(
            registry.hasRole(registry.ROUND_EXECUTOR_ROLE(), ANVIL_ADMIN),
            "REG-1: admin must NOT hold ROUND_EXECUTOR_ROLE after Phase 2 rewiring"
        );
    }

    function test_Phase2_AdminLosesProposerRole() public view {
        assertFalse(
            registry.hasRole(registry.ROUND_PROPOSER_ROLE(), ANVIL_ADMIN),
            "admin must NOT hold ROUND_PROPOSER_ROLE after Phase 2 (keeper/governor do)"
        );
    }

    function test_Phase2_GovernorHoldsOperationalRoles() public view {
        assertTrue(registry.hasRole(registry.ROUND_EXECUTOR_ROLE(), address(governor)), "gov must be executor");
        assertTrue(registry.hasRole(registry.ROUND_PROPOSER_ROLE(), address(governor)), "gov must be proposer");
        assertTrue(registry.hasRole(registry.ROUND_CANCELLER_ROLE(), address(governor)), "gov must be canceller");
        assertTrue(registry.hasRole(registry.ROUND_CHALLENGER_ROLE(), address(governor)), "gov must be challenger");
    }

    function test_Phase2_GovernorIsNotAdmin() public view {
        assertFalse(
            registry.hasRole(registry.DEFAULT_ADMIN_ROLE(), address(governor)), "governor must NOT be registry admin"
        );
    }

    function test_Phase2_KeeperIsProposerOnly() public view {
        assertTrue(registry.hasRole(registry.ROUND_PROPOSER_ROLE(), ANVIL_KEEPER), "keeper must be proposer");
        assertFalse(registry.hasRole(registry.ROUND_EXECUTOR_ROLE(), ANVIL_KEEPER), "keeper must NOT execute");
        assertFalse(registry.hasRole(registry.ROUND_CANCELLER_ROLE(), ANVIL_KEEPER), "keeper must NOT cancel");
        assertFalse(registry.hasRole(registry.ROUND_CHALLENGER_ROLE(), ANVIL_KEEPER), "keeper must NOT challenge");
        assertFalse(registry.hasRole(registry.DEFAULT_ADMIN_ROLE(), ANVIL_KEEPER), "keeper must NOT be admin");
    }

    function test_Phase2_AdminKeepsCircuitBreaker() public view {
        assertTrue(registry.hasRole(registry.DEFAULT_ADMIN_ROLE(), ANVIL_ADMIN), "admin keeps default-admin");
        assertTrue(
            registry.hasRole(registry.ROUND_CANCELLER_ROLE(), ANVIL_ADMIN), "admin keeps canceller (circuit-breaker)"
        );
    }

    function test_Phase2_RegistryRemainesSoleMinter() public view {
        assertTrue(token.hasRole(token.MINTER_ROLE(), address(registry)), "registry must be minter");
        assertFalse(token.hasRole(token.MINTER_ROLE(), address(governor)), "governor must NOT mint directly");
    }

    function test_Phase2_GovernorWiredToCorrectContracts() public view {
        assertEq(address(governor.registry()), address(registry), "governor registry mismatch");
        assertEq(address(governor.token()), address(token), "governor token mismatch");
    }
}
