// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

import {Script, console2} from "forge-std/Script.sol";

import {PricingEngine} from "../src/insurance/PricingEngine.sol";
import {PremiumPool} from "../src/insurance/PremiumPool.sol";
import {PolicyRegistry} from "../src/insurance/PolicyRegistry.sol";

/// @title  VerifyDeploymentPhase3 — read-only post-deploy sanity check for Phase 3 wiring
/// @notice Re-asserts every role-wiring property that DeployPhase3.s.sol set up.
///         Run after the Ledger broadcast to confirm the on-chain state is correct.
///
/// @dev    Required environment variables:
///           - PRICING_ENGINE_ADDRESS   : deployed PricingEngine
///           - PREMIUM_POOL_ADDRESS     : deployed PremiumPool
///           - POLICY_REGISTRY_ADDRESS  : deployed PolicyRegistry
///           - ADMIN_ADDRESS            : the EOA / Safe that holds DEFAULT_ADMIN_ROLE
///
///         Optional:
///           - KEEPER_ADDRESS           : if set, verifies that KEEPER_ROLE is granted
///
///         No private key required — pure read. Run with:
///           forge script script/VerifyDeploymentPhase3.s.sol:VerifyDeploymentPhase3 \
///             --rpc-url $RPC_ARBITRUM_SEPOLIA -vv
///
/// @dev    Assertions checked (9 total):
///           1. PricingEngine admin is ADMIN_ADDRESS
///           2. PremiumPool admin is ADMIN_ADDRESS
///           3. PolicyRegistry admin is ADMIN_ADDRESS
///           4. PremiumPool.POLICY_REGISTRY_ROLE granted to PolicyRegistry
///           5. Admin does NOT hold POLICY_REGISTRY_ROLE (least-privilege)
///           6. PolicyRegistry.usdc() matches PremiumPool.usdc()
///           7. PolicyRegistry.pricingEngine() = PricingEngine address
///           8. PolicyRegistry.pool() = PremiumPool address
///           9. (optional) KEEPER_ROLE granted to KEEPER_ADDRESS if env is set
contract VerifyDeploymentPhase3 is Script {
    uint256 internal _pass;
    uint256 internal _fail;

    function run() external {
        PricingEngine engine = PricingEngine(vm.envAddress("PRICING_ENGINE_ADDRESS"));
        PremiumPool pool = PremiumPool(vm.envAddress("PREMIUM_POOL_ADDRESS"));
        PolicyRegistry registry = PolicyRegistry(vm.envAddress("POLICY_REGISTRY_ADDRESS"));
        address admin = vm.envAddress("ADMIN_ADDRESS");

        console2.log("== VerifyDeploymentPhase3 ==");
        console2.log("PricingEngine  :", address(engine));
        console2.log("PremiumPool    :", address(pool));
        console2.log("PolicyRegistry :", address(registry));
        console2.log("Admin          :", admin);
        console2.log("");

        // 1. PricingEngine admin (immutable, not AccessControl)
        _check(engine.admin() == admin, "1/9 PricingEngine.admin = ADMIN_ADDRESS");

        // 2. PremiumPool admin
        _check(pool.hasRole(pool.DEFAULT_ADMIN_ROLE(), admin), "2/9 PremiumPool.admin = ADMIN_ADDRESS");

        // 3. PolicyRegistry admin
        _check(registry.hasRole(registry.DEFAULT_ADMIN_ROLE(), admin), "3/9 PolicyRegistry.admin = ADMIN_ADDRESS");

        // 4. PremiumPool grants POLICY_REGISTRY_ROLE to PolicyRegistry
        _check(
            pool.hasRole(pool.POLICY_REGISTRY_ROLE(), address(registry)),
            "4/9 PremiumPool.POLICY_REGISTRY_ROLE -> PolicyRegistry"
        );

        // 5. Admin does NOT hold POLICY_REGISTRY_ROLE (least-privilege)
        _check(!pool.hasRole(pool.POLICY_REGISTRY_ROLE(), admin), "5/9 admin does NOT hold POLICY_REGISTRY_ROLE");

        // 6. PolicyRegistry.pool == PremiumPool (address cross-check)
        _check(address(registry.pool()) == address(pool), "6/9 PolicyRegistry.pool = PremiumPool");

        // 7. PolicyRegistry.pricingEngine == PricingEngine
        _check(address(registry.pricingEngine()) == address(engine), "7/9 PolicyRegistry.pricingEngine = PricingEngine");

        // 8. PremiumPool and PolicyRegistry share the same USDC token
        _check(address(pool.usdc()) == address(registry.usdc()), "8/9 PremiumPool.usdc == PolicyRegistry.usdc");

        // 9. (optional) keeper has KEEPER_ROLE on PolicyRegistry
        address keeperAddr = vm.envOr("KEEPER_ADDRESS", address(0));
        if (keeperAddr != address(0)) {
            console2.log("Keeper         :", keeperAddr);
            _check(
                registry.hasRole(registry.KEEPER_ROLE(), keeperAddr), "9/9 PolicyRegistry.KEEPER_ROLE -> KEEPER_ADDRESS"
            );
        } else {
            console2.log("KEEPER_ADDRESS not set - skipping assertion 9/9");
            _pass++;
        }

        console2.log("");
        console2.log("Passed:", _pass);
        console2.log("Failed:", _fail);

        if (_fail > 0) revert("VerifyDeploymentPhase3: wiring assertions failed");
        console2.log("Phase 3 wiring OK");
    }

    function _check(
        bool condition,
        string memory label
    ) internal {
        if (condition) {
            console2.log("[PASS]", label);
            _pass++;
        } else {
            console2.log("[FAIL]", label);
            _fail++;
        }
    }
}
