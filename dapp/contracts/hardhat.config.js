require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
  networks: {
    hardhat: {
      chainId: 1337,
    },
    localhost: {
      url: "http://127.0.0.1:8545",
    },
    // Only add sepolia network if both RPC URL and private key are properly set
    // (not placeholder values)
    ...(process.env.SEPOLIA_RPC_URL && 
        process.env.PRIVATE_KEY && 
        process.env.PRIVATE_KEY.length === 66 && 
        process.env.PRIVATE_KEY.startsWith('0x') &&
        !process.env.PRIVATE_KEY.includes('YOUR') &&
        !process.env.SEPOLIA_RPC_URL.includes('YOUR') ? {
      sepolia: {
        url: process.env.SEPOLIA_RPC_URL,
        accounts: [process.env.PRIVATE_KEY],
      },
    } : {}),
  },
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts",
  },
  // Exclude node_modules from being treated as local files
  mocha: {
    timeout: 40000,
  },
};

