// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

/// @title  IPolicyRegistry — interface for parametric weather policy lifecycle
/// @notice Manages the full lifecycle of a parametric insurance policy:
///         subscriber pays premium → policy activates → oracle settles →
///         payout triggered automatically if temperature threshold is crossed.
///
/// @dev    **Phase 3 scaffolding — pre-implementation.**
///         Designed from the B49 contract schema (2026-06-23).
///         Implementation is gated on D-capital (capital model) and
///         D-réglementation (legal structure) decisions.
///
///         Lifecycle: PENDING → ACTIVE → CLAIMED | EXPIRED
///           PENDING  : premium received, waiting for targetDate window
///           ACTIVE   : within the insured period, oracle may trigger
///           CLAIMED  : event occurred, payout sent, terminal state
///           EXPIRED  : targetDate passed without event, terminal state
///
///         Settlement: uses the existing `ReclaimWeatherSource` oracle (Phase 1+2)
///         to read the confirmed temperature. The keeper calls `settlePolicy()`
///         after the oracle result is available. Auto-payout if T ≥ threshold.
///
/// @notice All amounts are in USDC with 6-decimal precision (1e6 = 1 USDC).
interface IPolicyRegistry {
    /*//////////////////////////////////////////////////////////////
                                TYPES
    //////////////////////////////////////////////////////////////*/

    enum PolicyState {
        None, // does not exist
        Pending, // premium paid, waiting for insured period
        Active, // insured period live
        Claimed, // event triggered payout — terminal
        Expired // period ended without event — terminal
    }

    /// @param policyId          keccak256 of (subscriber, locationKey, targetDate, nonce)
    /// @param subscriber        address that paid the premium
    /// @param sumAssured        maximum payout in USDC (6 decimals)
    /// @param premium           actual premium paid in USDC (6 decimals)
    /// @param triggerThresholdF temperature threshold in °F × 10 (e.g. 900 = 90.0 °F)
    /// @param locationKey       station identifier matching ReclaimWeatherSource (e.g. "KXHIGHTSFO")
    /// @param targetDate        UNIX timestamp of the target settlement day (midnight UTC)
    /// @param activatesAt       UNIX timestamp from which the oracle may settle
    /// @param expiresAt         UNIX timestamp after which the policy expires if unsettled
    /// @param state             current lifecycle state
    struct Policy {
        bytes32 policyId;
        address subscriber;
        uint256 sumAssured;
        uint256 premium;
        uint16 triggerThresholdF;
        bytes32 locationKey;
        uint64 targetDate;
        uint64 activatesAt;
        uint64 expiresAt;
        PolicyState state;
    }

    /*//////////////////////////////////////////////////////////////
                                EVENTS
    //////////////////////////////////////////////////////////////*/

    /// @notice Subscriber pays premium; policy enters PENDING state.
    event PolicySubscribed(
        bytes32 indexed policyId,
        address indexed subscriber,
        bytes32 locationKey,
        uint64 targetDate,
        uint256 sumAssured,
        uint256 premium
    );

    /// @notice Policy transitions PENDING → ACTIVE (insured period begins).
    event PolicyActivated(bytes32 indexed policyId, uint64 activatedAt);

    /// @notice Oracle confirmed event; payout sent; policy → CLAIMED.
    event PolicyClaimed(
        bytes32 indexed policyId, address indexed subscriber, uint256 payoutAmount, int16 observedTempF
    );

    /// @notice Period ended without event; premium retained; policy → EXPIRED.
    event PolicyExpired(bytes32 indexed policyId, uint64 expiredAt);

    /*//////////////////////////////////////////////////////////////
                                ERRORS
    //////////////////////////////////////////////////////////////*/

    error PolicyNotFound(bytes32 policyId);
    error PolicyNotInState(bytes32 policyId, PolicyState expected, PolicyState actual);
    error PremiumInsufficient(uint256 required, uint256 provided);
    error TargetDateInPast(uint64 targetDate, uint64 now_);
    error SettlementWindowNotOpen(bytes32 policyId);
    error AlreadySettled(bytes32 policyId);
    error SolvencyCheckFailed(uint256 solvencyRatioBps, uint256 minimumBps);
    error ZeroSumAssured();
    error UnsupportedLocation(bytes32 locationKey);

    /*//////////////////////////////////////////////////////////////
                            WRITE FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Subscribe to a parametric weather policy.
    ///         Caller transfers `premium` USDC; the pool reserves `sumAssured`.
    ///         Premium is derived from IPricingEngine.quote(pBps, sumAssured, daysAhead).
    /// @param  locationKey         Station key (must be in oracle's supported set).
    /// @param  targetDate          Settlement day as UNIX timestamp (midnight UTC).
    /// @param  sumAssured          Maximum payout in USDC (6 decimals).
    /// @param  triggerThresholdF   Temperature threshold in °F × 10 (e.g. 900 = 90.0 °F).
    /// @param  pBps                Predictor probability at subscription time (0–10 000 bps).
    ///                             Must be supplied by the frontend; verified off-chain for now.
    /// @return policyId            Unique identifier for the new policy.
    function subscribe(
        bytes32 locationKey,
        uint64 targetDate,
        uint256 sumAssured,
        uint16 triggerThresholdF,
        uint16 pBps
    ) external returns (bytes32 policyId);

    /// @notice Transition an ACTIVE policy to CLAIMED if the oracle temperature
    ///         meets or exceeds the threshold; otherwise to EXPIRED.
    ///         Can only be called after `activatesAt` and before `expiresAt + grace`.
    /// @dev    Caller is the keeper (KeeperSettlePolicy.s.sol). Pulls the oracle
    ///         result from `ReclaimWeatherSource.getResult(locationKey, targetDate)`.
    /// @param  policyId  Policy to settle.
    function settlePolicy(
        bytes32 policyId
    ) external;

    /// @notice Expire a policy whose `expiresAt` has passed and has not been settled.
    ///         Safe to call by anyone (permissionless clean-up).
    /// @param  policyId  Policy to expire.
    function expirePolicy(
        bytes32 policyId
    ) external;

    /*//////////////////////////////////////////////////////////////
                             VIEW FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Returns the full Policy struct for a given policyId.
    function getPolicy(
        bytes32 policyId
    ) external view returns (Policy memory);

    /// @notice Returns the current state of a policy.
    function stateOf(
        bytes32 policyId
    ) external view returns (PolicyState);

    /// @notice Compute the premium quote without creating a policy.
    ///         Delegates to IPricingEngine.quote(pBps, sumAssured, daysAhead).
    function quotePolicy(
        bytes32 locationKey,
        uint64 targetDate,
        uint256 sumAssured,
        uint16 triggerThresholdF,
        uint16 pBps
    ) external view returns (uint256 premium);
}
