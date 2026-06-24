// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

import {IPricingEngine} from "../interfaces/IPricingEngine.sol";

/// @title  PricingEngine — actuarial premium calculator for Phase 3 parametric policies
/// @notice Implements the formula from B48 design spec (2026-06-23):
///         premium = p × S × (1 + α_frais) × (1 + α_solvab) + β_adverse × S
///         Clamped to [PREMIUM_MIN, 50% × sumAssured].
///
///         Default loadings:
///           α_frais   = 20%  (expense loading)
///           α_solvab  = 15%  (solvency loading)
///           β_adverse =  5%  (adverse-selection; reduced to 2% once G2 gate is confirmed)
///         Horizon surcharge: +5% per extra day beyond day 1.
///
///         All amounts in USDC with 6-decimal precision (1e6 = 1 USDC).
contract PricingEngine is IPricingEngine {
    /*//////////////////////////////////////////////////////////////
                               CONSTANTS
    //////////////////////////////////////////////////////////////*/

    uint16  public constant DEFAULT_EXPENSE_BPS   = 2_000; // 20 %
    uint16  public constant DEFAULT_SOLVENCY_BPS  = 1_500; // 15 %
    uint16  public constant DEFAULT_ADVERSE_BPS   = 500;   //  5 % (initial; → 200 at G2 gate)
    uint256 public constant PREMIUM_MIN           = 5_000_000; // 5 USDC (6 decimals)
    uint256 private constant BPS                  = 10_000;
    uint16  private constant MAX_ADVERSE_BPS      = 1_000; // hard cap: 10 %
    uint8   private constant HORIZON_SURCHARGE_PCT = 5;    // +5 % per extra day

    /*//////////////////////////////////////////////////////////////
                                STORAGE
    //////////////////////////////////////////////////////////////*/

    address public immutable admin;

    uint16 private _expenseLoadingBps;
    uint16 private _solvencyLoadingBps;
    uint16 private _adverseLoadingBps;

    /*//////////////////////////////////////////////////////////////
                                EVENTS
    //////////////////////////////////////////////////////////////*/

    event AdverseLoadingUpdated(uint16 oldBps, uint16 newBps);

    /*//////////////////////////////////////////////////////////////
                                ERRORS
    //////////////////////////////////////////////////////////////*/

    error NotAdmin();
    error AdverseLoadingTooHigh(uint16 provided, uint16 maxAllowed);
    error ZeroAddress();

    /*//////////////////////////////////////////////////////////////
                             CONSTRUCTOR
    //////////////////////////////////////////////////////////////*/

    constructor(address admin_) {
        if (admin_ == address(0)) revert ZeroAddress();
        admin                = admin_;
        _expenseLoadingBps   = DEFAULT_EXPENSE_BPS;
        _solvencyLoadingBps  = DEFAULT_SOLVENCY_BPS;
        _adverseLoadingBps   = DEFAULT_ADVERSE_BPS;
    }

    /*//////////////////////////////////////////////////////////////
                           ADMIN FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Reduce adverse-selection loading once G2 Brier gate is confirmed.
    ///         Typical: 500 → 200 (5% → 2%).
    function setAdverseLoading(uint16 bps) external {
        if (msg.sender != admin) revert NotAdmin();
        if (bps > MAX_ADVERSE_BPS) revert AdverseLoadingTooHigh(bps, MAX_ADVERSE_BPS);
        emit AdverseLoadingUpdated(_adverseLoadingBps, bps);
        _adverseLoadingBps = bps;
    }

    /*//////////////////////////////////////////////////////////////
                              PRICING
    //////////////////////////////////////////////////////////////*/

    /// @inheritdoc IPricingEngine
    /// @dev Formula (all in USDC 6-decimal precision):
    ///      1. expectedLoss = pBps × sumAssured / 10 000
    ///      2. loaded = expectedLoss × (1 + α_frais) × (1 + α_solvab)
    ///      3. adversePremium = β_adverse × sumAssured / 10 000
    ///      4. horizonSurcharge = loaded × 5% × (daysAhead - 1)
    ///      5. premium = loaded + adversePremium + horizonSurcharge
    ///      6. clamp to [PREMIUM_MIN, sumAssured / 2]
    function quote(
        uint16  pBps,
        uint256 sumAssured,
        uint8   daysAhead
    ) external view returns (uint256 premium) {
        if (pBps > BPS) revert InvalidProbabilityBps(pBps);
        if (sumAssured == 0) revert ZeroSumAssured();

        // Step 1: pure expected loss
        uint256 expectedLoss = (uint256(pBps) * sumAssured) / BPS;

        // Step 2: actuarial loadings
        uint256 loaded = expectedLoss
            * (BPS + _expenseLoadingBps) / BPS
            * (BPS + _solvencyLoadingBps) / BPS;

        // Step 3: adverse-selection floor
        uint256 adverseComponent = (uint256(_adverseLoadingBps) * sumAssured) / BPS;

        // Step 4: horizon surcharge (+5 % per extra day beyond day 1)
        uint256 horizonSurcharge = daysAhead > 1
            ? (loaded * HORIZON_SURCHARGE_PCT * uint256(daysAhead - 1)) / 100
            : 0;

        // Step 5: total
        premium = loaded + adverseComponent + horizonSurcharge;

        // Step 6: clamp
        uint256 cap = sumAssured / 2;
        if (premium > cap) premium = cap;
        if (premium < PREMIUM_MIN) premium = PREMIUM_MIN;
    }

    /*//////////////////////////////////////////////////////////////
                               VIEWS
    //////////////////////////////////////////////////////////////*/

    /// @inheritdoc IPricingEngine
    function expenseLoadingBps() external view returns (uint16) {
        return _expenseLoadingBps;
    }

    /// @inheritdoc IPricingEngine
    function solvencyLoadingBps() external view returns (uint16) {
        return _solvencyLoadingBps;
    }

    /// @inheritdoc IPricingEngine
    function adverseLoadingBps() external view returns (uint16) {
        return _adverseLoadingBps;
    }

    /// @inheritdoc IPricingEngine
    function premiumMin() external pure returns (uint256) {
        return PREMIUM_MIN;
    }
}
