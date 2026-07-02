// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

import {IWeatherOracle} from "../interfaces/IWeatherOracle.sol";

/// @title  MockWeatherOracle — testnet oracle with keeper-controlled result posting
/// @notice Keeper calls postResult() after the settlement window to record the
///         observed temperature. Used on Arbitrum Sepolia for end-to-end Phase 3
///         testing before ReclaimWeatherSource is wired.
///
///         NOT for mainnet. On mainnet, replace with a Reclaim Protocol verifier
///         or another trust-minimised oracle (e.g. Chainlink EA).
///         DeployPhase3 enforces USE_MOCK_ORACLE=false on Arbitrum mainnet.
///
/// @dev    Access-gated: only the deployer (set as keeper at construction) can
///         post results, preventing unauthorised result injection on testnet.
contract MockWeatherOracle is IWeatherOracle {
    /// @notice Address allowed to call postResult (set to deployer at construction).
    address public immutable keeper;

    mapping(bytes32 => mapping(uint64 => int16)) private _temps;
    mapping(bytes32 => mapping(uint64 => bool))  private _settled;

    event ResultPosted(bytes32 indexed locationKey, uint64 indexed targetDate, int16 tempF);

    constructor() {
        keeper = msg.sender;
    }

    modifier onlyKeeper() {
        require(msg.sender == keeper, "MockWeatherOracle: not keeper");
        _;
    }

    /// @notice Post (or overwrite) an observed temperature result.
    /// @param locationKey  keccak256 of the station string (e.g. keccak256("KXHIGHTSFO"))
    /// @param targetDate   Settlement date as UNIX timestamp (midnight UTC)
    /// @param tempF        Observed temperature in °F × 10 (e.g. 900 = 90.0 °F)
    function postResult(bytes32 locationKey, uint64 targetDate, int16 tempF) external onlyKeeper {
        _temps[locationKey][targetDate]   = tempF;
        _settled[locationKey][targetDate] = true;
        emit ResultPosted(locationKey, targetDate, tempF);
    }

    /// @inheritdoc IWeatherOracle
    function getResult(bytes32 locationKey, uint64 targetDate)
        external
        view
        returns (int16 observedTempF, bool settled)
    {
        return (_temps[locationKey][targetDate], _settled[locationKey][targetDate]);
    }
}
