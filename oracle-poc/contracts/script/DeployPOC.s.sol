// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

import {Script} from "forge-std/Script.sol";
import {console2} from "forge-std/console2.sol";

import {IReclaim} from "../src/interfaces/IReclaim.sol";
import {ReclaimWeatherSource} from "../src/sources/ReclaimWeatherSource.sol";

/// @title  DeployPOC — deploy ReclaimWeatherSource to Arbitrum Sepolia
/// @notice Deploys a single-station, single-type instance pointed at the official
///         Reclaim verifier on Arbitrum Sepolia (per docs.reclaimprotocol.org,
///         retrieved 2026-05-16).
/// @dev    Signer convention matches Aratea/contracts/script/DeployArateaPhase1.s.sol:
///         the deployer address is read from env, and the actual signer is provided at
///         CLI invocation time via --ledger / --private-key / --account. This keeps
///         plain-text private keys out of .env files.
///
///         Required env:
///         - DEPLOYER_ADDRESS         (the EOA that will receive ownership of the deploy tx)
///
///         Optional env (sensible defaults):
///         - RECLAIM_VERIFIER_ADDRESS (defaults to Arbitrum Sepolia official)
///         - WEATHER_LOCATION_KEY     (defaults to "KJFK")
///         - WEATHER_TYPE_KEY         (defaults to "TEMP_C")
///
///         Usage (Ledger):
///         forge script script/DeployPOC.s.sol:DeployPOC \
///             --rpc-url $RPC_ARBITRUM_SEPOLIA \
///             --ledger --sender $DEPLOYER_ADDRESS --hd-paths "m/44'/60'/0'/0/0" \
///             --broadcast --verify
///
///         Usage (private key in env):
///         forge script script/DeployPOC.s.sol:DeployPOC \
///             --rpc-url $RPC_ARBITRUM_SEPOLIA \
///             --private-key $DEPLOYER_PK \
///             --broadcast --verify
contract DeployPOC is Script {
    /// @dev Official Reclaim verifier proxy on Arbitrum Sepolia.
    ///      Source: https://docs.reclaimprotocol.org/onchain/solidity/supported-networks
    address internal constant DEFAULT_RECLAIM_ARBITRUM_SEPOLIA = 0x4D1ee04EB5CeE02d4C123d4b67a86bDc7cA2E62A;

    function run() external returns (ReclaimWeatherSource source) {
        address deployer = vm.envAddress("DEPLOYER_ADDRESS");
        require(deployer != address(0), "DeployPOC: DEPLOYER_ADDRESS is the zero address");

        address verifierAddress = vm.envOr("RECLAIM_VERIFIER_ADDRESS", DEFAULT_RECLAIM_ARBITRUM_SEPOLIA);
        string memory locationKey = vm.envOr("WEATHER_LOCATION_KEY", string("KJFK"));
        string memory typeKey = vm.envOr("WEATHER_TYPE_KEY", string("TEMP_C"));

        bytes32 location = keccak256(bytes(locationKey));
        bytes32 measurementType = keccak256(bytes(typeKey));

        console2.log("== DeployPOC ==");
        console2.log("Deployer:", deployer);
        console2.log("Reclaim verifier:", verifierAddress);
        console2.log("Location key:", locationKey);
        console2.log("Type key:", typeKey);

        // The signer is provided by Foundry's CLI flags (--ledger / --private-key /
        // --account / --mnemonic). startBroadcast(deployer) tells Foundry to route every
        // subsequent state-changing call through whatever signer was configured to sign
        // for `deployer`. If the configured signer cannot sign for `deployer`, Foundry
        // reverts before broadcasting.
        vm.startBroadcast(deployer);
        source = new ReclaimWeatherSource(IReclaim(verifierAddress), location, measurementType);
        vm.stopBroadcast();

        console2.log("ReclaimWeatherSource deployed at:", address(source));
    }
}
