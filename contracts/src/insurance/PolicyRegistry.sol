// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

import {IPolicyRegistry} from "../interfaces/IPolicyRegistry.sol";
import {IPremiumPool} from "../interfaces/IPremiumPool.sol";
import {IPricingEngine} from "../interfaces/IPricingEngine.sol";
import {IWeatherOracle} from "../interfaces/IWeatherOracle.sol";

/// @title  PolicyRegistry — parametric weather policy lifecycle for Phase 3
/// @notice Manages the full lifecycle of on-chain parametric insurance policies:
///         subscriber pays USDC premium → reserve locked in PremiumPool →
///         keeper settles via oracle → payout if T ≥ threshold, else premium retained.
///
///         Lifecycle:
///           subscribe()     → PENDING  (premium transferred, sumAssured reserved)
///           settlePolicy()  → PENDING/ACTIVE → CLAIMED | EXPIRED  (keeper + oracle)
///           expirePolicy()  → PENDING/ACTIVE → EXPIRED  (permissionless, after expiresAt)
///
///         State mapping:
///           PENDING  = premium paid, before activatesAt (= targetDate)
///           ACTIVE   = after activatesAt, awaiting oracle settlement
///           CLAIMED  = oracle confirmed event (T ≥ threshold), payout sent
///           EXPIRED  = no event confirmed before expiresAt + grace, premium retained
///
///         All amounts in USDC (6-decimal precision, 1e6 = 1 USDC).
contract PolicyRegistry is AccessControl, ReentrancyGuard, IPolicyRegistry {
    using SafeERC20 for IERC20;

    /*//////////////////////////////////////////////////////////////
                                 ROLES
    //////////////////////////////////////////////////////////////*/

    /// @notice Keeper role — authorised to call settlePolicy() after activatesAt.
    bytes32 public constant KEEPER_ROLE = keccak256("KEEPER_ROLE");

    /*//////////////////////////////////////////////////////////////
                               CONSTANTS
    //////////////////////////////////////////////////////////////*/

    /// @dev Grace period after targetDate during which the oracle may post a result.
    uint64 private constant SETTLEMENT_GRACE = 2 days;
    /// @dev Minimum days ahead (same-day is still at least 1 in the pricing formula).
    uint8 private constant MIN_DAYS_AHEAD = 1;
    /// @dev Maximum subscription horizon (1 year).
    uint64 private constant MAX_SUBSCRIPTION_HORIZON = 365 days;

    /*//////////////////////////////////////////////////////////////
                                STORAGE
    //////////////////////////////////////////////////////////////*/

    IERC20 public immutable usdc;
    IPricingEngine public immutable pricingEngine;
    IPremiumPool public immutable pool;
    IWeatherOracle public oracle; // updatable by admin for oracle upgrades

    mapping(bytes32 => Policy) private _policies;
    mapping(address => uint256) private _nonces;
    mapping(bytes32 => bool) private _supportedLocations;

    /*//////////////////////////////////////////////////////////////
                                ERRORS
    //////////////////////////////////////////////////////////////*/

    error ZeroAddress();
    error HorizonTooFar(uint64 targetDate, uint64 maxDate);

    /*//////////////////////////////////////////////////////////////
                             CONSTRUCTOR
    //////////////////////////////////////////////////////////////*/

    constructor(
        address admin_,
        address usdc_,
        address pricingEngine_,
        address pool_,
        address oracle_
    ) {
        if (
            admin_ == address(0) || usdc_ == address(0) || pricingEngine_ == address(0) || pool_ == address(0)
                || oracle_ == address(0)
        ) revert ZeroAddress();

        _grantRole(DEFAULT_ADMIN_ROLE, admin_);
        usdc = IERC20(usdc_);
        pricingEngine = IPricingEngine(pricingEngine_);
        pool = IPremiumPool(pool_);
        oracle = IWeatherOracle(oracle_);
    }

    /*//////////////////////////////////////////////////////////////
                           ADMIN FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Update oracle address (admin only — for oracle contract upgrades).
    function setOracle(
        address oracle_
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (oracle_ == address(0)) revert ZeroAddress();
        oracle = IWeatherOracle(oracle_);
    }

    /// @notice Enable or disable a location key for subscriptions.
    function setSupportedLocation(
        bytes32 locationKey,
        bool supported
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _supportedLocations[locationKey] = supported;
    }

    /*//////////////////////////////////////////////////////////////
                         SUBSCRIBER FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @inheritdoc IPolicyRegistry
    /// @dev Flow:
    ///      1. Validate inputs (location, date, sumAssured).
    ///      2. Quote premium via PricingEngine.
    ///      3. Transfer USDC from subscriber to PremiumPool directly.
    ///      4. Notify PremiumPool of the premium (MCR check + accounting).
    ///      5. Reserve sumAssured in PremiumPool.
    ///      6. Persist policy and emit events.
    function subscribe(
        bytes32 locationKey,
        uint64 targetDate,
        uint256 sumAssured,
        uint16 triggerThresholdF,
        uint16 pBps
    ) external nonReentrant returns (bytes32 policyId) {
        if (!_supportedLocations[locationKey]) revert UnsupportedLocation(locationKey);
        if (sumAssured == 0) revert ZeroSumAssured();
        uint64 now_ = uint64(block.timestamp);
        if (targetDate <= now_) revert TargetDateInPast(targetDate, now_);
        uint64 maxDate = now_ + MAX_SUBSCRIPTION_HORIZON;
        if (targetDate > maxDate) revert HorizonTooFar(targetDate, maxDate);

        // Compute daysAhead for pricing (clamped to uint8 range, safe given MAX_HORIZON)
        uint64 secondsAhead = targetDate - now_;
        uint8 daysAhead = uint8(_clampToUint8(secondsAhead / 1 days + MIN_DAYS_AHEAD));

        uint256 premium = pricingEngine.quote(pBps, sumAssured, daysAhead);
        // Defensive guard only: quote() clamps to PREMIUM_MIN (> 0), so premium
        // can never be 0 unless the engine is swapped for a broken one.
        // slither-disable-next-line incorrect-equality
        if (premium == 0) revert PremiumInsufficient(1, 0); // guard (should never happen)

        // Unique policy id
        uint256 nonce = _nonces[msg.sender]++;
        policyId = keccak256(abi.encode(msg.sender, locationKey, targetDate, nonce));

        // Transfer USDC from subscriber directly to PremiumPool
        usdc.safeTransferFrom(msg.sender, address(pool), premium);
        // PremiumPool books the premium (accounting only, MCR gate)
        pool.receivePremium(policyId, premium);
        // Lock sumAssured as reserve for the policy
        pool.reserveForPolicy(policyId, sumAssured);

        Policy storage p = _policies[policyId];
        p.policyId = policyId;
        p.subscriber = msg.sender;
        p.sumAssured = sumAssured;
        p.premium = premium;
        p.triggerThresholdF = triggerThresholdF;
        p.locationKey = locationKey;
        p.targetDate = targetDate;
        p.activatesAt = targetDate; // oracle can settle from targetDate
        p.expiresAt = targetDate + SETTLEMENT_GRACE;
        p.state = PolicyState.Pending;

        emit PolicySubscribed(policyId, msg.sender, locationKey, targetDate, sumAssured, premium);
    }

    /*//////////////////////////////////////////////////////////////
                           KEEPER FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @inheritdoc IPolicyRegistry
    /// @dev Keeper calls this once the oracle result is available.
    ///      Transitions: PENDING/ACTIVE → CLAIMED | EXPIRED.
    function settlePolicy(
        bytes32 policyId
    ) external onlyRole(KEEPER_ROLE) nonReentrant {
        Policy storage p = _policies[policyId];
        if (p.subscriber == address(0)) revert PolicyNotFound(policyId);
        PolicyState state = p.state;
        if (state != PolicyState.Pending && state != PolicyState.Active) {
            revert AlreadySettled(policyId);
        }

        uint64 now_ = uint64(block.timestamp);
        if (now_ < p.activatesAt) revert SettlementWindowNotOpen(policyId);
        if (now_ > p.expiresAt) revert SettlementWindowNotOpen(policyId);

        // Auto-transition PENDING → ACTIVE when activatesAt has passed
        if (state == PolicyState.Pending) {
            p.state = PolicyState.Active;
            emit PolicyActivated(policyId, now_);
        }

        // Query oracle
        (int16 observedTempF, bool settled) = oracle.getResult(p.locationKey, p.targetDate);
        if (!settled) revert SettlementWindowNotOpen(policyId);

        // Trigger condition: observed temperature (°F × 10) ≥ threshold (°F × 10)
        if (observedTempF >= int16(p.triggerThresholdF)) {
            p.state = PolicyState.Claimed;
            pool.payout(policyId, p.subscriber, p.sumAssured);
            emit PolicyClaimed(policyId, p.subscriber, p.sumAssured, observedTempF);
        } else {
            p.state = PolicyState.Expired;
            pool.releaseReserve(policyId);
            emit PolicyExpired(policyId, now_);
        }
    }

    /*//////////////////////////////////////////////////////////////
                        PERMISSIONLESS FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @inheritdoc IPolicyRegistry
    /// @dev Safe clean-up: anyone can expire a policy after the grace period.
    function expirePolicy(
        bytes32 policyId
    ) external nonReentrant {
        Policy storage p = _policies[policyId];
        if (p.subscriber == address(0)) revert PolicyNotFound(policyId);
        PolicyState state = p.state;
        if (state != PolicyState.Pending && state != PolicyState.Active) {
            revert AlreadySettled(policyId);
        }
        uint64 now_ = uint64(block.timestamp);
        if (now_ <= p.expiresAt) revert SettlementWindowNotOpen(policyId);

        p.state = PolicyState.Expired;
        pool.releaseReserve(policyId);
        emit PolicyExpired(policyId, now_);
    }

    /*//////////////////////////////////////////////////////////////
                             VIEW FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @inheritdoc IPolicyRegistry
    function getPolicy(
        bytes32 policyId
    ) external view returns (Policy memory) {
        return _policies[policyId];
    }

    /// @inheritdoc IPolicyRegistry
    function stateOf(
        bytes32 policyId
    ) external view returns (PolicyState) {
        return _policies[policyId].state;
    }

    /// @inheritdoc IPolicyRegistry
    function quotePolicy(
        bytes32, /* locationKey — not used in pricing formula, kept for API symmetry */
        uint64 targetDate,
        uint256 sumAssured,
        uint16, /* triggerThresholdF — not used in pricing, kept for API symmetry */
        uint16 pBps
    ) external view returns (uint256 premium) {
        if (sumAssured == 0) revert ZeroSumAssured();
        uint64 now_ = uint64(block.timestamp);
        uint64 ahead = targetDate > now_ ? targetDate - now_ : 0;
        uint8 daysAhead = uint8(_clampToUint8(ahead / 1 days + MIN_DAYS_AHEAD));
        return pricingEngine.quote(pBps, sumAssured, daysAhead);
    }

    /*//////////////////////////////////////////////////////////////
                              HELPERS
    //////////////////////////////////////////////////////////////*/

    function _clampToUint8(
        uint64 v
    ) private pure returns (uint64) {
        return v > 255 ? 255 : v;
    }
}
