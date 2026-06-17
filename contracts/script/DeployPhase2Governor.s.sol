// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

import {Script, console2} from "forge-std/Script.sol";

import {AugPocToken} from "../src/token/AugPocToken.sol";
import {RoundRegistry} from "../src/rounds/RoundRegistry.sol";
import {MintGovernor} from "../src/governance/MintGovernor.sol";
import {IVotes} from "@openzeppelin/contracts/governance/utils/IVotes.sol";

/// @title  DeployPhase2Governor — deploys the MintGovernor and wires Phase 2 roles
/// @notice Adds the automatic-mint + token-weighted-contestation layer ON TOP of an already
///         deployed Phase 1 (AugPocToken + RoundRegistry). Deploys `MintGovernor`, then rewires
///         the registry roles to the least-privilege Phase 2 topology.
///
/// @dev    Run by the ADMIN (the registry's DEFAULT_ADMIN_ROLE holder) — role grants/revokes
///         require it. The signer is provided by Foundry CLI flags (--ledger / --private-key),
///         exactly like DeployArateaPhase1. The admin (cold) key is distinct and stays OUT of CI;
///         only the keeper (hot) key — proposer/finalizer — ever lives in CI.
///
///         Required env:
///           - ADMIN_ADDRESS    : registry DEFAULT_ADMIN_ROLE holder + broadcaster
///           - TOKEN_ADDRESS    : deployed AugPocToken
///           - REGISTRY_ADDRESS : deployed RoundRegistry
///           - KEEPER_ADDRESS   : the automated proposer/finalizer (hot key in CI)
///         Optional env (defaults in parentheses):
///           - GOVERNOR_TREASURY               (0x0 = no treasury subtraction)
///           - GOVERNOR_QUORUM_BPS             (1500 = 15%)
///           - GOVERNOR_PROPOSAL_THRESHOLD_BPS (100 = 1%)
///           - GOVERNOR_VOTE_DURATION_DAYS     (7)
///
///         Resulting role topology (registry):
///           DEFAULT_ADMIN_ROLE   → ADMIN            (unchanged; cold key, can re-wire)
///           ROUND_PROPOSER_ROLE  → KEEPER + GOVERNOR (keeper proposes monthly; governor proposes
///                                                     re-proposition alternatives)
///           ROUND_EXECUTOR_ROLE  → GOVERNOR ONLY    (admin's executor REVOKED — no human/keeper
///                                                     mint path that could bypass the vote)
///           ROUND_CANCELLER_ROLE → ADMIN + GOVERNOR (admin = emergency circuit-breaker; governor
///                                                     cancels superseded alternatives)
///           ROUND_CHALLENGER_ROLE→ GOVERNOR ONLY    (the single challenge front-door)
///         Token MINTER_ROLE stays with the registry (unchanged from Phase 1).
contract DeployPhase2Governor is Script {
    function run() external returns (MintGovernor governor) {
        address admin = vm.envAddress("ADMIN_ADDRESS");
        address tokenAddr = vm.envAddress("TOKEN_ADDRESS");
        address registryAddr = vm.envAddress("REGISTRY_ADDRESS");
        address keeper = vm.envAddress("KEEPER_ADDRESS");
        require(admin != address(0), "ADMIN_ADDRESS zero");
        require(keeper != address(0), "KEEPER_ADDRESS zero");

        address treasury = vm.envOr("GOVERNOR_TREASURY", address(0));
        uint16 quorumBps = uint16(vm.envOr("GOVERNOR_QUORUM_BPS", uint256(1500)));
        uint16 thresholdBps = uint16(vm.envOr("GOVERNOR_PROPOSAL_THRESHOLD_BPS", uint256(100)));
        uint32 voteDays = uint32(vm.envOr("GOVERNOR_VOTE_DURATION_DAYS", uint256(7)));

        RoundRegistry registry = RoundRegistry(registryAddr);
        AugPocToken token = AugPocToken(tokenAddr);

        console2.log("== DeployPhase2Governor ==");
        console2.log("Admin:   ", admin);
        console2.log("Token:   ", tokenAddr);
        console2.log("Registry:", registryAddr);
        console2.log("Keeper:  ", keeper);

        vm.startBroadcast(admin);

        governor = new MintGovernor(admin, registry, IVotes(tokenAddr), treasury, quorumBps, thresholdBps, voteDays);
        console2.log("MintGovernor deployed at:", address(governor));

        // --- Wire least-privilege roles (admin holds DEFAULT_ADMIN_ROLE, so these succeed) ---
        registry.grantRole(registry.ROUND_PROPOSER_ROLE(), keeper);
        registry.grantRole(registry.ROUND_PROPOSER_ROLE(), address(governor));
        registry.grantRole(registry.ROUND_EXECUTOR_ROLE(), address(governor));
        registry.grantRole(registry.ROUND_CANCELLER_ROLE(), address(governor));
        registry.grantRole(registry.ROUND_CHALLENGER_ROLE(), address(governor));

        // Remove the admin's direct mint path: from Phase 1 the admin held EXECUTOR (and PROPOSER).
        // In Phase 2 only the Governor may execute (so no round can be minted bypassing the vote),
        // and proposing is the keeper's job. The admin keeps CANCELLER (circuit-breaker) + admin.
        if (registry.hasRole(registry.ROUND_EXECUTOR_ROLE(), admin)) {
            registry.revokeRole(registry.ROUND_EXECUTOR_ROLE(), admin);
        }
        if (registry.hasRole(registry.ROUND_PROPOSER_ROLE(), admin)) {
            registry.revokeRole(registry.ROUND_PROPOSER_ROLE(), admin);
        }

        vm.stopBroadcast();

        _assertWiring(token, registry, governor, admin, keeper);

        console2.log("== Phase 2 wiring complete ==");
        return governor;
    }

    function _assertWiring(
        AugPocToken token,
        RoundRegistry registry,
        MintGovernor governor,
        address admin,
        address keeper
    ) private view {
        // Governor holds exactly the four operational roles, never role-admin.
        require(registry.hasRole(registry.ROUND_PROPOSER_ROLE(), address(governor)), "gov !proposer");
        require(registry.hasRole(registry.ROUND_EXECUTOR_ROLE(), address(governor)), "gov !executor");
        require(registry.hasRole(registry.ROUND_CANCELLER_ROLE(), address(governor)), "gov !canceller");
        require(registry.hasRole(registry.ROUND_CHALLENGER_ROLE(), address(governor)), "gov !challenger");
        require(!registry.hasRole(registry.DEFAULT_ADMIN_ROLE(), address(governor)), "gov must NOT be admin");

        // Keeper: proposer only — never executor/canceller/challenger/admin.
        require(registry.hasRole(registry.ROUND_PROPOSER_ROLE(), keeper), "keeper !proposer");
        require(!registry.hasRole(registry.ROUND_EXECUTOR_ROLE(), keeper), "keeper must NOT execute");
        require(!registry.hasRole(registry.ROUND_CANCELLER_ROLE(), keeper), "keeper must NOT cancel");
        require(!registry.hasRole(registry.ROUND_CHALLENGER_ROLE(), keeper), "keeper must NOT challenge");
        require(!registry.hasRole(registry.DEFAULT_ADMIN_ROLE(), keeper), "keeper must NOT be admin");

        // Admin: keeps DEFAULT_ADMIN + CANCELLER, loses the direct EXECUTOR mint path.
        require(registry.hasRole(registry.DEFAULT_ADMIN_ROLE(), admin), "admin !default-admin");
        require(registry.hasRole(registry.ROUND_CANCELLER_ROLE(), admin), "admin !canceller");
        require(!registry.hasRole(registry.ROUND_EXECUTOR_ROLE(), admin), "admin must NOT execute");

        // Token: registry remains the sole minter; governor must NOT mint directly.
        require(token.hasRole(token.MINTER_ROLE(), address(registry)), "registry !minter");
        require(!token.hasRole(token.MINTER_ROLE(), address(governor)), "gov must NOT mint");
        require(address(governor.registry()) == address(registry), "gov registry mismatch");
        require(address(governor.token()) == address(token), "gov token mismatch");
    }
}
