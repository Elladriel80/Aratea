// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

import {IAugPocToken} from "../interfaces/IAugPocToken.sol";
import {IRoundRegistry} from "../interfaces/IRoundRegistry.sol";

/// @title  RoundRegistry — on-chain lifecycle for the Aratea monthly mint rounds
/// @notice Implements the propose / challenge / execute / cancel state machine described
///         in `contracts/docs/ROUND-LIFECYCLE.md` and white paper §7.3. The registry holds
///         no funds; on `executeRound` it instructs `AugPocToken` to mint to ratified
///         beneficiaries. No emission cap is enforced on-chain — the Aratea token is not
///         designed to be traded on secondary markets and no per-supply cap is needed to
///         protect a price. Quality is guaranteed off-chain by the valuation rubric, the
///         token-weighted vote on valuations above 0.01 BTC, the new-entrant cooldown, the
///         slashing mechanism, and the annual audit (white paper §7.7).
contract RoundRegistry is AccessControl, ReentrancyGuard, IRoundRegistry {
    /*//////////////////////////////////////////////////////////////
                                 ROLES
    //////////////////////////////////////////////////////////////*/

    bytes32 public constant ROUND_PROPOSER_ROLE = keccak256("ROUND_PROPOSER_ROLE");
    bytes32 public constant ROUND_EXECUTOR_ROLE = keccak256("ROUND_EXECUTOR_ROLE");
    bytes32 public constant ROUND_CANCELLER_ROLE = keccak256("ROUND_CANCELLER_ROLE");

    /*//////////////////////////////////////////////////////////////
                              CONSTANTS
    //////////////////////////////////////////////////////////////*/

    uint32 public constant MIN_CHALLENGE_WINDOW_DAYS = 1;
    uint32 public constant MAX_CHALLENGE_WINDOW_DAYS = 365;

    /*//////////////////////////////////////////////////////////////
                               STORAGE
    //////////////////////////////////////////////////////////////*/

    /// @notice The AUG-POC token the registry mints into. Immutable for the registry's lifetime.
    IAugPocToken public immutable token;

    struct Round {
        string ipfsUri;
        uint64 proposedAt;
        uint32 challengeWindowDays;
        RoundStatus status;
        address[] beneficiaries;
        uint256[] amounts;
    }

    mapping(bytes32 => Round) private _rounds;

    /*//////////////////////////////////////////////////////////////
                              CONSTRUCTOR
    //////////////////////////////////////////////////////////////*/

    constructor(
        address admin,
        IAugPocToken token_
    ) {
        if (admin == address(0)) revert ZeroAddressAdmin();
        if (address(token_) == address(0)) revert ZeroAddressToken();
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        token = token_;
    }

    /*//////////////////////////////////////////////////////////////
                             LIFECYCLE
    //////////////////////////////////////////////////////////////*/

    /// @inheritdoc IRoundRegistry
    function proposeRound(
        bytes32 roundHash,
        address[] calldata beneficiaries,
        uint256[] calldata amounts,
        string calldata ipfsUri,
        uint32 challengeWindowDays
    ) external onlyRole(ROUND_PROPOSER_ROLE) {
        if (beneficiaries.length == 0) revert EmptyBeneficiaries();
        if (beneficiaries.length != amounts.length) revert MismatchedArrays();
        if (challengeWindowDays < MIN_CHALLENGE_WINDOW_DAYS || challengeWindowDays > MAX_CHALLENGE_WINDOW_DAYS) {
            revert InvalidChallengeWindow();
        }

        bytes32 expectedHash = keccak256(abi.encode(beneficiaries, amounts, ipfsUri));
        if (roundHash != expectedHash) revert InvalidRoundHash();

        if (_rounds[roundHash].proposedAt != 0) revert RoundAlreadyExists();

        for (uint256 i = 0; i < beneficiaries.length; i++) {
            if (beneficiaries[i] == address(0)) revert ZeroBeneficiary(i);
            if (amounts[i] == 0) revert ZeroAmount(i);
        }

        Round storage r = _rounds[roundHash];
        r.ipfsUri = ipfsUri;
        r.proposedAt = uint64(block.timestamp);
        r.challengeWindowDays = challengeWindowDays;
        r.status = RoundStatus.Proposed;
        r.beneficiaries = beneficiaries;
        r.amounts = amounts;

        emit RoundProposed(roundHash, ipfsUri, uint64(block.timestamp), challengeWindowDays, beneficiaries, amounts);
    }

    /// @inheritdoc IRoundRegistry
    function challengeRound(
        bytes32 roundHash,
        string calldata reasonIpfsUri
    ) external {
        Round storage r = _rounds[roundHash];
        if (r.status != RoundStatus.Proposed) revert RoundNotProposed();
        if (block.timestamp >= _windowEnd(r)) revert ChallengeWindowExpired();

        r.status = RoundStatus.Challenged;
        emit RoundChallenged(roundHash, msg.sender, reasonIpfsUri);
    }

    /// @inheritdoc IRoundRegistry
    function executeRound(
        bytes32 roundHash
    ) external onlyRole(ROUND_EXECUTOR_ROLE) nonReentrant {
        Round storage r = _rounds[roundHash];
        if (r.status != RoundStatus.Proposed && r.status != RoundStatus.Challenged) {
            revert RoundNotProposedOrChallenged();
        }
        if (block.timestamp < _windowEnd(r)) revert ChallengeWindowNotExpired();

        uint256 totalMint;
        for (uint256 i = 0; i < r.amounts.length; i++) {
            totalMint += r.amounts[i];
        }

        r.status = RoundStatus.Executed;

        // Effects → Interactions: the status change is committed BEFORE any mint call.
        // Token.mint() in OpenZeppelin v5 does not call back into the recipient, so
        // reentrancy is structurally impossible; nonReentrant is defense-in-depth.
        for (uint256 i = 0; i < r.beneficiaries.length; i++) {
            token.mint(r.beneficiaries[i], r.amounts[i]);
        }

        emit RoundExecuted(roundHash, uint64(block.timestamp), totalMint);
    }

    /// @inheritdoc IRoundRegistry
    function cancelRound(
        bytes32 roundHash,
        string calldata reasonIpfsUri
    ) external onlyRole(ROUND_CANCELLER_ROLE) {
        Round storage r = _rounds[roundHash];
        if (r.status != RoundStatus.Proposed && r.status != RoundStatus.Challenged) {
            revert RoundNotCancellable();
        }
        r.status = RoundStatus.Cancelled;
        emit RoundCancelled(roundHash, msg.sender, reasonIpfsUri);
    }

    /*//////////////////////////////////////////////////////////////
                                VIEWS
    //////////////////////////////////////////////////////////////*/

    /// @inheritdoc IRoundRegistry
    function statusOf(
        bytes32 roundHash
    ) external view returns (RoundStatus) {
        return _rounds[roundHash].status;
    }

    /// @notice Returns the round's static fields (ipfsUri, proposedAt, challengeWindowDays,
    ///         status). Use `getRoundBeneficiaries` and `getRoundAmounts` for the arrays.
    function getRound(
        bytes32 roundHash
    ) external view returns (string memory ipfsUri, uint64 proposedAt, uint32 challengeWindowDays, RoundStatus status) {
        Round storage r = _rounds[roundHash];
        return (r.ipfsUri, r.proposedAt, r.challengeWindowDays, r.status);
    }

    /// @notice Returns the beneficiaries array of a round.
    function getRoundBeneficiaries(
        bytes32 roundHash
    ) external view returns (address[] memory) {
        return _rounds[roundHash].beneficiaries;
    }

    /// @notice Returns the amounts array of a round.
    function getRoundAmounts(
        bytes32 roundHash
    ) external view returns (uint256[] memory) {
        return _rounds[roundHash].amounts;
    }

    /// @notice Convenience: timestamp at which the challenge window closes (`proposedAt +
    ///         challengeWindowDays * 1 days`). Returns 0 for an unknown round.
    function windowEndOf(
        bytes32 roundHash
    ) external view returns (uint256) {
        Round storage r = _rounds[roundHash];
        if (r.proposedAt == 0) return 0;
        return _windowEnd(r);
    }

    /*//////////////////////////////////////////////////////////////
                              INTERNAL
    //////////////////////////////////////////////////////////////*/

    function _windowEnd(
        Round storage r
    ) private view returns (uint256) {
        return uint256(r.proposedAt) + uint256(r.challengeWindowDays) * 1 days;
    }
}
