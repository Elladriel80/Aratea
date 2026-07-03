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

// ─── Minimal helpers (shared with Phase3.t.sol, inlined to avoid import cycles) ──

contract MockUSDC2 is MockERC20 {
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

contract MockOracle2 is IWeatherOracle {
    mapping(bytes32 => mapping(uint64 => int16)) private _r;
    mapping(bytes32 => mapping(uint64 => bool)) private _s;

    function setResult(
        bytes32 loc,
        uint64 dt,
        int16 t
    ) external {
        _r[loc][dt] = t;
        _s[loc][dt] = true;
    }

    function getResult(
        bytes32 loc,
        uint64 dt
    ) external view returns (int16, bool) {
        return (_r[loc][dt], _s[loc][dt]);
    }
}

// ─── PremiumPool — missing branch coverage ────────────────────────────────────

contract PremiumPoolCoverageTest is Test {
    PremiumPool pool;
    MockUSDC2 usdc;

    address admin = makeAddr("admin");
    address registry = makeAddr("registry");
    address alice = makeAddr("alice");

    bytes32 constant PID = keccak256("coverage-policy");

    function setUp() public {
        usdc = new MockUSDC2();
        pool = new PremiumPool(admin, address(usdc));
        vm.startPrank(admin);
        pool.grantRole(pool.POLICY_REGISTRY_ROLE(), registry);
        vm.stopPrank();
    }

    function _seed(
        uint256 amount
    ) internal {
        usdc.mint(admin, amount);
        vm.startPrank(admin);
        usdc.approve(address(pool), amount);
        pool.deposit(amount);
        vm.stopPrank();
    }

    // deposit — ZeroAmount revert
    function test_deposit_revertsZeroAmount() public {
        vm.prank(admin);
        vm.expectRevert(IPremiumPool.ZeroAmount.selector);
        pool.deposit(0);
    }

    // withdraw — ZeroAmount revert
    function test_withdraw_revertsZeroAmount() public {
        _seed(300_000e6);
        vm.prank(admin);
        vm.expectRevert(IPremiumPool.ZeroAmount.selector);
        pool.withdraw(0);
    }

    // withdraw — InsufficientAvailableCapital (amount > _availableCapital)
    function test_withdraw_revertsInsufficientCapital() public {
        _seed(300_000e6);
        vm.prank(admin);
        vm.expectRevert(); // InsufficientAvailableCapital
        pool.withdraw(400_000e6);
    }

    // receivePremium — ZeroAmount revert
    function test_receivePremium_revertsZeroAmount() public {
        _seed(200_000e6);
        vm.prank(registry);
        vm.expectRevert(IPremiumPool.ZeroAmount.selector);
        pool.receivePremium(PID, 0);
    }

    // reserveForPolicy — ZeroAmount revert
    function test_reserveForPolicy_revertsZeroAmount() public {
        _seed(300_000e6);
        vm.prank(registry);
        vm.expectRevert(IPremiumPool.ZeroAmount.selector);
        pool.reserveForPolicy(PID, 0);
    }

    // payout — ZeroAmount revert
    function test_payout_revertsZeroAmount() public {
        _seed(300_000e6);
        vm.startPrank(registry);
        pool.reserveForPolicy(PID, 1000e6);
        vm.expectRevert(IPremiumPool.ZeroAmount.selector);
        pool.payout(PID, alice, 0);
        vm.stopPrank();
    }

    // payout — ReserveNotFound (no reserve exists for policy)
    function test_payout_revertsReserveNotFound() public {
        _seed(300_000e6);
        vm.prank(registry);
        vm.expectRevert(); // ReserveNotFound
        pool.payout(PID, alice, 1000e6);
    }

    // payout — PayoutExceedsReserve (amount > reserved)
    function test_payout_revertsExceedsReserve() public {
        _seed(300_000e6);
        vm.startPrank(registry);
        pool.reserveForPolicy(PID, 1000e6);
        vm.expectRevert(); // PayoutExceedsReserve
        pool.payout(PID, alice, 2000e6);
        vm.stopPrank();
    }

    // releaseReserve — ReserveNotFound
    function test_releaseReserve_revertsNotFound() public {
        vm.prank(registry);
        vm.expectRevert(); // ReserveNotFound
        pool.releaseReserve(PID);
    }

    // totalCapital — includes reserved
    function test_totalCapital_includesReserved() public {
        _seed(300_000e6);
        vm.prank(registry);
        pool.reserveForPolicy(PID, 50_000e6);
        // available=250k, reserved=50k → total=300k
        assertEq(pool.totalCapital(), 300_000e6);
    }

    // isSolvent — false when capital below MCR
    function test_isSolvent_falseWhenBelowMCR() public {
        // Pool starts empty → 0 < 200_000e6 MCR floor
        assertFalse(pool.isSolvent());
    }
}

// ─── PolicyRegistry — missing branch coverage ─────────────────────────────────

contract PolicyRegistryCoverageTest is Test {
    PricingEngine engine;
    PremiumPool pool;
    PolicyRegistry reg;
    MockUSDC2 usdc;
    MockOracle2 oracle;

    address admin = makeAddr("admin");
    address keeper = makeAddr("keeper");
    address alice = makeAddr("alice");

    bytes32 constant LOC = keccak256("KXHIGHTSFO");
    uint16 constant THR = 900;

    uint64 targetDate;

    function setUp() public {
        usdc = new MockUSDC2();
        engine = new PricingEngine(admin);
        pool = new PremiumPool(admin, address(usdc));
        oracle = new MockOracle2();
        reg = new PolicyRegistry(admin, address(usdc), address(engine), address(pool), address(oracle));

        vm.startPrank(admin);
        pool.grantRole(pool.POLICY_REGISTRY_ROLE(), address(reg));
        reg.grantRole(reg.KEEPER_ROLE(), keeper);
        reg.setSupportedLocation(LOC, true);
        vm.stopPrank();

        // Seed pool above MCR
        usdc.mint(admin, 250_000e6);
        vm.startPrank(admin);
        usdc.approve(address(pool), 250_000e6);
        pool.deposit(250_000e6);
        vm.stopPrank();

        targetDate = uint64(block.timestamp) + 3 days;

        usdc.mint(alice, 100_000e6);
        vm.prank(alice);
        usdc.approve(address(reg), type(uint256).max);
    }

    function _sub(
        uint256 s,
        uint16 p
    ) internal returns (bytes32) {
        vm.prank(alice);
        return reg.subscribe(LOC, targetDate, s, THR, p);
    }

    // setOracle — admin updates oracle address
    function test_setOracle_updatesOracle() public {
        MockOracle2 oracle2 = new MockOracle2();
        vm.prank(admin);
        reg.setOracle(address(oracle2));
        assertEq(address(reg.oracle()), address(oracle2));
    }

    // setOracle — revert on zero address
    function test_setOracle_revertsZeroAddress() public {
        vm.prank(admin);
        vm.expectRevert(); // ZeroAddress
        reg.setOracle(address(0));
    }

    // subscribe — HorizonTooFar (>365 days ahead)
    function test_subscribe_revertsHorizonTooFar() public {
        uint64 tooFar = uint64(block.timestamp) + 366 days;
        vm.prank(alice);
        vm.expectRevert(); // HorizonTooFar
        reg.subscribe(LOC, tooFar, 1000e6, THR, 4000);
    }

    // settlePolicy — PolicyNotFound
    function test_settlePolicy_revertsNotFound() public {
        vm.prank(keeper);
        vm.expectRevert(); // PolicyNotFound
        reg.settlePolicy(keccak256("nonexistent"));
    }

    // expirePolicy — PolicyNotFound
    function test_expirePolicy_revertsNotFound() public {
        vm.expectRevert(); // PolicyNotFound
        reg.expirePolicy(keccak256("nonexistent"));
    }

    // expirePolicy — AlreadySettled (policy already claimed)
    function test_expirePolicy_revertsAlreadySettled() public {
        bytes32 pid = _sub(1000e6, 4000);
        vm.warp(targetDate);
        oracle.setResult(LOC, targetDate, int16(THR)); // claimed
        vm.prank(keeper);
        reg.settlePolicy(pid);

        vm.warp(targetDate + 5 days); // past expiresAt
        vm.expectRevert(); // AlreadySettled
        reg.expirePolicy(pid);
    }

    // settlePolicy — auto-transition PENDING→ACTIVE then settle
    function test_settlePolicy_autoTransitionPendingToActive() public {
        bytes32 pid = _sub(1000e6, 4000);
        // Warp to exactly activatesAt (still Pending)
        vm.warp(targetDate);
        oracle.setResult(LOC, targetDate, 850); // below threshold → expired
        vm.prank(keeper);
        reg.settlePolicy(pid);
        // Should be Expired (auto-transitioned through Active)
        assertEq(uint8(reg.stateOf(pid)), uint8(IPolicyRegistry.PolicyState.Expired));
    }

    // quotePolicy — targetDate in the past or equal to now → days_ahead=1 (clamp)
    function test_quotePolicy_targetInPastClampsToMinDaysAhead() public {
        // targetDate == now → secondsAhead=0 → daysAhead clamped to MIN_DAYS_AHEAD(1)
        uint256 q = reg.quotePolicy(LOC, uint64(block.timestamp), 1000e6, THR, 3000);
        assertGt(q, 0);
    }

    // setSupportedLocation — disable a location
    function test_setSupportedLocation_canDisable() public {
        bytes32 newLoc = keccak256("KXLOWTCHI");
        vm.prank(admin);
        reg.setSupportedLocation(newLoc, true);
        // Now disable
        vm.prank(admin);
        reg.setSupportedLocation(newLoc, false);
        vm.prank(alice);
        vm.expectRevert(); // UnsupportedLocation
        reg.subscribe(newLoc, targetDate, 1000e6, THR, 3000);
    }
}
