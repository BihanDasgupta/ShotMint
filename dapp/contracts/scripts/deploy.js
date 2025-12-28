const hre = require("hardhat");

async function main() {
  console.log("Deploying ShotMintBetting contract...");

  const ShotMintBetting = await hre.ethers.getContractFactory("ShotMintBetting");
  const betting = await ShotMintBetting.deploy();

  await betting.waitForDeployment();

  const address = await betting.getAddress();
  console.log("✅ ShotMintBetting deployed to:", address);
  console.log("\n📝 Update your frontend .env with:");
  console.log(`NEXT_PUBLIC_CONTRACT_ADDRESS=${address}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

