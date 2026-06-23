// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

/// @title  IPricingEngine — interface for the parametric premium calculator
/// @notice Translates a predictor probability p(event) into a USDC premium amount
///         for a given insured sum and horizon, applying actuarial loadings.
///
/// @dev    **Phase 3 scaffolding — pre-implementation.**
///         This interface was designed from the B48 actuarial spec (2026-06-23).
///         Implementation is gated on D-capital (capital model choice) and
///         D-réglementation (legal structure) decisions by Jean-Sébastien.
///
///         Premium formula (B48):
///           premium = p × sumAssured
///                     × (1 + α_frais)            // 0.20 baseline
///                     × (1 + α_solvab)           // 0.15 baseline
///                     + β_adverse × sumAssured   // 0.05 initial; reduces to 0.02 at G2 gate
///
///         Constraints:
///           premium_min  = 5 USDC   (floor, usability)
///           premium_max  = 50% × sumAssured  (solvency cap)
///
/// @notice All amounts are in USDC with 6-decimal precision (1e6 = 1 USDC).
///         Probability is expressed in basis points (0–10 000), so 7 000 = 70%.
interface IPricingEngine {
    /*//////////////////////////////////////////////////////////////
                               ERRORS
    //////////////////////////////////////////////////////////////*/

    /// @notice Probability must be in [0, 10 000] basis points.
    error InvalidProbabilityBps(uint16 pBps);

    /// @notice Sum assured must be > 0.
    error ZeroSumAssured();

    /// @notice Computed premium would exceed the 50% cap relative to sumAssured.
    error PremiumExceedsCap(uint256 premium, uint256 cap);

    /*//////////////////////////////////////////////////////////////
                              FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Compute the USDC premium for a parametric policy.
    /// @param  pBps        Predictor probability of the insured event, in basis points (0–10 000).
    ///                     Supplied off-chain from the learned predictor at subscribe time.
    /// @param  sumAssured  Insured amount in USDC (6 decimals). Maximum payout if event occurs.
    /// @param  daysAhead   Forecast horizon in whole days (1 = same-day, 3 = 3 days forward).
    ///                     Longer horizons carry higher uncertainty and may attract a surcharge.
    /// @return premium     USDC premium amount (6 decimals), clamped to [premium_min, premium_max].
    function quote(
        uint16 pBps,
        uint256 sumAssured,
        uint8 daysAhead
    ) external view returns (uint256 premium);

    /*//////////////////////////////////////////////////////////////
                               VIEWS
    //////////////////////////////////////////////////////////////*/

    /// @notice Returns the expense loading coefficient (α_frais), scaled by 1e4.
    ///         Example: 2 000 = 20%.
    function expenseLoadingBps() external view returns (uint16);

    /// @notice Returns the solvency loading coefficient (α_solvab), scaled by 1e4.
    ///         Example: 1 500 = 15%.
    function solvencyLoadingBps() external view returns (uint16);

    /// @notice Returns the current adverse-selection loading (β_adverse), scaled by 1e4.
    ///         Starts at 500 (5%); reduced to 200 once G2 Brier gate is confirmed.
    function adverseLoadingBps() external view returns (uint16);

    /// @notice Minimum premium floor in USDC (6 decimals). Default: 5_000_000 (5 USDC).
    function premiumMin() external view returns (uint256);
}
