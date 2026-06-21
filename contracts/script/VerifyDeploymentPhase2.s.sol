// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

import {Script, console2} from "forge-std/Script.sol";

import {AugPocToken} from "../src/token/AugPocToken.sol";
import {RoundRegistry} from "../src/rounds/RoundRegistry.sol";
import {MintGovernor} from "../src/governance/MintGovernor.sol";

/// @title  VerifyDeploymentPhase2 — read-only post-deploy sanity check for Phase 2 wiring
/// @notice Re-asserts every role-wiring property that DeployPhase2Governor set up. Run after
///         the Ledger broadcast to confirm the on-chain state matches the intended topology
///         (covers REG-1 from SECURITY-AUDIT-2026-06-21.md).
///
/// @dev    Required environment variables:
///           - TOKEN_ADDRESS    : deployed AugPocToken
///           - REGISTRY_ADDRESS : deployed RoundRegistry
///           - GOVERNOR_ADDRESS : deployed MintGovernor (Phase 2)
///           - ADMIN_ADDRESS    : the EOA / Safe that holds DEFAULT_ADMIN_ROLE
///           - KEEPER_ADDRESS   : the hot-key proposer
///
///         No private key required — pure read. Run with:
///           forge script script/VerifyDeploymentPhase2.s.sol:VerifyDeploymentPhase2 \
///             --rpc-url $RPC_ARBITRUM_SEPOLIA -vv
contract VerifyDeploymentPhase2 is Script {
    function run() external view {
        AugPocToken token = AugPocToken(vm.envAddress("TOKEN_ADDRESS"));
        RoundRegistry registry = RoundRegistry(vm.envAddress("REGISTRY_ADDRESS"));
        MintGovernor governor = MintGovernor(vm.envAddress("GOVERNOR_ADDRESS"));
        address admin = vm.envAddress("ADMIN_ADDRESS");
        address keeper = vm.envAddress("KEEPER_ADDRESS");

        console2.log("== VerifyDeploymentPhase2 ==");
        console2.log("Token:    ", address(token));
        console2.log("Registry: ", address(registry));
        console2.log("Governor: ", address(governor));
        console2.log("Admin:    ", admin);
        console2.log("Keeper:   ", keeper);

        // --- Token: unchanged from Phase 1 ---
        require(token.hasRole(token.DEFAULT_ADMIN_ROLE(), admin), "token: admin missing DEFAULT_ADMIN_ROLE");
        require(token.hasRole(token.MINTER_ROLE(), address(registry)), "token: registry missing MINTER_ROLE");
        require(!token.hasRole(token.MINTER_ROLE(), admin), "token: admin must NOT hold MINTER_ROLE");
        require(!token.hasRole(token.MINTER_ROLE(), address(governor)), "token: governor must NOT mint directly");
        require(!token.paused(), "token: must be unpaused");

        // --- Registry: Phase 2 topology ---

        // Governor holds the 4 operational roles.
        require(registry.hasRole(registry.ROUND_PROPOSER_ROLE(), address(governor)), "registry: gov missing PROPOSER");
        require(registry.hasRole(registry.ROUND_EXECUTOR_ROLE(), address(governor)), "registry: gov missing EXECUTOR");
        require(registry.hasRole(registry.ROUND_CANCELLER_ROLE(), address(governor)), "registry: gov missing CANCELLER");
        require(registry.hasRole(registry.ROUND_CHALLENGER_ROLE(), address(governor)), "registry: gov missing CHALLENGER");
        require(!registry.hasRole(registry.DEFAULT_ADMIN_ROLE(), address(governor)), "registry: gov must NOT be admin");

        // Keeper: proposer ONLY (REG-1 scope enforcement).
        require(registry.hasRole(registry.ROUND_PROPOSER_ROLE(), keeper), "registry: keeper missing PROPOSER");
        require(!registry.hasRole(registry.ROUND_EXECUTOR_ROLE(), keeper), "registry: keeper must NOT execute");
        require(!registry.hasRole(registry.ROUND_CANCELLER_ROLE(), keeper), "registry: keeper must NOT cancel");
        require(!registry.hasRole(registry.ROUND_CHALLENGER_ROLE(), keeper), "registry: keeper must NOT challenge");
        require(!registry.hasRole(registry.DEFAULT_ADMIN_ROLE(), keeper), "registry: keeper must NOT be admin");

        // Admin: DEFAULT_ADMIN + CANCELLER only — direct mint path REVOKED (REG-1).
        require(registry.hasRole(registry.DEFAULT_ADMIN_ROLE(), admin), "registry: admin missing DEFAULT_ADMIN");
        require(registry.hasRole(registry.ROUND_CANCELLER_ROLE(), admin), "registry: admin missing CANCELLER (circuit-breaker)");
        require(!registry.hasRole(registry.ROUND_EXECUTOR_ROLE(), admin), "REG-1 VIOLATED: admin must NOT hold EXECUTOR after Phase 2");
        require(!registry.hasRole(registry.ROUND_PROPOSER_ROLE(), admin), "registry: admin must NOT hold PROPOSER after Phase 2");
        require(!registry.hasRole(registry.ROUND_CHALLENGER_ROLE(), admin), "registry: admin must NOT hold CHALLENGER");

        // --- Governor wiring ---
        require(address(governor.registry()) == address(registry), "governor: registry mismatch");
        require(address(governor.token()) == address(token), "governor: token mismatch");

        console2.log("== All Phase 2 assertions passed ==");
        console2.log("   REG-1 CONFIRMED: admin does NOT hold ROUND_EXECUTOR_ROLE");
    }
}
