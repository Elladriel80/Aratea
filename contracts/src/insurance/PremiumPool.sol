// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

import {IPremiumPool} from "../interfaces/IPremiumPool.sol";

/// @title  PremiumPool — USDC reserve pool for Phase 3 parametric policies
/// @notice Holds the association's reserves (premiums + admin capital).
///         Enforces the MCR floor (Art. R334-6 Code des assurances, régime simplifié):
///         available capital ≥ max(200 000 USDC, 18% × annual_premiums).
///
///         Legal structure: Association à but lucratif loi Alsace-Moselle.
///         No external stakers — solvency comes from accumulated premiums + admin seed.
///
///         Roles:
///           DEFAULT_ADMIN_ROLE  — deposit / withdraw (association admin only)
///           POLICY_REGISTRY_ROLE — receivePremium / reserveForPolicy / payout / releaseReserve
contract PremiumPool is AccessControl, ReentrancyGuard, IPremiumPool {
    using SafeERC20 for IERC20;

    /*//////////////////////////////////////////////////////////////
                                 ROLES
    //////////////////////////////////////////////////////////////*/

    bytes32 public constant POLICY_REGISTRY_ROLE = keccak256("POLICY_REGISTRY_ROLE");

    /*//////////////////////////////////////////////////////////////
                               CONSTANTS
    //////////////////////////////////////////////////////////////*/

    /// @notice Statutory MCR floor — régime simplifié AM under 5M€/year.
    ///         200 000 USDC (6 decimals = 200_000e6).
    uint256 public constant MCR_FLOOR_USDC = 200_000e6;

    uint256 private constant PCT_100 = 100;

    /*//////////////////////////////////////////////////////////////
                                STORAGE
    //////////////////////////////////////////////////////////////*/

    IERC20 public immutable usdc;

    uint256 private _availableCapital;
    uint256 private _totalReserved;
    uint256 private _annualPremiums;

    mapping(bytes32 => uint256) private _reserves;

    /*//////////////////////////////////////////////////////////////
                                ERRORS
    //////////////////////////////////////////////////////////////*/

    error ZeroAddress();
    error PayoutExceedsReserve(bytes32 policyId, uint256 amount, uint256 reserved);

    /*//////////////////////////////////////////////////////////////
                             CONSTRUCTOR
    //////////////////////////////////////////////////////////////*/

    constructor(address admin_, address usdc_) {
        if (admin_ == address(0) || usdc_ == address(0)) revert ZeroAddress();
        _grantRole(DEFAULT_ADMIN_ROLE, admin_);
        usdc = IERC20(usdc_);
    }

    /*//////////////////////////////////////////////////////////////
                        ASSOCIATION ADMIN FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @inheritdoc IPremiumPool
    function deposit(uint256 amount) external onlyRole(DEFAULT_ADMIN_ROLE) nonReentrant {
        if (amount == 0) revert ZeroAmount();
        usdc.safeTransferFrom(msg.sender, address(this), amount);
        _availableCapital += amount;
        emit CapitalDeposited(msg.sender, amount, _availableCapital);
    }

    /// @inheritdoc IPremiumPool
    function withdraw(uint256 amount) external onlyRole(DEFAULT_ADMIN_ROLE) nonReentrant {
        if (amount == 0) revert ZeroAmount();
        if (_availableCapital < amount) revert InsufficientAvailableCapital(amount, _availableCapital);
        uint256 remaining = _availableCapital - amount;
        uint256 floor     = mcrFloor();
        if (remaining < floor) revert SolvencyCheckFailed(remaining, floor);
        _availableCapital -= amount;
        usdc.safeTransfer(msg.sender, amount);
        emit CapitalWithdrawn(msg.sender, amount, _availableCapital);
    }

    /*//////////////////////////////////////////////////////////////
                        POLICY REGISTRY FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @inheritdoc IPremiumPool
    /// @dev USDC is transferred directly by PolicyRegistry to this contract before this call.
    ///      This function only updates internal accounting and enforces the MCR gate.
    function receivePremium(bytes32 policyId, uint256 amount)
        external
        onlyRole(POLICY_REGISTRY_ROLE)
        nonReentrant
    {
        if (amount == 0) revert ZeroAmount();
        uint256 floor = mcrFloor();
        // Reject new subscriptions if pool is already below MCR floor
        if (_availableCapital < floor) revert PoolBelowMCR(_availableCapital, floor);
        _availableCapital  += amount;
        _annualPremiums    += amount;
        emit PremiumReceived(policyId, amount);
    }

    /// @inheritdoc IPremiumPool
    function reserveForPolicy(bytes32 policyId, uint256 sumAssured)
        external
        onlyRole(POLICY_REGISTRY_ROLE)
        nonReentrant
    {
        if (sumAssured == 0) revert ZeroAmount();
        if (_reserves[policyId] != 0) revert ReserveAlreadyExists(policyId);
        if (_availableCapital < sumAssured) {
            revert InsufficientAvailableCapital(sumAssured, _availableCapital);
        }
        _availableCapital -= sumAssured;
        _totalReserved    += sumAssured;
        _reserves[policyId] = sumAssured;
        emit CapitalReserved(policyId, sumAssured);
    }

    /// @inheritdoc IPremiumPool
    function payout(bytes32 policyId, address subscriber, uint256 amount)
        external
        onlyRole(POLICY_REGISTRY_ROLE)
        nonReentrant
    {
        if (amount == 0) revert ZeroAmount();
        uint256 reserved = _reserves[policyId];
        if (reserved == 0) revert ReserveNotFound(policyId);
        if (amount > reserved) revert PayoutExceedsReserve(policyId, amount, reserved);
        delete _reserves[policyId];
        _totalReserved -= reserved;
        // Remainder above payout amount goes back to available capital
        _availableCapital += reserved - amount;
        usdc.safeTransfer(subscriber, amount);
        emit PayoutSent(policyId, subscriber, amount);
    }

    /// @inheritdoc IPremiumPool
    function releaseReserve(bytes32 policyId)
        external
        onlyRole(POLICY_REGISTRY_ROLE)
        nonReentrant
    {
        uint256 reserved = _reserves[policyId];
        if (reserved == 0) revert ReserveNotFound(policyId);
        delete _reserves[policyId];
        _totalReserved    -= reserved;
        _availableCapital += reserved;
        emit ReserveReleased(policyId, reserved);
    }

    /*//////////////////////////////////////////////////////////////
                             VIEW FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @inheritdoc IPremiumPool
    function totalCapital() external view returns (uint256) {
        return _availableCapital + _totalReserved;
    }

    /// @inheritdoc IPremiumPool
    function availableCapital() external view returns (uint256) {
        return _availableCapital;
    }

    /// @inheritdoc IPremiumPool
    function totalReserved() external view returns (uint256) {
        return _totalReserved;
    }

    /// @inheritdoc IPremiumPool
    function reservedForPolicy(bytes32 policyId) external view returns (uint256) {
        return _reserves[policyId];
    }

    /// @inheritdoc IPremiumPool
    /// @dev Regulatory formula (Art. R334-6 CA, régime simplifié):
    ///      marge = max(200_000 USDC, 18% × annual_premiums)
    ///      The 26% × avg_3yr_claims term is omitted at pilot stage (no claims history).
    function mcrFloor() public view returns (uint256) {
        uint256 dynamic = (_annualPremiums * 18) / PCT_100;
        return dynamic > MCR_FLOOR_USDC ? dynamic : MCR_FLOOR_USDC;
    }

    /// @inheritdoc IPremiumPool
    function annualPremiumsCollected() external view returns (uint256) {
        return _annualPremiums;
    }

    /// @inheritdoc IPremiumPool
    function isSolvent() external view returns (bool) {
        return _availableCapital >= mcrFloor();
    }
}
