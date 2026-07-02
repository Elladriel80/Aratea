// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

import {Script, console2} from "forge-std/Script.sol";

import {PricingEngine}      from "../src/insurance/PricingEngine.sol";
import {PremiumPool}        from "../src/insurance/PremiumPool.sol";
import {PolicyRegistry}     from "../src/insurance/PolicyRegistry.sol";
import {MockWeatherOracle}  from "../src/insurance/MockWeatherOracle.sol";

/// @title  DeployPhase3 — deploys the parametric insurance stack (Phase 3)
/// @notice Deploys PricingEngine → PremiumPool → PolicyRegistry in order,
///         wires the POLICY_REGISTRY_ROLE on PremiumPool, and logs all addresses.
///
///         Oracle strategy:
///           - If USE_MOCK_ORACLE=true (default), also deploys MockWeatherOracle
///             and uses it as the oracle. Appropriate for Arbitrum Sepolia testing.
///           - If USE_MOCK_ORACLE=false, reads ORACLE_ADDRESS from env (must be a
///             live IWeatherOracle implementation, e.g. ReclaimWeatherSource).
///
///         Required env:
///           - ADMIN_ADDRESS   : association admin (DEFAULT_ADMIN_ROLE on pool + registry)
///           - USDC_ADDRESS    : USDC ERC-20 address on target chain
///         Optional env:
///           - USE_MOCK_ORACLE : "true" (default) to deploy + use MockWeatherOracle
///           - ORACLE_ADDRESS  : IWeatherOracle address (required if USE_MOCK_ORACLE=false)
///
///         Resulting Phase 3 topology:
///           PricingEngine.admin       = ADMIN_ADDRESS
///           PremiumPool.DEFAULT_ADMIN = ADMIN_ADDRESS
///           PremiumPool.POLICY_REGISTRY_ROLE = PolicyRegistry (granted here)
///           PolicyRegistry.DEFAULT_ADMIN = ADMIN_ADDRESS
///           PolicyRegistry.KEEPER_ROLE   = to be granted to keeper by admin after deploy
///           oracle                    = MockWeatherOracle (testnet) | ORACLE_ADDRESS (mainnet)
///
///         After deploy, the admin must:
///           1. Grant KEEPER_ROLE on PolicyRegistry to the keeper address.
///           2. For each supported location, call setSupportedLocation(locationKey, true).
///           3. Seed the pool with initial capital if needed (deposit USDC as admin).
///           4. Set NEXT_PUBLIC_POLICY_REGISTRY_ADDRESS / NEXT_PUBLIC_PREMIUM_POOL_ADDRESS
///              / NEXT_PUBLIC_PRICING_ENGINE_ADDRESS in the dashboard env.
contract DeployPhase3 is Script {
    function run() external returns (
        PricingEngine      pricingEngine,
        PremiumPool        pool,
        PolicyRegistry     policyRegistry,
        address            oracle
    ) {
        address admin = vm.envAddress("ADMIN_ADDRESS");
        address usdc  = vm.envAddress("USDC_ADDRESS");
        require(admin != address(0), "ADMIN_ADDRESS zero");
        require(usdc  != address(0), "USDC_ADDRESS zero");

        bool useMock = vm.envOr("USE_MOCK_ORACLE", true);
        // Safety guard: MockWeatherOracle is permissioned but not production-grade.
        // Refuse to deploy it on Arbitrum mainnet (chainid 42161) regardless of the env var.
        require(!useMock || block.chainid != 42161,
            "USE_MOCK_ORACLE forbidden on Arbitrum mainnet (chainid 42161)");

        console2.log("== DeployPhase3 ==");
        console2.log("Admin:", admin);
        console2.log("USDC: ", usdc);
        console2.log("Mock oracle:", useMock);

        vm.startBroadcast(admin);

        // 1. Pricing engine — stateless actuarial calculator
        pricingEngine = new PricingEngine(admin);
        console2.log("PricingEngine:", address(pricingEngine));

        // 2. Premium pool — USDC reserves + MCR enforcement
        pool = new PremiumPool(admin, usdc);
        console2.log("PremiumPool:  ", address(pool));

        // 3. Oracle — mock for testnet, real for mainnet
        if (useMock) {
            oracle = address(new MockWeatherOracle());
            console2.log("MockWeatherOracle:", oracle);
        } else {
            oracle = vm.envAddress("ORACLE_ADDRESS");
            require(oracle != address(0), "ORACLE_ADDRESS zero");
            console2.log("Oracle (external):", oracle);
        }

        // 4. Policy registry — full lifecycle
        policyRegistry = new PolicyRegistry(admin, usdc, address(pricingEngine), address(pool), oracle);
        console2.log("PolicyRegistry:", address(policyRegistry));

        // 5. Wire: PolicyRegistry needs POLICY_REGISTRY_ROLE on PremiumPool
        pool.grantRole(pool.POLICY_REGISTRY_ROLE(), address(policyRegistry));

        vm.stopBroadcast();

        _assertWiring(pool, policyRegistry, admin);

        console2.log("== Phase 3 wiring complete ==");
        console2.log("");
        console2.log("Next steps (admin):");
        console2.log("  1. Grant KEEPER_ROLE on PolicyRegistry to the keeper address:");
        console2.log("     cast send $POLICY_REGISTRY_ADDRESS 'grantRole(bytes32,address)'");
        console2.log("       $(cast keccak 'KEEPER_ROLE') $KEEPER_ADDRESS");
        console2.log("  2. Enable locations: setSupportedLocation(keccak256(SERIES_NAME), true)");
        console2.log("  3. Set dashboard env: NEXT_PUBLIC_POLICY_REGISTRY_ADDRESS,");
        console2.log("     NEXT_PUBLIC_PREMIUM_POOL_ADDRESS, NEXT_PUBLIC_PRICING_ENGINE_ADDRESS");
        if (useMock) {
            console2.log("  4. Post oracle results (testnet): call MockWeatherOracle.postResult(...)");
        }
    }

    function _assertWiring(PremiumPool pool, PolicyRegistry registry, address admin) private view {
        require(pool.hasRole(pool.DEFAULT_ADMIN_ROLE(), admin), "pool !admin");
        require(pool.hasRole(pool.POLICY_REGISTRY_ROLE(), address(registry)), "pool !registry role");
        require(registry.hasRole(registry.DEFAULT_ADMIN_ROLE(), admin), "registry !admin");
        require(!pool.hasRole(pool.DEFAULT_ADMIN_ROLE(), address(registry)), "registry must NOT be pool admin");
    }
}
