// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

import {Test} from "forge-std/Test.sol";
import {MockERC20} from "forge-std/mocks/MockERC20.sol";

import {PricingEngine}    from "../../src/insurance/PricingEngine.sol";
import {PremiumPool}      from "../../src/insurance/PremiumPool.sol";
import {PolicyRegistry}   from "../../src/insurance/PolicyRegistry.sol";
import {MockWeatherOracle} from "../../src/insurance/MockWeatherOracle.sol";
import {IPolicyRegistry}  from "../../src/interfaces/IPolicyRegistry.sol";

/// @title  FullStackPhase3E2E — end-to-end integration test for the Phase 3 stack
/// @notice Exercises the complete parametric policy lifecycle:
///         Deploy → seed capital → subscribe → oracle post → settle (CLAIMED / EXPIRED)
///         Uses MockERC20 as USDC and MockWeatherOracle for oracle results.
contract FullStackPhase3E2E is Test {

    // ── actors ────────────────────────────────────────────────────────────────
    address internal admin  = makeAddr("admin");
    address internal keeper = makeAddr("keeper");
    address internal alice  = makeAddr("alice");
    address internal bob    = makeAddr("bob");

    // ── contracts ─────────────────────────────────────────────────────────────
    MockERC20          internal usdc;
    PricingEngine      internal engine;
    PremiumPool        internal pool;
    MockWeatherOracle  internal oracle;
    PolicyRegistry     internal registry;

    // ── constants ─────────────────────────────────────────────────────────────
    bytes32 internal constant LOC_SFO  = keccak256("KXHIGHTSFO");
    bytes32 internal constant LOC_CHI  = keccak256("KXLOWTCHI");
    uint16  internal constant THRESH_SFO = 900;  // 90.0 °F × 10
    uint16  internal constant THRESH_CHI = 100;  // 10.0 °F × 10

    // ── setup ─────────────────────────────────────────────────────────────────

    function setUp() public {
        // 1. Deploy mock USDC (6 decimals)
        MockERC20 mock = new MockERC20();
        mock.initialize("Mock USDC", "USDC", 6);
        usdc = mock;

        // 2. Deploy Phase 3 contracts
        engine   = new PricingEngine(admin);
        pool     = new PremiumPool(admin, address(usdc));
        oracle   = new MockWeatherOracle();
        registry = new PolicyRegistry(
            admin, address(usdc), address(engine), address(pool), address(oracle)
        );

        // 3. Wire roles
        vm.startPrank(admin);
        pool.grantRole(pool.POLICY_REGISTRY_ROLE(), address(registry));
        registry.grantRole(registry.KEEPER_ROLE(), keeper);
        registry.setSupportedLocation(LOC_SFO, true);
        registry.setSupportedLocation(LOC_CHI, true);
        vm.stopPrank();

        // 4. Seed pool above MCR floor (200 000 USDC)
        _mintAndApproveAdmin(250_000e6);
        vm.startPrank(admin);
        pool.deposit(250_000e6);
        vm.stopPrank();

        // 5. Fund subscribers
        _mintFor(alice, 10_000e6);
        _mintFor(bob,   10_000e6);
    }

    // ── helpers ───────────────────────────────────────────────────────────────

    function _mintFor(address who, uint256 amount) internal {
        deal(address(usdc), who, amount);
        vm.prank(who);
        usdc.approve(address(registry), type(uint256).max);
    }

    function _mintAndApproveAdmin(uint256 amount) internal {
        deal(address(usdc), admin, amount);
        vm.prank(admin);
        usdc.approve(address(pool), amount);
    }

    function _subscribeFor(
        address subscriber,
        bytes32 location,
        uint64  targetDate,
        uint256 sumAssured,
        uint16  threshold,
        uint16  pBps
    ) internal returns (bytes32 policyId) {
        vm.prank(subscriber);
        return registry.subscribe(location, targetDate, sumAssured, threshold, pBps);
    }

    // ── E2E: CLAIMED path ──────────────────────────────────────────────────────

    /// Full flow: subscribe → oracle posts above threshold → keeper settles → payout
    function test_e2e_claimedPath() public {
        uint64 targetDate = uint64(block.timestamp) + 7 days;

        // Alice subscribes: 1 000 USDC coverage, 40% probability, threshold 90°F
        bytes32 pid = _subscribeFor(alice, LOC_SFO, targetDate, 1_000e6, THRESH_SFO, 4_000);

        // Verify policy state = Pending
        assertEq(uint8(registry.stateOf(pid)), uint8(IPolicyRegistry.PolicyState.Pending));

        // Pool has premium + seed
        assertGt(pool.availableCapital(), 250_000e6 - 1_000e6); // seed minus reserve

        // Advance to settlement window
        vm.warp(targetDate);

        // Keeper posts oracle result: 92°F (above 90°F threshold)
        oracle.postResult(LOC_SFO, targetDate, 920);

        uint256 aliceBefore = usdc.balanceOf(alice);
        vm.prank(keeper);
        registry.settlePolicy(pid);

        // Assert CLAIMED + payout received
        assertEq(uint8(registry.stateOf(pid)), uint8(IPolicyRegistry.PolicyState.Claimed));
        assertEq(usdc.balanceOf(alice) - aliceBefore, 1_000e6, "alice should receive sumAssured");
        assertEq(pool.reservedForPolicy(pid), 0, "reserve cleared after payout");
    }

    // ── E2E: EXPIRED path ─────────────────────────────────────────────────────

    /// Full flow: subscribe → oracle posts below threshold → keeper settles → reserve released
    function test_e2e_expiredPath() public {
        uint64 targetDate = uint64(block.timestamp) + 3 days;

        bytes32 pid = _subscribeFor(alice, LOC_SFO, targetDate, 2_000e6, THRESH_SFO, 3_000);
        // Capture balance AFTER subscribe — premium already deducted at this point
        uint256 aliceBalAfterSub = usdc.balanceOf(alice);

        vm.warp(targetDate);
        // Oracle result: 85°F (below 90°F threshold)
        oracle.postResult(LOC_SFO, targetDate, 850);

        uint256 poolBefore = pool.availableCapital();
        vm.prank(keeper);
        registry.settlePolicy(pid);

        assertEq(uint8(registry.stateOf(pid)), uint8(IPolicyRegistry.PolicyState.Expired));
        // sumAssured reserve returned to pool
        assertEq(pool.availableCapital(), poolBefore + 2_000e6, "reserve released to pool");
        // Settlement must not change alice's balance (premium was already deducted at subscription)
        assertEq(usdc.balanceOf(alice), aliceBalAfterSub, "alice balance unchanged (no payout)");
    }

    // ── E2E: permissionless expiry ────────────────────────────────────────────

    /// After grace period anyone can call expirePolicy() to release reserve
    function test_e2e_permissionlessExpiry() public {
        uint64 targetDate = uint64(block.timestamp) + 1 days;
        bytes32 pid = _subscribeFor(alice, LOC_SFO, targetDate, 500e6, THRESH_SFO, 2_000);

        // Advance past grace period (targetDate + 2 days)
        vm.warp(targetDate + 3 days);

        uint256 poolBefore = pool.availableCapital();
        // Bob (anyone) can expire
        vm.prank(bob);
        registry.expirePolicy(pid);

        assertEq(uint8(registry.stateOf(pid)), uint8(IPolicyRegistry.PolicyState.Expired));
        assertEq(pool.availableCapital(), poolBefore + 500e6);
    }

    // ── E2E: two concurrent policies ──────────────────────────────────────────

    /// Alice and Bob hold independent policies on different locations; both settle correctly
    function test_e2e_twoConcurrentPolicies() public {
        uint64 targetDate = uint64(block.timestamp) + 5 days;

        // Alice: SFO high-temp policy
        bytes32 pidAlice = _subscribeFor(alice, LOC_SFO, targetDate, 1_000e6, THRESH_SFO, 5_000);
        // Bob: CHI low-temp policy
        bytes32 pidBob   = _subscribeFor(bob,   LOC_CHI, targetDate, 800e6,   THRESH_CHI, 2_000);

        vm.warp(targetDate);

        // SFO: 95°F → above 90°F threshold (900) → CLAIMED for Alice
        oracle.postResult(LOC_SFO, targetDate, 950);
        // CHI: 5°F → below 10°F threshold (100) → EXPIRED for Bob (no event trigger)
        oracle.postResult(LOC_CHI, targetDate, 50);

        uint256 aliceBefore = usdc.balanceOf(alice);
        uint256 bobBefore   = usdc.balanceOf(bob);

        vm.startPrank(keeper);
        registry.settlePolicy(pidAlice);
        registry.settlePolicy(pidBob);
        vm.stopPrank();

        assertEq(uint8(registry.stateOf(pidAlice)), uint8(IPolicyRegistry.PolicyState.Claimed));
        assertEq(uint8(registry.stateOf(pidBob)),   uint8(IPolicyRegistry.PolicyState.Expired));
        assertEq(usdc.balanceOf(alice) - aliceBefore, 1_000e6, "Alice claimed");
        assertEq(usdc.balanceOf(bob)   - bobBefore,   0,       "Bob no payout");
    }

    // ── E2E: exact-threshold trigger ──────────────────────────────────────────

    /// Temperature exactly at threshold → CLAIMED (>= condition)
    function test_e2e_exactThresholdClaimed() public {
        uint64 targetDate = uint64(block.timestamp) + 2 days;
        bytes32 pid = _subscribeFor(alice, LOC_SFO, targetDate, 1_000e6, THRESH_SFO, 4_500);

        vm.warp(targetDate);
        oracle.postResult(LOC_SFO, targetDate, int16(THRESH_SFO)); // exactly 90.0°F

        vm.prank(keeper);
        registry.settlePolicy(pid);
        assertEq(uint8(registry.stateOf(pid)), uint8(IPolicyRegistry.PolicyState.Claimed));
    }

    // ── E2E: MCR solvency enforcement ─────────────────────────────────────────

    /// Admin can withdraw surplus but cannot breach the MCR floor
    function test_e2e_withdrawBelowMCRReverts() public {
        // 250k available, MCR = 200k → max withdrawal = 50k
        vm.prank(admin);
        pool.withdraw(50_000e6); // ok: leaves 200k = MCR floor exactly

        // Next withdrawal of 1 USDC would breach MCR
        vm.prank(admin);
        vm.expectRevert();
        pool.withdraw(1e6);
    }

    // ── E2E: G2 gate — reduce adverse loading after edge confirmed ────────────

    /// Admin reduces adverse loading from 5% to 2% once G2 Brier gate is confirmed
    function test_e2e_g2GateReducesAdverseLoading() public {
        assertEq(engine.adverseLoadingBps(), 500); // initial 5%

        // Quote at initial 5% adverse loading
        // adverseComponent = 500 × 1000e6 / 10000 = 50e6
        uint256 premiumBefore = engine.quote(3_000, 1_000e6, 1);

        // G2 gate confirmed — admin reduces adverse loading from 5% to 2%
        vm.prank(admin);
        engine.setAdverseLoading(200);

        assertEq(engine.adverseLoadingBps(), 200);

        // Quote after: adverseComponent = 200 × 1000e6 / 10000 = 20e6 (30e6 cheaper)
        uint256 premiumAfter = engine.quote(3_000, 1_000e6, 1);
        assertLt(premiumAfter, premiumBefore, "premium should be lower after G2 gate reduces adverse loading");
    }
}
