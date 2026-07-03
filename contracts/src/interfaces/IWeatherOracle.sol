// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

/// @title  IWeatherOracle — read-only interface for weather settlement results
/// @notice Abstraction over the on-chain oracle (ReclaimWeatherSource or mock).
///         PolicyRegistry calls this after the settlement window opens to determine
///         whether the insured temperature event occurred.
///
/// @dev    Phase 3 integration point. The concrete implementation can be
///         ReclaimWeatherSource (Reclaim Protocol proofs) or any trusted data
///         provider that stores (locationKey, targetDate) → observedTempF.
///
///         locationKey must match the station identifiers used in IPolicyRegistry
///         (e.g. keccak256("KXHIGHTSFO") for San Francisco high temperature).
///         targetDate is the settlement day as UNIX timestamp at midnight UTC.
interface IWeatherOracle {
    /// @notice Returns the confirmed temperature for a given station and target date.
    /// @param  locationKey    Station identifier (keccak256 of the station string,
    ///                        e.g. keccak256("KXHIGHTSFO")).
    /// @param  targetDate     Settlement day as UNIX timestamp (midnight UTC).
    /// @return observedTempF  Temperature in °F × 10 (e.g. 900 = 90.0 °F).
    ///                        Returns 0 if not yet settled — callers must check `settled`.
    /// @return settled        True if the oracle has posted a confirmed result for
    ///                        this (locationKey, targetDate) pair.
    function getResult(
        bytes32 locationKey,
        uint64 targetDate
    ) external view returns (int16 observedTempF, bool settled);
}
