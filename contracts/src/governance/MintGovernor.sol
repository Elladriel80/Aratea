// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
import {IVotes} from "@openzeppelin/contracts/governance/utils/IVotes.sol";

import {RoundRegistry} from "../rounds/RoundRegistry.sol";
import {IRoundRegistry} from "../interfaces/IRoundRegistry.sol";

/// @title  MintGovernor — automatic monthly mint + token-weighted contestation (Phase 2)
/// @notice Sits ON TOP of the unchanged `RoundRegistry` (the sole mint source). Implements the
///         rules acted in `docs/gouvernance-auto-mint.fr.md`:
///
///         Nominal (uncontested) flow:
///           - The keeper (holding ROUND_PROPOSER_ROLE on the registry) proposes a round at J0.
///           - After the challenge window, ANYONE calls `finalize(roundHash)`; the Governor
///             (holding ROUND_EXECUTOR_ROLE) executes it → mint. No human in the loop.
///
///         Contested flow:
///           - A token holder calls `challenge(roundHash)` → the Governor marks the round
///             `Challenged` (it holds ROUND_CHALLENGER_ROLE, the registry's single challenge
///             front-door) and opens a token-weighted vote.
///           - Vote weight is frozen at the round's `proposedAt` snapshot (ERC20Votes checkpoints,
///             timestamp clock). Buying/borrowing tokens AFTER the proposal carries NO weight.
///           - The original is REJECTED iff quorum is reached AND strictly more than half of the
///             expressed votes are AGAINST. Quorum not reached → round validated as-is.
///           - On rejection, a re-proposition cycle opens: holders ≥ proposalThreshold submit
///             alternative allocations (capped at MAX_ALTERNATIVES per dispute), voted SEQUENTIALLY
///             by submission order. An alternative is accepted under the SAME quorum as the original
///             (quorum reached AND for > against). The first accepted is minted and all siblings are
///             cancelled.
///
///         Security posture (see the contract's tests + docs):
///           - Anti-vote-buying: weights snapshotted at proposal time.
///           - No mint bypasses the rules: the registry is the only minter, the Governor is its
///             only EXECUTOR, and the Governor executes only the uncontested or vote-accepted path.
///           - Keeper = proposer/finalizer ONLY; it holds no role that can change roles.
///           - Exact integer math: quorum uses ceil division; "> 50%" is `against > for` (no
///             rounding in the attacker's favor).
///           - TESTNET / pre-audit. Mint-controlling governance is the highest-risk class —
///             community audit required before mainnet.
contract MintGovernor is AccessControl, ReentrancyGuard {
    using Math for uint256;

    /*//////////////////////////////////////////////////////////////
                                 TYPES
    //////////////////////////////////////////////////////////////*/

    enum BallotState {
        None, // never created
        Pending, // queued, vote not started yet
        Voting, // vote in progress
        Rejected, // vote lost (or superseded by an accepted sibling)
        Accepted // vote won → executed
    }

    /// @notice One vote, keyed by the registry round hash it ratifies (original or alternative).
    struct Ballot {
        bytes32 dispute; // the dispute key = the ORIGINAL contested round hash
        bool isOriginal; // true for the first ballot of a dispute
        uint64 voteStart;
        uint64 voteEnd;
        uint256 forVotes;
        uint256 againstVotes;
        BallotState state;
    }

    /// @notice A contestation around an original round, with its sequential ballot queue.
    struct Dispute {
        uint64 snapshot; // = original round proposedAt (vote-weight timepoint). 0 = no dispute.
        uint256 circulating; // circulating supply cached at snapshot
        uint256 quorumVotes; // quorum threshold (votes) cached at snapshot
        bytes32 activeBallot; // ballot currently open for voting, 0 if none
        bool originalDecided; // the original ballot has been tallied
        bool resolved; // terminal: an allocation was minted
        bytes32 executed; // the round that was minted (0 if none)
        bytes32[] queue; // ballots in submission order (original first)
    }

    /*//////////////////////////////////////////////////////////////
                               CONSTANTS
    //////////////////////////////////////////////////////////////*/

    uint16 public constant BPS_DENOMINATOR = 10_000;
    uint32 public constant MIN_VOTE_DAYS = 1;
    uint32 public constant MAX_VOTE_DAYS = 365;
    /// @notice Cap on the number of ALTERNATIVES per dispute (the original is not counted). Bounds
    ///         the `queue` loops in `_activateNextPending`/`_executeWinner` so a holder ≥ threshold
    ///         cannot grow the queue until those loops exceed the block gas limit (resolution DoS).
    uint256 public constant MAX_ALTERNATIVES = 16;

    /*//////////////////////////////////////////////////////////////
                            IMMUTABLE WIRING
    //////////////////////////////////////////////////////////////*/

    /// @notice The registry the Governor proposes/challenges/executes/cancels on.
    RoundRegistry public immutable registry;
    /// @notice The vote-weight source (AUG-POC, an ERC20Votes token with a timestamp clock).
    IVotes public immutable token;

    /*//////////////////////////////////////////////////////////////
                            TUNABLE PARAMS
    //////////////////////////////////////////////////////////////*/

    /// @notice Quorum as a fraction of circulating supply at the snapshot (bps). Default 15%.
    uint16 public quorumBps;
    /// @notice Minimum weight (bps of circulating) to submit an alternative. Default 1%.
    uint16 public proposalThresholdBps;
    /// @notice Vote duration in days. Default 7.
    uint32 public voteDurationDays;
    /// @notice Treasury address excluded from "circulating supply" (total − treasury). 0 disables
    ///         the subtraction. The treasury MUST self-delegate for the subtraction to be exact
    ///         (ERC20Votes checkpoints delegated units, not raw balances).
    address public treasury;

    /*//////////////////////////////////////////////////////////////
                                STORAGE
    //////////////////////////////////////////////////////////////*/

    mapping(bytes32 => Dispute) private _disputes; // key = original round hash
    mapping(bytes32 => Ballot) private _ballots; // key = ballot round hash
    /// @notice ballotRound => voter => has voted (prevents double voting on a ballot).
    mapping(bytes32 => mapping(address => bool)) public hasVoted;

    /*//////////////////////////////////////////////////////////////
                                EVENTS
    //////////////////////////////////////////////////////////////*/

    event RoundFinalized(bytes32 indexed roundHash);
    event DisputeOpened(
        bytes32 indexed originalRound, address indexed challenger, uint64 snapshot, uint256 quorumVotes, uint64 voteEnd
    );
    event VoteOpened(bytes32 indexed originalRound, bytes32 indexed ballotRound, uint64 voteStart, uint64 voteEnd);
    event VoteCast(bytes32 indexed ballotRound, address indexed voter, bool support, uint256 weight);
    event BallotRejected(
        bytes32 indexed originalRound, bytes32 indexed ballotRound, uint256 forVotes, uint256 againstVotes
    );
    event AlternativeProposed(bytes32 indexed originalRound, bytes32 indexed altRound, address indexed proposer);
    event DisputeResolved(bytes32 indexed originalRound, bytes32 indexed executedRound);
    /// @notice Emitted when an admin force-resolves a stuck dispute without minting.
    event DisputeForceResolved(bytes32 indexed originalRound);
    event ParamUpdated(string indexed key, uint256 value);
    event TreasuryUpdated(address treasury);

    /*//////////////////////////////////////////////////////////////
                                ERRORS
    //////////////////////////////////////////////////////////////*/

    error ZeroAddress();
    error InvalidParam();
    error RoundUnknown();
    error NotFinalizable();
    error NotContestable();
    error WindowClosed();
    error SnapshotNotInPast();
    error AlreadyDisputed();
    error NoVotingPower();
    error NoActiveBallot();
    error NotActiveBallot();
    error VotingClosed();
    error VotingNotStarted();
    error VotingNotEnded();
    error AlreadyVoted();
    error BallotNotVoting();
    error DisputeAlreadyResolved();
    error OriginalNotRejected();
    error BelowProposalThreshold();
    error EmptyAllocation();
    error TooManyAlternatives();

    /*//////////////////////////////////////////////////////////////
                              CONSTRUCTOR
    //////////////////////////////////////////////////////////////*/

    constructor(
        address admin,
        RoundRegistry registry_,
        IVotes token_,
        address treasury_,
        uint16 quorumBps_,
        uint16 proposalThresholdBps_,
        uint32 voteDurationDays_
    ) {
        if (admin == address(0)) revert ZeroAddress();
        if (address(registry_) == address(0) || address(token_) == address(0)) revert ZeroAddress();
        if (quorumBps_ == 0 || quorumBps_ > BPS_DENOMINATOR) revert InvalidParam();
        if (proposalThresholdBps_ > BPS_DENOMINATOR) revert InvalidParam();
        if (voteDurationDays_ < MIN_VOTE_DAYS || voteDurationDays_ > MAX_VOTE_DAYS) revert InvalidParam();

        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        registry = registry_;
        token = token_;
        treasury = treasury_; // may be 0 (no subtraction)
        quorumBps = quorumBps_;
        proposalThresholdBps = proposalThresholdBps_;
        voteDurationDays = voteDurationDays_;
    }

    /*//////////////////////////////////////////////////////////////
                          NOMINAL (UNCONTESTED)
    //////////////////////////////////////////////////////////////*/

    /// @notice Permissionless finalization of an UNCONTESTED round once its challenge window has
    ///         passed. Reverts if the round is not in `Proposed` status (a challenged round is
    ///         resolved through the vote, never here). The registry re-checks the window.
    /// @dev    The keeper calls this monthly, but anyone may — it cannot mint anything the registry
    ///         would not already mint on its own rules.
    function finalize(
        bytes32 roundHash
    ) external nonReentrant {
        if (registry.statusOf(roundHash) != IRoundRegistry.RoundStatus.Proposed) revert NotFinalizable();
        registry.executeRound(roundHash); // registry enforces "window expired"
        emit RoundFinalized(roundHash);
    }

    /*//////////////////////////////////////////////////////////////
                          CONTESTATION → VOTE
    //////////////////////////////////////////////////////////////*/

    /// @notice A token holder contests a `Proposed` round during its challenge window, opening a
    ///         token-weighted vote on the original allocation.
    /// @dev    Weight is frozen at the round's `proposedAt`. The challenger must have had voting
    ///         power at that snapshot (i.e. balance delegated before the proposal).
    function challenge(
        bytes32 roundHash,
        string calldata reasonIpfsUri
    ) external nonReentrant {
        // Only proposedAt + status are needed; ipfsUri and challengeWindowDays are intentionally
        // discarded (the partial-tuple read is deliberate, not a forgotten return value).
        // slither-disable-next-line unused-return
        (, uint64 proposedAt,, IRoundRegistry.RoundStatus status) = registry.getRound(roundHash);
        if (proposedAt == 0) revert RoundUnknown();
        // Only a still-`Proposed` round can be contested. After the first challenge the round is
        // `Challenged`, so a second `challenge` for the same round trips this guard (it also
        // doubles as the "cannot dispute twice" guard since a dispute always flips the status).
        if (status != IRoundRegistry.RoundStatus.Proposed) revert NotContestable();
        if (block.timestamp >= registry.windowEndOf(roundHash)) revert WindowClosed();
        // Snapshot must be strictly in the past so getPastVotes/getPastTotalSupply are queryable.
        if (block.timestamp <= proposedAt) revert SnapshotNotInPast();
        if (_disputes[roundHash].snapshot != 0) revert AlreadyDisputed();
        if (token.getPastVotes(msg.sender, proposedAt) == 0) revert NoVotingPower();

        uint256 circulating = _circulatingAt(proposedAt);
        uint256 quorumVotes = Math.ceilDiv(circulating * quorumBps, BPS_DENOMINATOR);

        // Vote runs at least `voteDurationDays`, but never ends before the registry challenge
        // window closes — otherwise an upheld allocation could not yet be executed (the registry
        // requires the window to have passed).
        uint64 voteEnd = uint64(Math.max(block.timestamp + _voteDuration(), registry.windowEndOf(roundHash)));

        Dispute storage d = _disputes[roundHash];
        d.snapshot = proposedAt;
        d.circulating = circulating;
        d.quorumVotes = quorumVotes;
        d.activeBallot = roundHash;
        d.queue.push(roundHash);

        Ballot storage b = _ballots[roundHash];
        b.dispute = roundHash;
        b.isOriginal = true;
        b.voteStart = uint64(block.timestamp);
        b.voteEnd = voteEnd;
        b.state = BallotState.Voting;

        // Interaction with the trusted registry (no callback into this contract).
        registry.challengeRound(roundHash, reasonIpfsUri);

        emit DisputeOpened(roundHash, msg.sender, proposedAt, quorumVotes, voteEnd);
        emit VoteOpened(roundHash, roundHash, uint64(block.timestamp), voteEnd);
    }

    /// @notice Cast a token-weighted vote on the currently active ballot of a dispute.
    /// @param  ballotRound the round hash being voted on (original or alternative).
    /// @param  support     true = keep/accept the allocation, false = reject it.
    function castVote(
        bytes32 ballotRound,
        bool support
    ) external {
        Ballot storage b = _ballots[ballotRound];
        if (b.state != BallotState.Voting) revert BallotNotVoting();
        Dispute storage d = _disputes[b.dispute];
        if (d.activeBallot != ballotRound) revert NotActiveBallot();
        if (block.timestamp < b.voteStart) revert VotingNotStarted();
        if (block.timestamp >= b.voteEnd) revert VotingClosed();
        if (hasVoted[ballotRound][msg.sender]) revert AlreadyVoted();

        uint256 weight = token.getPastVotes(msg.sender, d.snapshot);
        if (weight == 0) revert NoVotingPower();

        hasVoted[ballotRound][msg.sender] = true;
        if (support) {
            b.forVotes += weight;
        } else {
            b.againstVotes += weight;
        }
        emit VoteCast(ballotRound, msg.sender, support, weight);
    }

    /// @notice Tally the active ballot after its vote ends and apply the outcome:
    ///         original upheld/validated → mint it; original rejected → open re-proposition;
    ///         alternative accepted → mint it and cancel siblings; alternative rejected → next.
    /// @dev    Permissionless. Mints occur only here or in `finalize`, always via the registry.
    function resolve(
        bytes32 ballotRound
    ) external nonReentrant {
        Ballot storage b = _ballots[ballotRound];
        if (b.state != BallotState.Voting) revert BallotNotVoting();
        if (block.timestamp < b.voteEnd) revert VotingNotEnded();
        Dispute storage d = _disputes[b.dispute];
        if (d.activeBallot != ballotRound) revert NotActiveBallot();

        d.activeBallot = bytes32(0);

        if (b.isOriginal) {
            d.originalDecided = true;
            bool quorumReached = (b.forVotes + b.againstVotes) >= d.quorumVotes;
            // Reject iff quorum reached AND strictly more than half of expressed votes are AGAINST.
            // "> 50% against" ⇔ against > for (exact, integer-safe). A tie upholds the round.
            bool rejected = quorumReached && (b.againstVotes > b.forVotes);
            if (rejected) {
                b.state = BallotState.Rejected;
                emit BallotRejected(b.dispute, ballotRound, b.forVotes, b.againstVotes);
                // Re-proposition opens: activeBallot stays 0 until an alternative is submitted.
            } else {
                b.state = BallotState.Accepted;
                _executeWinner(d, b.dispute, ballotRound);
            }
        } else {
            // Alternative: SAME quorum as the original (anti-capture by a low-turnout whale).
            // Accepted iff quorum reached AND strictly more "for" than "against" votes.
            bool quorumReached = (b.forVotes + b.againstVotes) >= d.quorumVotes;
            bool accepted = quorumReached && (b.forVotes > b.againstVotes);
            if (accepted) {
                b.state = BallotState.Accepted;
                _executeWinner(d, b.dispute, ballotRound);
            } else {
                b.state = BallotState.Rejected;
                emit BallotRejected(b.dispute, ballotRound, b.forVotes, b.againstVotes);
                _activateNextPending(d, b.dispute);
            }
        }
    }

    /// @notice Submit an alternative allocation during a re-proposition cycle (the original was
    ///         rejected and nothing has been minted yet). Caller must hold ≥ proposalThreshold of
    ///         the snapshot's circulating supply. The alternative is registered in the registry,
    ///         immediately locked (`Challenged`) so the permissionless finalizer cannot touch it,
    ///         and queued; it starts voting at once if no other ballot is active.
    /// @return altHash the registry round hash of the alternative.
    function proposeAlternative(
        bytes32 originalRound,
        address[] calldata beneficiaries,
        uint256[] calldata amounts,
        string calldata ipfsUri
    ) external nonReentrant returns (bytes32 altHash) {
        Dispute storage d = _disputes[originalRound];
        if (d.snapshot == 0) revert RoundUnknown();
        if (d.resolved) revert DisputeAlreadyResolved();
        // Re-proposition only opens once the original is decided-and-not-resolved, i.e. rejected.
        if (!d.originalDecided) revert OriginalNotRejected();
        if (beneficiaries.length == 0) revert EmptyAllocation();
        // queue[0] is the original; cap the number of ALTERNATIVES (anti-spam / anti-DoS gas).
        if (d.queue.length - 1 >= MAX_ALTERNATIVES) revert TooManyAlternatives();

        uint256 thresholdVotes = Math.max(Math.mulDiv(d.circulating, proposalThresholdBps, BPS_DENOMINATOR), 1);
        if (token.getPastVotes(msg.sender, d.snapshot) < thresholdVotes) revert BelowProposalThreshold();

        altHash = keccak256(abi.encode(beneficiaries, amounts, ipfsUri));

        // Effects first (checks-effects-interactions): queue the alternative and, if no other
        // ballot is active, open its vote immediately. If the registry calls below revert (e.g.
        // duplicate hash), the whole tx reverts and these writes roll back.
        d.queue.push(altHash);
        Ballot storage b = _ballots[altHash];
        b.dispute = originalRound;
        b.isOriginal = false;
        bool activateNow = d.activeBallot == bytes32(0);
        if (activateNow) {
            b.voteStart = uint64(block.timestamp);
            b.voteEnd = uint64(block.timestamp + _voteDuration());
            b.state = BallotState.Voting;
            d.activeBallot = altHash;
        } else {
            b.state = BallotState.Pending;
        }

        // Interactions: register the alternative and lock it. proposeRound re-validates the
        // hash/arrays and reverts on a duplicate; challengeRound moves it to Challenged so only
        // this Governor's vote-resolution path (never `finalize`) can ever execute it.
        registry.proposeRound(altHash, beneficiaries, amounts, ipfsUri, voteDurationDays);
        registry.challengeRound(altHash, ipfsUri);

        emit AlternativeProposed(originalRound, altHash, msg.sender);
        if (activateNow) emit VoteOpened(originalRound, altHash, b.voteStart, b.voteEnd);
    }

    /*//////////////////////////////////////////////////////////////
                              ADMIN (PARAMS)
    //////////////////////////////////////////////////////////////*/

    function setQuorumBps(
        uint16 newQuorumBps
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (newQuorumBps == 0 || newQuorumBps > BPS_DENOMINATOR) revert InvalidParam();
        quorumBps = newQuorumBps;
        emit ParamUpdated("quorumBps", newQuorumBps);
    }

    function setProposalThresholdBps(
        uint16 newThresholdBps
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (newThresholdBps > BPS_DENOMINATOR) revert InvalidParam();
        proposalThresholdBps = newThresholdBps;
        emit ParamUpdated("proposalThresholdBps", newThresholdBps);
    }

    function setVoteDurationDays(
        uint32 newVoteDurationDays
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (newVoteDurationDays < MIN_VOTE_DAYS || newVoteDurationDays > MAX_VOTE_DAYS) revert InvalidParam();
        voteDurationDays = newVoteDurationDays;
        emit ParamUpdated("voteDurationDays", newVoteDurationDays);
    }

    function setTreasury(
        address newTreasury
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        treasury = newTreasury;
        emit TreasuryUpdated(newTreasury);
    }

    /*//////////////////////////////////////////////////////////////
                              EMERGENCY
    //////////////////////////////////////////////////////////////*/

    /// @notice Last-resort admin escape hatch: mark a stuck dispute as resolved WITHOUT minting.
    /// @dev    Needed only if `_executeWinner` can never complete — e.g. the registry reverted
    ///         `executeRound` because `ROUND_EXECUTOR_ROLE` was accidentally revoked. Marks
    ///         `resolved = true` (no token transfer occurs). If there is still an `activeBallot`,
    ///         it is marked `Rejected` and cleared so that `resolve()` cannot be called again.
    ///         Protected by `DEFAULT_ADMIN_ROLE`. SHOULD NEVER be needed in normal operation.
    function forceResolveStuck(
        bytes32 originalRound
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        Dispute storage d = _disputes[originalRound];
        if (d.snapshot == 0) revert RoundUnknown();
        if (d.resolved) revert DisputeAlreadyResolved();
        d.resolved = true;
        if (d.activeBallot != bytes32(0)) {
            _ballots[d.activeBallot].state = BallotState.Rejected;
            d.activeBallot = bytes32(0);
        }
        emit DisputeForceResolved(originalRound);
    }

    /*//////////////////////////////////////////////////////////////
                                VIEWS
    //////////////////////////////////////////////////////////////*/

    /// @notice Circulating supply (= total minted − treasury) at a past timepoint, the quorum base.
    function circulatingSupplyAt(
        uint256 timepoint
    ) external view returns (uint256) {
        return _circulatingAt(timepoint);
    }

    function getDispute(
        bytes32 originalRound
    )
        external
        view
        returns (
            uint64 snapshot,
            uint256 circulating,
            uint256 quorumVotes,
            bytes32 activeBallot,
            bool originalDecided,
            bool resolved,
            bytes32 executed,
            bytes32[] memory queue
        )
    {
        Dispute storage d = _disputes[originalRound];
        return
            (
                d.snapshot,
                d.circulating,
                d.quorumVotes,
                d.activeBallot,
                d.originalDecided,
                d.resolved,
                d.executed,
                d.queue
            );
    }

    function getBallot(
        bytes32 ballotRound
    )
        external
        view
        returns (
            bytes32 dispute,
            bool isOriginal,
            uint64 voteStart,
            uint64 voteEnd,
            uint256 forVotes,
            uint256 againstVotes,
            BallotState state
        )
    {
        Ballot storage b = _ballots[ballotRound];
        return (b.dispute, b.isOriginal, b.voteStart, b.voteEnd, b.forVotes, b.againstVotes, b.state);
    }

    /*//////////////////////////////////////////////////////////////
                               INTERNAL
    //////////////////////////////////////////////////////////////*/

    function _voteDuration() private view returns (uint256) {
        return uint256(voteDurationDays) * 1 days;
    }

    function _circulatingAt(
        uint256 timepoint
    ) private view returns (uint256) {
        uint256 total = token.getPastTotalSupply(timepoint);
        if (treasury == address(0)) return total;
        uint256 tre = token.getPastVotes(treasury, timepoint);
        return total > tre ? total - tre : 0;
    }

    /// @dev Activate a specific queued ballot (alternative) for voting now.
    function _activateBallot(
        Dispute storage d,
        bytes32 disputeKey,
        bytes32 ballotRound
    ) private {
        Ballot storage b = _ballots[ballotRound];
        b.voteStart = uint64(block.timestamp);
        b.voteEnd = uint64(block.timestamp + _voteDuration());
        b.state = BallotState.Voting;
        d.activeBallot = ballotRound;
        emit VoteOpened(disputeKey, ballotRound, b.voteStart, b.voteEnd);
    }

    /// @dev Activate the next Pending ballot in submission order, if any.
    function _activateNextPending(
        Dispute storage d,
        bytes32 disputeKey
    ) private {
        uint256 len = d.queue.length;
        for (uint256 i = 0; i < len; i++) {
            bytes32 q = d.queue[i];
            // Enum state equality is exact and intended (no manipulable value involved).
            // slither-disable-next-line incorrect-equality
            if (_ballots[q].state == BallotState.Pending) {
                _activateBallot(d, disputeKey, q);
                return;
            }
        }
        // None pending: dispute stays open awaiting a new alternative (activeBallot already 0).
    }

    /// @dev Mint the winning allocation through the registry and cancel every other ballot of the
    ///      dispute that is still cancellable. Marks the dispute resolved (terminal).
    function _executeWinner(
        Dispute storage d,
        bytes32 disputeKey,
        bytes32 winner
    ) private {
        // Effects first: mark resolved and flip every still-open sibling ballot to Rejected.
        d.resolved = true;
        d.executed = winner;
        uint256 len = d.queue.length;
        for (uint256 i = 0; i < len; i++) {
            bytes32 q = d.queue[i];
            if (q == winner) continue;
            Ballot storage qb = _ballots[q];
            if (qb.state == BallotState.Pending || qb.state == BallotState.Voting) {
                qb.state = BallotState.Rejected;
            }
        }

        // Interactions: mint the winner, then cancel every superseded sibling round so it can
        // never be executed later. The registry/token are trusted and do not call back; this
        // function is also `nonReentrant` at every external entry point.
        registry.executeRound(winner);
        for (uint256 i = 0; i < len; i++) {
            bytes32 q = d.queue[i];
            if (q == winner) continue;
            if (registry.statusOf(q) == IRoundRegistry.RoundStatus.Challenged) {
                registry.cancelRound(q, "governor:superseded");
            }
        }

        emit DisputeResolved(disputeKey, winner);
    }
}
