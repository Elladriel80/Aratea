// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

/// @title  IPremiumPool — interface for the parametric insurance reserve pool
/// @notice Holds the association's USDC reserves (premiums collected + initial capital),
///         reserves funds for active policies, and routes payouts on claim events.
///
/// @dev    **Phase 3 scaffolding — pre-implementation.**
///         Designed from B49 (2026-06-23), updated per D-capital decision (2026-06-24).
///
///         Legal structure: Association à but lucratif loi Alsace-Moselle.
///         Members = token holders. No external underwriting stakers.
///         Solvency model: reserves built up from collected premiums + initial capital
///         injection by the association admin to meet the MCR floor (200 000 €,
///         Art. R334-6 Code des assurances, simplified regime under 5M€/year).
///
///         Capital flow:
///           Association admin  →  deposit(amount)          → pool.availableCapital
///           Subscriber         →  (via PolicyRegistry)     → pool.receivePremium()
///           PolicyActive       →  reserveForPolicy()        → pool.reserved
///           Claim event        →  payout()                 → subscriber
///           Policy expired     →  releaseReserve()         → pool.available
///           Admin              →  withdraw(amount)          ← pool.available (if MCR met)
///
///         Minimum Capital Requirement (MCR — Art. R334-6 CA simplified regime):
///           Required margin = max(200_000 USDC, max(18% × annual_premiums,
///                                                    26% × avg_3yr_claims))
///           availableCapital must remain ≥ required_margin at all times.
///           New subscriptions are rejected if pool is below MCR floor.
///
/// @notice All amounts are in USDC with 6-decimal precision (1e6 = 1 USDC).
interface IPremiumPool {
    /*//////////////////////////////////////////////////////////////
                                EVENTS
    //////////////////////////////////////////////////////////////*/

    /// @notice Capital deposited by the association admin to fund the pool.
    event CapitalDeposited(address indexed admin, uint256 amount, uint256 newBalance);

    /// @notice Capital withdrawn by the association admin (only surplus above MCR).
    event CapitalWithdrawn(address indexed admin, uint256 amount, uint256 newBalance);

    /// @notice Premium received from a subscriber (via PolicyRegistry).
    event PremiumReceived(bytes32 indexed policyId, uint256 amount);

    /// @notice Capital reserved for an active policy (locked until settled).
    event CapitalReserved(bytes32 indexed policyId, uint256 sumAssured);

    /// @notice Payout sent to a subscriber after a claim event.
    event PayoutSent(bytes32 indexed policyId, address indexed subscriber, uint256 amount);

    /// @notice Reserved capital released back to available pool (on policy expiry).
    event ReserveReleased(bytes32 indexed policyId, uint256 sumAssured);

    /*//////////////////////////////////////////////////////////////
                                ERRORS
    //////////////////////////////////////////////////////////////*/

    error InsufficientAvailableCapital(uint256 requested, uint256 available);
    /// @dev Emitted when an operation would breach the MCR floor.
    error SolvencyCheckFailed(uint256 availableBps, uint256 mcrFloorUsdc);
    error ZeroAmount();
    error NotPolicyRegistry();
    error NotAdmin();
    error ReserveNotFound(bytes32 policyId);
    error ReserveAlreadyExists(bytes32 policyId);
    /// @dev Emitted at subscribe time if pool solvency is below MCR floor.
    error PoolBelowMCR(uint256 availableCapital, uint256 mcrFloor);

    /*//////////////////////////////////////////////////////////////
                        ASSOCIATION ADMIN FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Deposit USDC into the pool as association capital.
    ///         Used to meet or top up the MCR floor before accepting subscriptions.
    ///         Only callable by the association admin (ADMIN_ROLE).
    /// @param  amount  USDC amount (6 decimals). Caller must have approved this contract.
    function deposit(uint256 amount) external;

    /// @notice Withdraw surplus capital above the MCR floor.
    ///         Rejected if the remaining balance would breach the MCR.
    ///         Only callable by the association admin (ADMIN_ROLE).
    /// @param  amount  USDC amount (6 decimals).
    function withdraw(uint256 amount) external;

    /*//////////////////////////////////////////////////////////////
                        POLICY REGISTRY FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Called by PolicyRegistry at subscribe time to book premium income.
    ///         Reverts with PoolBelowMCR if availableCapital < mcrFloor before booking.
    ///         Premium added to availableCapital after MCR check passes.
    /// @param  policyId  Caller-managed policy identifier.
    /// @param  amount    Premium in USDC (6 decimals). Transferred from PolicyRegistry.
    function receivePremium(bytes32 policyId, uint256 amount) external;

    /// @notice Called by PolicyRegistry when a policy activates.
    ///         Locks `sumAssured` USDC from available capital as a reserve.
    ///         Reverts if available capital < sumAssured.
    /// @param  policyId   Policy identifier.
    /// @param  sumAssured Amount to reserve in USDC (6 decimals).
    function reserveForPolicy(bytes32 policyId, uint256 sumAssured) external;

    /// @notice Called by PolicyRegistry on a successful claim.
    ///         Transfers `amount` USDC from the reserve to `subscriber` and closes the reserve.
    /// @param  policyId    Policy identifier (must have an existing reserve).
    /// @param  subscriber  Recipient of the payout.
    /// @param  amount      Payout in USDC (6 decimals); must be ≤ reserved amount.
    function payout(bytes32 policyId, address subscriber, uint256 amount) external;

    /// @notice Called by PolicyRegistry when a policy expires without a claim.
    ///         Releases reserved capital back to availableCapital.
    /// @param  policyId  Policy identifier (must have an existing reserve).
    function releaseReserve(bytes32 policyId) external;

    /*//////////////////////////////////////////////////////////////
                             VIEW FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Total USDC balance of the pool (available + reserved).
    function totalCapital() external view returns (uint256);

    /// @notice USDC available for new reservations or withdrawals.
    function availableCapital() external view returns (uint256);

    /// @notice USDC locked as reserves for active policies.
    function totalReserved() external view returns (uint256);

    /// @notice Reserved amount for a specific policy (0 if not reserved).
    function reservedForPolicy(bytes32 policyId) external view returns (uint256);

    /// @notice MCR floor in USDC: minimum required availableCapital at all times.
    ///         Computed from regulatory formula (Art. R334-6 CA) or set by admin.
    ///         Floor = max(200_000e6, max(18% × annual_premiums, 26% × avg_claims)).
    function mcrFloor() external view returns (uint256);

    /// @notice Annual premiums collected (used for MCR computation).
    function annualPremiumsCollected() external view returns (uint256);

    /// @notice Whether the pool currently meets its MCR floor.
    function isSolvent() external view returns (bool);
}
