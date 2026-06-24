// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

import {Script, console2} from "forge-std/Script.sol";

import {PolicyRegistry}  from "../src/insurance/PolicyRegistry.sol";
import {IPolicyRegistry} from "../src/interfaces/IPolicyRegistry.sol";

/// @title  KeeperSettlePolicy — settles a parametric policy after the oracle posts a result
/// @notice The keeper (KEEPER_ROLE on PolicyRegistry) calls this once:
///           - the policy's targetDate has passed (settlement window is open), and
///           - the oracle has posted a confirmed temperature result for
///             (policy.locationKey, policy.targetDate).
///
///         The PolicyRegistry then:
///           - If observedTempF ≥ triggerThresholdF → CLAIMED, payout to subscriber
///           - Else                                  → EXPIRED, reserve released
///
///         Required env:
///           - POLICY_REGISTRY_ADDRESS : deployed PolicyRegistry
///           - POLICY_ID               : 0x-prefixed bytes32 policy id to settle
///         Optional env:
///           - MOCK_ORACLE_ADDRESS     : if set, logs a reminder to call postResult() first
///
///         Signer = keeper (KEEPER_ROLE holder). Provided via CLI:
///           forge script script/KeeperSettlePolicy.s.sol \
///             --rpc-url $RPC_ARBITRUM_SEPOLIA \
///             --private-key $KEEPER_PRIVATE_KEY \
///             --broadcast \
///             -vv
contract KeeperSettlePolicy is Script {
    function run() external {
        PolicyRegistry registry = PolicyRegistry(vm.envAddress("POLICY_REGISTRY_ADDRESS"));
        bytes32 policyId = vm.envBytes32("POLICY_ID");

        require(address(registry) != address(0), "POLICY_REGISTRY_ADDRESS zero");
        require(policyId != bytes32(0), "POLICY_ID zero");

        console2.log("== KeeperSettlePolicy ==");
        console2.log("PolicyRegistry:", address(registry));
        console2.logBytes32(policyId);

        // Hint: if a mock oracle is in play, remind the operator to post the result first.
        address mockOracle = vm.envOr("MOCK_ORACLE_ADDRESS", address(0));
        if (mockOracle != address(0)) {
            console2.log("Reminder: ensure MockWeatherOracle.postResult() was called at:", mockOracle);
        }

        // Read policy state for informational logging (no signer required for view calls)
        try registry.getPolicy(policyId) returns (
            IPolicyRegistry.Policy memory p
        ) {
            console2.log("Subscriber:     ", p.subscriber);
            console2.log("LocationKey:    ");
            console2.logBytes32(p.locationKey);
            console2.log("TargetDate:     ", p.targetDate);
            console2.log("SumAssured:     ", p.sumAssured);
            console2.log("TriggerThresh:  ", p.triggerThresholdF);
            console2.log("State (0=Pend,1=Act,2=Clm,3=Exp):", uint8(p.state));
        } catch {
            revert("Policy not found - check POLICY_ID");
        }

        vm.startBroadcast(); // signer = keeper via CLI
        registry.settlePolicy(policyId);
        vm.stopBroadcast();

        console2.log("Policy settled. Check on-chain state for CLAIMED or EXPIRED outcome.");
    }
}
