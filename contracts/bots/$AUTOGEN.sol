// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/metatx/ERC2771Context.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@gelatonetwork/relay-context/contracts/GelatoRelayContext.sol";

contract AUTOGEN is ERC2771Context, GelatoRelayContext {
    address public owner;
    IERC20 public feeToken;
    address public vault;

    constructor(address _forwarder, address _feeToken, address _vault)
        ERC2771Context(_forwarder)
    {
        owner = _msgSender();
        feeToken = IERC20(_feeToken);
        vault = _vault;
    }

    function claimProfit(uint256 amount) external {
        feeToken.approve(vault, amount);
        (bool success,) = vault.call(abi.encodeWithSignature("depositAndSplit(uint256)", amount));
        require(success, "Vault call failed");
    }

    function isRelayContext() public pure override returns (bool) { return true; }
    function _msgSender() internal view override(GelatoRelayContext, Context) returns (address) { return GelatoRelayContext._msgSender(); }
    function _msgData() internal view override(GelatoRelayContext, Context) returns (bytes calldata) { return GelatoRelayContext._msgData(); }
}
