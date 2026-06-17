// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

import {Script, console2} from "forge-std/Script.sol";

import {RoundRegistry} from "../src/rounds/RoundRegistry.sol";

/// @title  KeeperProposeRound — the keeper proposes the monthly mint round (J0)
/// @notice Off-chain the valuation agent computes the allocation and pins the report to IPFS;
///         this script commits it on-chain via `RoundRegistry.proposeRound`, starting the
///         challenge window. The signer is the KEEPER (hot key, ROUND_PROPOSER_ROLE only),
///         provided through Foundry CLI flags (`--private-key $KEEPER_PRIVATE_KEY` in CI, or a
///         keystore/ledger locally).
///
/// @dev    Required env:
///           - REGISTRY_ADDRESS      : deployed RoundRegistry
///           - ROUND_BENEFICIARIES   : comma-separated addresses
///           - ROUND_AMOUNTS         : comma-separated uint256 amounts (wei; 1 sat = 1e18)
///           - ROUND_IPFS            : ipfs URI of the valuation report
///         Optional env:
///           - ROUND_WINDOW_DAYS     : challenge window in days (default 7; genesis used 30)
///
///         The round hash is `keccak256(abi.encode(beneficiaries, amounts, ipfsUri))` — the
///         script logs it so the finalize step (and any observer) can reference the round.
contract KeeperProposeRound is Script {
    function run() external returns (bytes32 roundHash) {
        RoundRegistry registry = RoundRegistry(vm.envAddress("REGISTRY_ADDRESS"));
        address[] memory beneficiaries = vm.envAddress("ROUND_BENEFICIARIES", ",");
        uint256[] memory amounts = vm.envUint("ROUND_AMOUNTS", ",");
        string memory ipfsUri = vm.envString("ROUND_IPFS");
        uint32 windowDays = uint32(vm.envOr("ROUND_WINDOW_DAYS", uint256(7)));

        require(beneficiaries.length == amounts.length, "beneficiaries/amounts length mismatch");

        roundHash = keccak256(abi.encode(beneficiaries, amounts, ipfsUri));

        console2.log("== KeeperProposeRound ==");
        console2.log("Registry:   ", address(registry));
        console2.log("Window days:", windowDays);
        console2.logBytes32(roundHash);

        vm.startBroadcast(); // signer from CLI (keeper hot key)
        registry.proposeRound(roundHash, beneficiaries, amounts, ipfsUri, windowDays);
        vm.stopBroadcast();

        console2.log("Round proposed. Finalize after the window with KeeperFinalize + this hash.");
        return roundHash;
    }
}
