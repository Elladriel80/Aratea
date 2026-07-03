// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

import {Test} from "forge-std/Test.sol";
import {MockERC20} from "forge-std/mocks/MockERC20.sol";

import {PricingEngine} from "../../src/insurance/PricingEngine.sol";
import {PremiumPool} from "../../src/insurance/PremiumPool.sol";
import {PolicyRegistry} from "../../src/insurance/PolicyRegistry.sol";
import {IWeatherOracle} from "../../src/interfaces/IWeatherOracle.sol";
import {IPolicyRegistry} from "../../src/interfaces/IPolicyRegistry.sol";
import {IPremiumPool} from "../../src/interfaces/IPremiumPool.sol";
import {IPricingEngine} from "../../src/interfaces/IPricingEngine.sol";

// ─── Helpers ──────────────────────────────────────────────────────────────────

contract MockUSDC is MockERC20 {
    constructor() {
        initialize("Mock USDC", "USDC", 6);
    }

    function mint(
        address to,
        uint256 amount
    ) external {
        _mint(to, amount);
    }
}

contract MockOracle is IWeatherOracle {
    mapping(bytes32 => mapping(uint64 => int16)) private _results;
    mapping(bytes32 => mapping(uint64 => bool)) private _settled;

    function setResult(
        bytes32 locationKey,
        uint64 targetDate,
        int16 tempF
    ) external {
        _results[locationKey][targetDate] = tempF;
        _settled[locationKey][targetDate] = true;
    }

    function getResult(
        bytes32 locationKey,
        uint64 targetDate
    ) external view returns (int16 observedTempF, bool settled) {
        return (_results[locationKey][targetDate], _settled[locationKey][targetDate]);
    }
}

// ─── PricingEngine tests ───────────────────────────────────────────────────────

contract PricingEngineTest is Test {
    PricingEngine engine;
    address admin = makeAddr("admin");

    function setUp() public {
        engine = new PricingEngine(admin);
    }

    function test_defaults() public view {
        assertEq(engine.expenseLoadingBps(), 2000);
        assertEq(engine.solvencyLoadingBps(), 1500);
        assertEq(engine.adverseLoadingBps(), 500);
        assertEq(engine.premiumMin(), 5_000_000);
    }

    function test_quote_floorsAtMin() public view {
        // p=1%, S=10 USDC → expected loss 0.1 USDC + loadings → still below 5 USDC floor
        uint256 p = engine.quote(100, 10_000_000, 1); // 1% × 10 USDC
        assertEq(p, engine.premiumMin());
    }

    function test_quote_typical() public view {
        // p=70%, S=1000 USDC, daysAhead=1
        // expectedLoss = 7000 * 1000e6 / 10000 = 700e6
        // loaded = 700e6 * 1.20 * 1.15 = 700e6 * 1.38 = 966e6
        // adverseComponent = 500 * 1000e6 / 10000 = 50e6
        // horizonSurcharge = 0 (daysAhead=1)
        // total = 966e6 + 50e6 = 1016e6
        // cap = 500e6 → clamped to 500e6
        uint256 p = engine.quote(7000, 1_000_000_000, 1);
        assertEq(p, 500_000_000); // capped at 50%
    }

    function test_quote_horizonSurcharge() public view {
        // p=10%, S=1000 USDC, daysAhead=3
        // expectedLoss = 1000 * 1000e6 / 10000 = 100e6
        // loaded = 100e6 * 1.20 * 1.15 = 138e6
        // surcharge = 138e6 * 5% * 2 = 13.8e6 → 13e6 (integer division)
        // adverseComponent = 500 * 1000e6 / 10000 = 50e6
        // total = 138e6 + 13e6 + 50e6 = 201e6
        uint256 p3 = engine.quote(1000, 1_000_000_000, 3);
        uint256 p1 = engine.quote(1000, 1_000_000_000, 1);
        assertGt(p3, p1, "3-day horizon should cost more than 1-day");
    }

    function test_quote_revertsOnInvalidProbability() public {
        vm.expectRevert(abi.encodeWithSelector(IPricingEngine.InvalidProbabilityBps.selector, uint16(10_001)));
        engine.quote(10_001, 1_000_000_000, 1);
    }

    function test_quote_revertsOnZeroSumAssured() public {
        vm.expectRevert();
        engine.quote(5000, 0, 1);
    }

    function test_setAdverseLoading_onlyAdmin() public {
        vm.prank(makeAddr("notAdmin"));
        vm.expectRevert(PricingEngine.NotAdmin.selector);
        engine.setAdverseLoading(200);
    }

    function test_setAdverseLoading_tooHigh() public {
        vm.prank(admin);
        vm.expectRevert();
        engine.setAdverseLoading(2000); // > 1000 (10% cap)
    }

    function test_setAdverseLoading_g2Gate() public {
        vm.prank(admin);
        engine.setAdverseLoading(200); // G2 confirmed: reduce from 5% to 2%
        assertEq(engine.adverseLoadingBps(), 200);
    }
}

// ─── PremiumPool tests ────────────────────────────────────────────────────────

contract PremiumPoolTest is Test {
    PremiumPool pool;
    MockUSDC usdc;

    address admin = makeAddr("admin");
    address registry = makeAddr("registry");
    address alice = makeAddr("alice");

    bytes32 constant POLICY_ID = keccak256("test-policy");
    bytes32 constant POLICY_ID_2 = keccak256("test-policy-2");

    function setUp() public {
        usdc = new MockUSDC();
        pool = new PremiumPool(admin, address(usdc));

        // Grant POLICY_REGISTRY_ROLE to registry mock address
        // Use startPrank/stopPrank: vm.prank would be consumed by the POLICY_REGISTRY_ROLE() staticcall
        vm.startPrank(admin);
        pool.grantRole(pool.POLICY_REGISTRY_ROLE(), registry);
        vm.stopPrank();
    }

    function _seedPool(
        uint256 amount
    ) internal {
        usdc.mint(admin, amount);
        vm.startPrank(admin);
        usdc.approve(address(pool), amount);
        pool.deposit(amount);
        vm.stopPrank();
    }

    function test_deposit_updatesBalance() public {
        _seedPool(500_000e6);
        assertEq(pool.availableCapital(), 500_000e6);
        assertTrue(pool.isSolvent());
    }

    function test_deposit_onlyAdmin() public {
        usdc.mint(alice, 1e6);
        vm.prank(alice);
        vm.expectRevert();
        pool.deposit(1e6);
    }

    function test_withdraw_surplus() public {
        _seedPool(400_000e6); // above 200k MCR floor
        vm.prank(admin);
        pool.withdraw(100_000e6); // leaves 300k — still above MCR
        assertEq(pool.availableCapital(), 300_000e6);
    }

    function test_withdraw_revertsIfBreachesMCR() public {
        _seedPool(200_000e6); // exactly at MCR floor
        vm.prank(admin);
        vm.expectRevert(); // SolvencyCheckFailed
        pool.withdraw(1e6); // would leave 199_999e6 < MCR
    }

    function test_receivePremium_updatesBalance() public {
        _seedPool(200_000e6); // meet MCR
        // Registry sends USDC to pool then notifies
        usdc.mint(address(pool), 100e6);
        vm.prank(registry);
        pool.receivePremium(POLICY_ID, 100e6);
        assertEq(pool.availableCapital(), 200_100e6);
        assertEq(pool.annualPremiumsCollected(), 100e6);
    }

    function test_receivePremium_revertsWhenBelowMCR() public {
        // Pool starts with 0 capital → below MCR floor
        usdc.mint(address(pool), 50e6);
        vm.prank(registry);
        vm.expectRevert(); // PoolBelowMCR
        pool.receivePremium(POLICY_ID, 50e6);
    }

    function test_reserveForPolicy_locksCapital() public {
        _seedPool(300_000e6);
        vm.prank(registry);
        pool.reserveForPolicy(POLICY_ID, 50_000e6);
        assertEq(pool.availableCapital(), 250_000e6);
        assertEq(pool.totalReserved(), 50_000e6);
        assertEq(pool.reservedForPolicy(POLICY_ID), 50_000e6);
    }

    function test_reserveForPolicy_revertsIfDuplicate() public {
        _seedPool(300_000e6);
        vm.startPrank(registry);
        pool.reserveForPolicy(POLICY_ID, 50_000e6);
        vm.expectRevert(); // ReserveAlreadyExists
        pool.reserveForPolicy(POLICY_ID, 50_000e6);
        vm.stopPrank();
    }

    function test_reserveForPolicy_revertsIfInsufficient() public {
        _seedPool(100e6); // 100 USDC only
        vm.prank(registry);
        vm.expectRevert(); // InsufficientAvailableCapital
        pool.reserveForPolicy(POLICY_ID, 1000e6);
    }

    function test_payout_sendsUSDCAndReleasesRemainder() public {
        _seedPool(300_000e6);
        vm.startPrank(registry);
        pool.reserveForPolicy(POLICY_ID, 1000e6);
        pool.payout(POLICY_ID, alice, 1000e6); // full payout
        vm.stopPrank();
        assertEq(usdc.balanceOf(alice), 1000e6);
        assertEq(pool.reservedForPolicy(POLICY_ID), 0);
    }

    function test_payout_partialReleaseRemainder() public {
        _seedPool(300_000e6);
        vm.startPrank(registry);
        pool.reserveForPolicy(POLICY_ID, 1000e6);
        pool.payout(POLICY_ID, alice, 800e6); // partial payout
        vm.stopPrank();
        // 200e6 returned to available
        assertEq(pool.availableCapital(), 300_000e6 - 1000e6 + 200e6);
    }

    function test_releaseReserve_returnsToAvailable() public {
        _seedPool(300_000e6);
        vm.startPrank(registry);
        pool.reserveForPolicy(POLICY_ID, 50_000e6);
        pool.releaseReserve(POLICY_ID);
        vm.stopPrank();
        assertEq(pool.availableCapital(), 300_000e6);
        assertEq(pool.totalReserved(), 0);
    }

    function test_mcrFloor_dynamicAboveStatutory() public {
        _seedPool(500_000e6);
        // Inject premiums: 18% of 10M = 1.8M → exceeds statutory 200k
        usdc.mint(address(pool), 10_000_000e6);
        vm.prank(registry);
        pool.receivePremium(POLICY_ID, 10_000_000e6);
        // MCR floor = 18% × 10M = 1.8M
        assertEq(pool.mcrFloor(), (10_000_000e6 * 18) / 100);
    }
}

// ─── PolicyRegistry tests ─────────────────────────────────────────────────────

contract PolicyRegistryTest is Test {
    PricingEngine engine;
    PremiumPool pool;
    PolicyRegistry registry;
    MockUSDC usdc;
    MockOracle oracleMock;

    address admin = makeAddr("admin");
    address keeper = makeAddr("keeper");
    address alice = makeAddr("alice");

    bytes32 constant LOC_SFO = keccak256("KXHIGHTSFO");
    bytes32 constant LOC_CHI = keccak256("KXLOWTCHI");

    uint64 targetDate;
    uint16 constant THRESHOLD_F = 900; // 90.0 °F × 10

    function setUp() public {
        usdc = new MockUSDC();
        engine = new PricingEngine(admin);
        pool = new PremiumPool(admin, address(usdc));
        oracleMock = new MockOracle();
        registry = new PolicyRegistry(admin, address(usdc), address(engine), address(pool), address(oracleMock));

        // Wire roles
        vm.startPrank(admin);
        pool.grantRole(pool.POLICY_REGISTRY_ROLE(), address(registry));
        registry.grantRole(registry.KEEPER_ROLE(), keeper);
        registry.setSupportedLocation(LOC_SFO, true);
        registry.setSupportedLocation(LOC_CHI, true);
        vm.stopPrank();

        // Seed pool above MCR
        usdc.mint(admin, 250_000e6);
        vm.startPrank(admin);
        usdc.approve(address(pool), 250_000e6);
        pool.deposit(250_000e6);
        vm.stopPrank();

        // Target date = 3 days from now
        targetDate = uint64(block.timestamp) + 3 days;

        // Fund subscriber
        usdc.mint(alice, 100_000e6);
        vm.prank(alice);
        usdc.approve(address(registry), type(uint256).max);
    }

    // ── Helpers ───────────────────────────────────────────────────

    function _subscribe(
        uint256 sumAssured,
        uint16 pBps
    ) internal returns (bytes32 policyId) {
        vm.prank(alice);
        return registry.subscribe(LOC_SFO, targetDate, sumAssured, THRESHOLD_F, pBps);
    }

    // ── subscribe ─────────────────────────────────────────────────

    function test_subscribe_createsPolicyPending() public {
        bytes32 pid = _subscribe(1000e6, 4000); // 40% probability
        IPolicyRegistry.Policy memory p = registry.getPolicy(pid);
        assertEq(p.subscriber, alice);
        assertEq(p.sumAssured, 1000e6);
        assertEq(uint8(p.state), uint8(IPolicyRegistry.PolicyState.Pending));
        assertEq(p.locationKey, LOC_SFO);
        assertEq(p.targetDate, targetDate);
        assertEq(p.activatesAt, targetDate);
        assertEq(p.expiresAt, targetDate + 2 days);
    }

    function test_subscribe_transfersPremiumToPool() public {
        bytes32 pid = _subscribe(1000e6, 3000);
        IPolicyRegistry.Policy memory p = registry.getPolicy(pid);
        // Pool holds the premium (sent directly at subscribe)
        assertGt(usdc.balanceOf(address(pool)), 250_000e6); // initial seed + premium
        // Policy has correct premium recorded
        assertGt(p.premium, 0);
    }

    function test_subscribe_revertsUnsupportedLocation() public {
        vm.prank(alice);
        vm.expectRevert();
        registry.subscribe(keccak256("KXHIGHTUNK"), targetDate, 1000e6, THRESHOLD_F, 4000);
    }

    function test_subscribe_revertsTargetInPast() public {
        vm.prank(alice);
        vm.expectRevert();
        registry.subscribe(LOC_SFO, uint64(block.timestamp) - 1, 1000e6, THRESHOLD_F, 4000);
    }

    function test_subscribe_revertsZeroSumAssured() public {
        vm.prank(alice);
        vm.expectRevert();
        registry.subscribe(LOC_SFO, targetDate, 0, THRESHOLD_F, 4000);
    }

    // ── settlePolicy — CLAIMED ─────────────────────────────────────

    function test_settlePolicy_claimedWhenTempAboveThreshold() public {
        bytes32 pid = _subscribe(1000e6, 4000);

        // Advance to activatesAt
        vm.warp(targetDate);
        // Post oracle result: 95.0°F = 950 (above threshold 90.0°F = 900)
        oracleMock.setResult(LOC_SFO, targetDate, 950);

        uint256 aliceBefore = usdc.balanceOf(alice);
        vm.prank(keeper);
        registry.settlePolicy(pid);

        assertEq(uint8(registry.stateOf(pid)), uint8(IPolicyRegistry.PolicyState.Claimed));
        assertEq(usdc.balanceOf(alice) - aliceBefore, 1000e6);
        assertEq(pool.reservedForPolicy(pid), 0);
    }

    // ── settlePolicy — EXPIRED ─────────────────────────────────────

    function test_settlePolicy_expiredWhenTempBelowThreshold() public {
        bytes32 pid = _subscribe(1000e6, 4000);

        vm.warp(targetDate);
        oracleMock.setResult(LOC_SFO, targetDate, 850); // 85.0°F < 90.0°F threshold

        uint256 poolBefore = pool.availableCapital();
        vm.prank(keeper);
        registry.settlePolicy(pid);

        assertEq(uint8(registry.stateOf(pid)), uint8(IPolicyRegistry.PolicyState.Expired));
        // sumAssured reserve released back to pool
        assertEq(pool.availableCapital(), poolBefore + 1000e6);
    }

    // ── settlePolicy — at threshold ────────────────────────────────

    function test_settlePolicy_claimedAtExactThreshold() public {
        bytes32 pid = _subscribe(1000e6, 4000);
        vm.warp(targetDate);
        oracleMock.setResult(LOC_SFO, targetDate, int16(THRESHOLD_F)); // exact threshold

        vm.prank(keeper);
        registry.settlePolicy(pid);
        assertEq(uint8(registry.stateOf(pid)), uint8(IPolicyRegistry.PolicyState.Claimed));
    }

    // ── settlePolicy — error cases ─────────────────────────────────

    function test_settlePolicy_revertsNotKeeper() public {
        bytes32 pid = _subscribe(1000e6, 4000);
        vm.warp(targetDate);
        oracleMock.setResult(LOC_SFO, targetDate, 950);

        vm.prank(alice);
        vm.expectRevert();
        registry.settlePolicy(pid);
    }

    function test_settlePolicy_revertsBeforeActivatesAt() public {
        bytes32 pid = _subscribe(1000e6, 4000);
        // Still before targetDate
        oracleMock.setResult(LOC_SFO, targetDate, 950);
        vm.prank(keeper);
        vm.expectRevert(); // SettlementWindowNotOpen
        registry.settlePolicy(pid);
    }

    function test_settlePolicy_revertsAfterExpiresAt() public {
        bytes32 pid = _subscribe(1000e6, 4000);
        vm.warp(targetDate + 3 days); // past expiresAt (targetDate + 2 days)
        oracleMock.setResult(LOC_SFO, targetDate, 950);
        vm.prank(keeper);
        vm.expectRevert(); // SettlementWindowNotOpen
        registry.settlePolicy(pid);
    }

    function test_settlePolicy_revertsOracleNotSettled() public {
        bytes32 pid = _subscribe(1000e6, 4000);
        vm.warp(targetDate);
        // Oracle result not posted
        vm.prank(keeper);
        vm.expectRevert(); // SettlementWindowNotOpen
        registry.settlePolicy(pid);
    }

    function test_settlePolicy_revertsAlreadySettled() public {
        bytes32 pid = _subscribe(1000e6, 4000);
        vm.warp(targetDate);
        oracleMock.setResult(LOC_SFO, targetDate, 950);
        vm.prank(keeper);
        registry.settlePolicy(pid);
        // Second settle attempt
        vm.prank(keeper);
        vm.expectRevert(); // AlreadySettled
        registry.settlePolicy(pid);
    }

    // ── expirePolicy ───────────────────────────────────────────────

    function test_expirePolicy_afterGracePeriod() public {
        bytes32 pid = _subscribe(1000e6, 4000);
        vm.warp(targetDate + 3 days); // past expiresAt
        uint256 poolBefore = pool.availableCapital();
        registry.expirePolicy(pid); // anyone can call
        assertEq(uint8(registry.stateOf(pid)), uint8(IPolicyRegistry.PolicyState.Expired));
        assertEq(pool.availableCapital(), poolBefore + 1000e6);
    }

    function test_expirePolicy_revertsBeforeExpiresAt() public {
        bytes32 pid = _subscribe(1000e6, 4000);
        vm.warp(targetDate + 1 days); // within grace window
        vm.expectRevert(); // SettlementWindowNotOpen
        registry.expirePolicy(pid);
    }

    // ── quotePolicy ────────────────────────────────────────────────

    function test_quotePolicy_matchesSubscribedPremium() public {
        uint256 quoted = registry.quotePolicy(LOC_SFO, targetDate, 1000e6, THRESHOLD_F, 4000);
        bytes32 pid = _subscribe(1000e6, 4000);
        IPolicyRegistry.Policy memory p = registry.getPolicy(pid);
        assertEq(quoted, p.premium);
    }

    // ── two independent policies ───────────────────────────────────

    function test_twoIndependentPolicies() public {
        address bob = makeAddr("bob");
        usdc.mint(bob, 100_000e6);
        vm.prank(bob);
        usdc.approve(address(registry), type(uint256).max);

        bytes32 pidAlice = _subscribe(1000e6, 4000);
        vm.prank(bob);
        bytes32 pidBob = registry.subscribe(LOC_CHI, targetDate, 500e6, THRESHOLD_F, 2000);

        assertTrue(pidAlice != pidBob);
        assertEq(registry.getPolicy(pidAlice).subscriber, alice);
        assertEq(registry.getPolicy(pidBob).subscriber, bob);
    }
}
