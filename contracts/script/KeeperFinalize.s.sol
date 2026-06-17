// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

import {Script, console2} from "forge-std/Script.sol";

import {MintGovernor} from "../src/governance/MintGovernor.sol";
import {IRoundRegistry} from "../src/interfaces/IRoundRegistry.sol";
import {RoundRegistry} from "../src/rounds/RoundRegistry.sol";

/// @title  KeeperFinalize — permissionless finalization of an uncontested round
/// @notice After the challenge window, calls `MintGovernor.finalize(roundHash)` which executes the
///         round (mint) IFF it is still `Proposed` (uncontested). A challenged round reverts here
///         and is instead resolved through the vote. `finalize` is permissionless, so this can be
///         run by the keeper hot key or anyone; broadcasting with the keeper key is the default.
///
/// @dev    Required env:
///           - GOVERNOR_ADDRESS : deployed MintGovernor
///           - REGISTRY_ADDRESS : deployed RoundRegistry (for a read-only pre-check)
///           - ROUND_HASH       : the round to finalize (bytes32)
contract KeeperFinalize is Script {
    function run() external {
        MintGovernor governor = MintGovernor(vm.envAddress("GOVERNOR_ADDRESS"));
        RoundRegistry registry = RoundRegistry(vm.envAddress("REGISTRY_ADDRESS"));
        bytes32 roundHash = vm.envBytes32("ROUND_HASH");

        IRoundRegistry.RoundStatus status = registry.statusOf(roundHash);
        console2.log("== KeeperFinalize ==");
        console2.logBytes32(roundHash);
        console2.log("Status (0 None,1 Proposed,2 Challenged,3 Executed,4 Cancelled):", uint8(status));

        if (status != IRoundRegistry.RoundStatus.Proposed) {
            // Not finalizable here: either already executed/cancelled, or challenged (vote pending).
            console2.log("Not in Proposed state - skipping finalize (no-op).");
            return;
        }

        vm.startBroadcast(); // signer from CLI (keeper hot key, or anyone)
        governor.finalize(roundHash);
        vm.stopBroadcast();

        console2.log("Finalized: round executed (mint done) if the window had passed.");
    }
}
