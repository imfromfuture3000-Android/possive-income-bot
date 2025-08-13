require('dotenv').config();
const { ethers } = require("hardhat");

async function main() {
  const owner = process.env.OWNER_ADDRESS;
  const dai = process.env.DAI_TOKEN;
  const forwarder = process.env.FORWARDER;

  console.log("Deploying UniversalVault...");

  const Vault = await ethers.getContractFactory("UniversalVault");
  const vault = await Vault.deploy(owner, dai);
  await vault.deployed();
  console.log("✅ UniversalVault deployed to:", vault.address);

  const AUTOGEN = await ethers.getContractFactory("AUTOGEN");
  const autogen = await AUTOGEN.deploy(forwarder, dai, vault.address);
  await autogen.deployed();
  console.log("✅ $AUTOGEN deployed to:", autogen.address);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Deployment failed:", error);
    process.exit(1);
  });
