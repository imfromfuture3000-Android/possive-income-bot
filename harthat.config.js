require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

module.exports = {
  solidity: "0.8.20",
  networks: {
    "base-sepolia": {
      url: process.env.BASE_SEPOLIA_RPC_URL,
      accounts: [], // Gasless — no private key
    },
  },
};
