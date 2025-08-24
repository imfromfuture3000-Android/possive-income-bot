#!/bin/bash
set -e

echo "🚀 Starting deployment to Base Sepolia..."

# Check if required environment variables are set
if [ -z "$PRIVATE_KEY" ]; then
    echo "❌ PRIVATE_KEY environment variable is required for deployment"
    exit 1
fi

if [ -z "$BASE_SEPOLIA_RPC_URL" ]; then
    echo "⚠️  Using default Base Sepolia RPC URL"
    export BASE_SEPOLIA_RPC_URL="https://sepolia.base.org"
fi

echo "🔧 Installing dependencies..."
npm install

echo "🔨 Compiling contracts..."
npx hardhat compile

echo "🌐 Deploying to Base Sepolia..."
npx hardhat run scripts/deploy.js --network base-sepolia

echo "✅ Deployment completed! Check deployment.json for transaction hashes."
