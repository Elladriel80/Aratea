// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

/// @title  IRoundRegistry — external interface of RoundRegistry
/// @notice The on-chain anchor point for the monthly mint rounds described in white paper §7.3.
///         Each round is committed under a `roundHash` derived off-chain, traverses a
///         lifecycle (Proposed → Challenged? → Executed | Cancelled), and on execution
///         mints AUG-POC tokens to ratified beneficiaries. No emission cap is enforced
///         on-chain — quality is guaranteed by the off-chain valuation rubric, the
///         token-weighted vote on individual valuations above 0.01 BTC, the new-entrant
///         cooldown, the slashing mechanism, and the annual audit (white paper §7.7).
interface IRoundRegistry {
    /*//////////////////////////////////////////////////////////////
                                  TYPES
    //////////////////////////////////////////////////////////////*/

    enum RoundStatus {
        None,
        Proposed,
        Challenged,
        Executed,
        Cancelled
    }

    /*//////////////////////////////////////////////////////////////
                                 EVENTS
    //////////////////////////////////////////////////////////////*/

    /// @notice Emitted when a new round is committed by the proposer (a Safe multisig).
    event RoundProposed(
        bytes32 indexed roundHash,
        string ipfsUri,
        uint64 proposedAt,
        uint32 challengeWindow,
        address[] beneficiaries,
        uint256[] amounts
    );

    /// @notice Emitted when anyone formally challenges a Proposed round during its window.
    event RoundChallenged(bytes32 indexed roundHash, address indexed challenger, string reasonIpfsUri);

    /// @notice Emitted when a round is executed: tokens have been minted to all beneficiaries
    ///         and the round is permanently sealed in the `Executed` state.
    event RoundExecuted(bytes32 indexed roundHash, uint64 executedAt, uint256 totalMinted);

    /// @notice Emitted when a round is cancelled by the canceller role (the Safe multisig).
    event RoundCancelled(bytes32 indexed roundHash, address indexed canceller, string reasonIpfsUri);

    /*//////////////////////////////////////////////////////////////
                                ERRORS
    //////////////////////////////////////////////////////////////*/

    error ZeroAddressAdmin();
    error ZeroAddressToken();
    error InvalidRoundHash();
    error RoundAlreadyExists();
    error MismatchedArrays();
    error EmptyBeneficiaries();
    error ZeroAmount(uint256 index);
    error ZeroBeneficiary(uint256 index);
    error InvalidChallengeWindow();
    error RoundNotProposedOrChallenged();
    error RoundNotProposed();
    error RoundNotCancellable();
    error ChallengeWindowNotExpired();
    error ChallengeWindowExpired();

    /*//////////////////////////////////////////////////////////////
                              FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Propose a new round committed under `roundHash`. The hash is computed
    ///         off-chain as `keccak256(abi.encode(beneficiaries, amounts, ipfsUri))` and
    ///         must match a re-computation from the on-chain inputs.
    /// @dev    Caller must hold ROUND_PROPOSER_ROLE (the Safe multisig).
    function proposeRound(
        bytes32 roundHash,
        address[] calldata beneficiaries,
        uint256[] calldata amounts,
        string calldata ipfsUri,
        uint32 challengeWindow
    ) external;

    /// @notice File a formal challenge against a Proposed round during its challenge window,
    ///         moving it to `Challenged` so the permissionless finalization can no longer
    ///         auto-execute it; resolution happens through the MintGovernor's token-weighted vote.
    /// @dev    Phase 2: caller must hold ROUND_CHALLENGER_ROLE (the MintGovernor). Token holders
    ///         challenge through the Governor's public `challenge()`, which opens the vote and then
    ///         calls this. Gating it prevents a stake-free direct challenge from freezing a round
    ///         with no vote to resolve it.
    function challengeRound(
        bytes32 roundHash,
        string calldata reasonIpfsUri
    ) external;

    /// @notice Execute a round whose challenge window has expired. Mints tokens to every
    ///         beneficiary and marks the round Executed.
    /// @dev    Caller must hold ROUND_EXECUTOR_ROLE (the Safe multisig).
    function executeRound(
        bytes32 roundHash
    ) external;

    /// @notice Cancel a Proposed or Challenged round. Permanent — once cancelled the round
    ///         can never be revived.
    /// @dev    Caller must hold ROUND_CANCELLER_ROLE (the Safe multisig).
    function cancelRound(
        bytes32 roundHash,
        string calldata reasonIpfsUri
    ) external;

    /*//////////////////////////////////////////////////////////////
                                 VIEWS
    //////////////////////////////////////////////////////////////*/

    /// @notice Returns the current status of a round.
    function statusOf(
        bytes32 roundHash
    ) external view returns (RoundStatus);
}
