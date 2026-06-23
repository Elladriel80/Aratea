// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

/// @title  IPremiumPool — interface for the parametric insurance capital pool
/// @notice Holds USDC capital from underwriters (Phase 3: initially Jean-Sébastien only —
///         C2 "paramétrique pur" model per D-capital decision), receives premiums from
///         policyholders, reserves capital for active policies, and routes payouts.
///
/// @dev    **Phase 3 scaffolding — pre-implementation.**
///         Designed from the B49 contract schema (2026-06-23).
///         Implementation is gated on D-capital (who provides capital, staker model vs.
///         solo underwriter) and D-réglementation (legal structure) decisions.
///
///         Capital flow:
///           Underwriter  →  deposit(amount)        → pool.balance
///           Subscriber   →  (via PolicyRegistry)   → pool.receivePremium()
///           PolicyActive →  reserveForPolicy()      → pool.reserved
///           Claim        →  payout()               → subscriber
///           Expired      →  releaseReserve()       → pool.available
///           Underwriter  →  withdraw(amount)        ← pool.available (if MCR met)
///
///         Minimum Capital Requirement (MCR):
///           solvencyRatio = available / totalReserved ≥ MCR_BPS (3 000 = 30%)
///           Deposits and withdrawals that would breach MCR are rejected.
///
/// @notice All amounts are in USDC with 6-decimal precision (1e6 = 1 USDC).
interface IPremiumPool {
    /*//////////////////////////////////////////////////////////////
                                EVENTS
    //////////////////////////////////////////////////////////////*/

    /// @notice Capital deposited by an underwriter.
    event CapitalDeposited(address indexed provider, uint256 amount, uint256 newBalance);

    /// @notice Capital withdrawn by an underwriter (only available capital, post-MCR check).
    event CapitalWithdrawn(address indexed provider, uint256 amount, uint256 newBalance);

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
    error SolvencyCheckFailed(uint256 solvencyRatioBps, uint256 minimumBps);
    error ZeroAmount();
    error NotPolicyRegistry();
    error ReserveNotFound(bytes32 policyId);
    error ReserveAlreadyExists(bytes32 policyId);

    /*//////////////////////////////////////////////////////////////
                        CAPITAL PROVIDER FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Deposit USDC into the pool as underwriting capital.
    ///         Increases `availableCapital`. No MCR floor on deposits.
    /// @param  amount  USDC amount (6 decimals). Caller must have approved this contract.
    function deposit(uint256 amount) external;

    /// @notice Withdraw available (unreserved) USDC from the pool.
    ///         Rejected if the withdrawal would breach MCR.
    /// @param  amount  USDC amount (6 decimals).
    function withdraw(uint256 amount) external;

    /*//////////////////////////////////////////////////////////////
                        POLICY REGISTRY FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Called by PolicyRegistry at subscribe time to book premium income.
    ///         Premium is added to availableCapital (it is income, not reserved).
    /// @param  policyId  Caller-managed policy identifier.
    /// @param  amount    Premium in USDC (6 decimals). Transferred from PolicyRegistry.
    function receivePremium(bytes32 policyId, uint256 amount) external;

    /// @notice Called by PolicyRegistry when a policy activates.
    ///         Locks `sumAssured` USDC from available capital as a reserve.
    ///         Reverts if available capital < sumAssured or MCR is breached after reservation.
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

    /// @notice Current solvency ratio in basis points: available / totalReserved × 10 000.
    ///         Returns type(uint256).max when totalReserved == 0 (fully solvent).
    function solvencyRatioBps() external view returns (uint256);

    /// @notice Minimum solvency ratio threshold in basis points (e.g. 3 000 = 30%).
    function mcrBps() external view returns (uint16);
}
