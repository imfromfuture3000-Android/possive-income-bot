require('dotenv').config();
const { ethers } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  
  console.log("🚀 Deploying contracts with the account:", deployer.address);
  console.log("💰 Account balance:", (await deployer.getBalance()).toString());

  const network = await ethers.provider.getNetwork();
  console.log("🌐 Network:", network.name, "Chain ID:", network.chainId);

  const owner = process.env.OWNER_ADDRESS || deployer.address;
  const dai = process.env.DAI_TOKEN;
  const forwarder = process.env.FORWARDER;

  if (!dai || !forwarder) {
    throw new Error("❌ Missing DAI_TOKEN or FORWARDER environment variables");
  }

  console.log("📝 Configuration:");
  console.log("   Owner:", owner);
  console.log("   DAI Token:", dai);
  console.log("   Forwarder:", forwarder);

  console.log("\n🏗️  Deploying UniversalVault...");
  const Vault = await ethers.getContractFactory("UniversalVault");
  const vault = await Vault.deploy(owner, dai);
  await vault.waitForDeployment();
  
  const vaultAddress = await vault.getAddress();
  console.log("✅ UniversalVault deployed to:", vaultAddress);

  console.log("\n🤖 Deploying $AUTOGEN bot...");
  const AUTOGEN = await ethers.getContractFactory("AUTOGEN");
  const autogen = await AUTOGEN.deploy(forwarder, dai, vaultAddress);
  await autogen.waitForDeployment();
  
  const autogenAddress = await autogen.getAddress();
  console.log("✅ $AUTOGEN deployed to:", autogenAddress);

  // Get deployment transaction hashes
  console.log("\n📋 Deployment Summary:");
  console.log("=====================================");
  console.log("🏦 UniversalVault:");
  console.log("   Address:", vaultAddress);
  console.log("   Tx Hash:", vault.deploymentTransaction().hash);
  console.log("\n🤖 $AUTOGEN Bot:");
  console.log("   Address:", autogenAddress);
  console.log("   Tx Hash:", autogen.deploymentTransaction().hash);
  console.log("=====================================");

  // Save deployment info
  const deploymentInfo = {
    network: network.name,
    chainId: network.chainId,
    deployer: deployer.address,
    contracts: {
      UniversalVault: {
        address: vaultAddress,
        txHash: vault.deploymentTransaction().hash
      },
      AUTOGEN: {
        address: autogenAddress,
        txHash: autogen.deploymentTransaction().hash
      }
    }
  };

  const fs = require('fs');
  fs.writeFileSync('deployment.json', JSON.stringify(deploymentInfo, null, 2));
  console.log("\n💾 Deployment info saved to deployment.json");
  
  return deploymentInfo;
}

main()
  .then((info) => {
    console.log("\n🎉 Deployment completed successfully!");
    console.log("🔗 Live transaction hashes:");
    console.log("   UniversalVault:", info.contracts.UniversalVault.txHash);
    console.log("   $AUTOGEN:", info.contracts.AUTOGEN.txHash);
    process.exit(0);
  })
  .catch((error) => {
    console.error("💥 Deployment failed:", error);
    process.exit(1);
  });
