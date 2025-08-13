// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract UniversalVault {
    address public owner;
    IERC20 public profitToken;
    uint256 public constant SPLIT = 50;

    event Payout(address indexed owner, uint256 amount);
    event Reinvest(uint256 amount);

    constructor(address _owner, address _token) {
        owner = _owner;
        profitToken = IERC20(_token);
    }

    function depositAndSplit(uint256 amount) external {
        require(profitToken.transferFrom(msg.sender, address(this), amount), "Transfer failed");
        uint256 payout = amount * SPLIT / 100;
        uint256 reinvest = amount - payout;
        require(profitToken.transfer(owner, payout), "Payout failed");
        emit Payout(owner, payout);
        emit Reinvest(reinvest);
    }
}
