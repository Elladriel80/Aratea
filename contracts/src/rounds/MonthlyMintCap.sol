// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

/// @title  MonthlyMintCap — pure library enforcing the 10% monthly mint cap
/// @notice Math used by RoundRegistry (M3) to ensure that the total amount minted in any
///         single calendar month (UTC) never exceeds 10% of the supply circulating at the
///         start of that month. White paper §7.7. Stateless by design — the caller is
///         responsible for tracking `alreadyMintedThisMonth` and reading `block.timestamp`
///         and the token's `totalSupply`.
///
/// @dev    Genesis exception: when `supplyAtMonthStart == 0`, the cap does not bind. The
///         very first mint of the protocol (and any subsequent mint that occurs while
///         total supply remains zero) is unconstrained by this library. This is the only
///         exception and is documented in contracts/docs/ROUND-LIFECYCLE.md §6.
///
///         Calendar mapping: month identifiers are computed as
///             monthId = year * 12 + (month - 1)
///         where (year, month) is the UTC Gregorian date of the timestamp. month ∈ [1, 12].
///         Two timestamps fall in the same month iff `monthIdOf(t1) == monthIdOf(t2)`.
///
///         Conversion uses Howard Hinnant's `civil_from_days` algorithm
///         (https://howardhinnant.github.io/date_algorithms.html). Validity range:
///         supports any `timestamp ∈ [0, type(uint64).max]` (well past the year 5_000_000),
///         so block.timestamp inputs are always safe.
library MonthlyMintCap {
    /// @notice Cap rate, in basis points. 1000 bps = 10%.
    uint256 internal constant CAP_BPS = 1000;
    uint256 internal constant BPS_DENOMINATOR = 10_000;

    uint256 private constant SECONDS_PER_DAY = 86_400;

    /*//////////////////////////////////////////////////////////////
                              CALENDAR
    //////////////////////////////////////////////////////////////*/

    /// @notice Returns the canonical month id `year * 12 + (month - 1)` for a UTC timestamp.
    /// @dev    Pure. Uses Howard Hinnant's algorithm. For any reachable EVM timestamp the
    ///         result is exact (no leap-year drift).
    function monthIdOf(
        uint256 timestamp
    ) internal pure returns (uint256) {
        (uint256 y, uint256 m) = _civilFromDays(timestamp / SECONDS_PER_DAY);
        return y * 12 + (m - 1);
    }

    /// @dev Howard Hinnant `civil_from_days` — converts days-since-1970-01-01 into the
    ///      Gregorian (year, month) tuple. Day-of-month is intentionally omitted: the cap
    ///      depends only on the bucket (year, month).
    ///
    ///      The intermediate divisions and multiplications below form an integer-exact
    ///      algorithm. Each division on `z`, `doe`, or `yoe` is INTENTIONALLY composed with
    ///      a subsequent multiplication; the algorithm is mathematically proven to yield the
    ///      same result as the unrounded computation for any input within the supported
    ///      range, and the result is verified against known UTC reference dates in the unit
    ///      tests. Slither's `divide-before-multiply` warning is therefore a false positive
    ///      on the whole function and the detector is suppressed for the block below.
    // slither-disable-start divide-before-multiply
    function _civilFromDays(
        uint256 daysSinceEpoch
    ) private pure returns (uint256 year, uint256 month) {
        // Shift origin to 0000-03-01 so March is the first month of an "era".
        uint256 z = daysSinceEpoch + 719_468;
        uint256 era = z / 146_097;
        uint256 doe = z - era * 146_097; // day of era,  ∈ [0, 146_096]
        uint256 yoe = (doe - doe / 1460 + doe / 36_524 - doe / 146_096) / 365; // year of era, ∈ [0, 399]
        uint256 doy = doe - (365 * yoe + yoe / 4 - yoe / 100); // day of year (March-based)
        uint256 mp = (5 * doy + 2) / 153; // March-based month index, ∈ [0, 11]
        month = mp < 10 ? mp + 3 : mp - 9; // shift to January-based [1, 12]
        year = yoe + era * 400 + (mp >= 10 ? 1 : 0);
    }

    // slither-disable-end divide-before-multiply

    /*//////////////////////////////////////////////////////////////
                              CAP MATH
    //////////////////////////////////////////////////////////////*/

    /// @notice Whether minting `requestedAmount` is admissible in the current month, given
    ///         `supplyAtMonthStart` and the amount `alreadyMintedThisMonth`.
    /// @dev    Two early-return cases for clean semantics:
    ///         1. `requestedAmount == 0` is always admissible (no inflation, trivially safe
    ///            even when `alreadyMintedThisMonth` somehow exceeded the cap defensively).
    ///         2. `supplyAtMonthStart == 0` triggers the genesis exception: every amount
    ///            is admissible because the very first mint has nothing to dilute.
    function isMintAdmissible(
        uint256 supplyAtMonthStart,
        uint256 alreadyMintedThisMonth,
        uint256 requestedAmount
    ) internal pure returns (bool) {
        if (requestedAmount == 0) return true;
        if (supplyAtMonthStart == 0) return true;

        uint256 cap = (supplyAtMonthStart * CAP_BPS) / BPS_DENOMINATOR;
        // Defensive overflow guard — alreadyMinted ≤ cap by induction in normal operation,
        // but the library refuses to wrap if a misuse pushes it above.
        if (alreadyMintedThisMonth >= cap) return false;
        return requestedAmount <= cap - alreadyMintedThisMonth;
    }

    /// @notice Returns the absolute monthly cap given the supply at month-start. For
    ///         `supplyAtMonthStart == 0` returns `type(uint256).max` as a sentinel meaning
    ///         "cap does not bind".
    function capFor(
        uint256 supplyAtMonthStart
    ) internal pure returns (uint256) {
        if (supplyAtMonthStart == 0) return type(uint256).max;
        return (supplyAtMonthStart * CAP_BPS) / BPS_DENOMINATOR;
    }

    /// @notice Remaining mint margin in the current month. Returns `type(uint256).max` when
    ///         `supplyAtMonthStart == 0` (no cap), or 0 if the cap is already exhausted.
    function remainingMargin(
        uint256 supplyAtMonthStart,
        uint256 alreadyMintedThisMonth
    ) internal pure returns (uint256) {
        if (supplyAtMonthStart == 0) return type(uint256).max;
        uint256 cap = (supplyAtMonthStart * CAP_BPS) / BPS_DENOMINATOR;
        if (alreadyMintedThisMonth >= cap) return 0;
        return cap - alreadyMintedThisMonth;
    }
}
