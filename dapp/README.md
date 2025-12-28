# ShotMint - Complete Setup Guide

A decentralized application (dApp) that wraps around an RNN model made by the creator from scratch, MintShooteRNN, for NBA game predictions and enables users to place bets through wallet and smart contract integration.

## 🏗️ Architecture

The dApp consists of three main components:

1. **Backend API** (FastAPI) - Serves RNN model predictions
2. **Smart Contracts** (Solidity) - Handles betting logic on-chain
3. **Frontend** (Next.js + React) - User interface with wallet integration

## 📁 Project Structure

```
dapp/
├── backend/              # FastAPI backend
│   ├── main.py          # API endpoints
│   ├── prediction_service.py  # RNN model wrapper
│   └── requirements.txt
├── contracts/            # Smart contracts
│   ├── ShotMintBetting.sol
│   ├── hardhat.config.js
│   ├── package.json
│   └── scripts/
│       └── deploy.js
└── frontend/             # Next.js frontend
    ├── app/
    │   ├── components/
    │   ├── page.tsx
    │   ├── layout.tsx
    │   └── providers.tsx
    ├── package.json
    └── next.config.js
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn
- MetaMask or compatible Web3 wallet

### 1. Backend Setup

```bash
cd dapp/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the API server
python main.py
```

The API will be available at `http://localhost:8000`

### 2. Smart Contracts Setup

```bash
cd dapp/contracts

# Install dependencies
npm install

# Compile contracts
npm run compile

# Deploy to local network (requires Hardhat node running)
npm run deploy:local

# Or deploy to Sepolia testnet
# First, create .env file with:
# SEPOLIA_RPC_URL=your_rpc_url
# PRIVATE_KEY=your_private_key
npm run deploy:sepolia
```

**Note:** Make sure to copy the deployed contract address and update it in the frontend `.env` file.

### 3. Frontend Setup

```bash
cd dapp/frontend

# Install dependencies
npm install

# Create .env.local file (copy from .env.example)
cp .env.example .env.local

# Update .env.local with:
# - WalletConnect Project ID (get from https://cloud.walletconnect.com)
# - API URL (default: http://localhost:8000)
# - Contract address (from deployment step)

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 🔧 Configuration

### Backend Configuration

The prediction service automatically looks for:
- Model: `models/MintShooter-RNN.h5` or `nba_win_predictor_rnn_v3.h5`
- Scaler: `nba_feature_scaler_rnn_v3.pkl`

Update paths in `prediction_service.py` if your files are in different locations.

### Frontend Configuration

Update `.env.local`:
```env
NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID=your-project-id
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CONTRACT_ADDRESS=0x...
```

## 📡 API Endpoints

### `POST /predict`
Make a single game prediction

**Request:**
```json
{
  "team0_stats": {
    "PTS": 115,
    "REB": 45,
    "AST": 28,
    "FG_PCT": 0.48,
    "TOV": 12
  },
  "team1_stats": {
    "PTS": 112,
    "REB": 42,
    "AST": 25,
    "FG_PCT": 0.46,
    "TOV": 14
  },
  "team0_elo": 1600,
  "team1_elo": 1650,
  "team0_is_home": true,
  "team0_name": "Lakers",
  "team1_name": "Warriors"
}
```

**Response:**
```json
{
  "team0_win_probability": 0.65,
  "team1_win_probability": 0.35,
  "predicted_winner": "TEAM0",
  "confidence": 0.30,
  "raw_prediction": 0.65
}
```

### `POST /predict/batch`
Make predictions for multiple games

### `POST /bets`
Create a new bet record

### `GET /bets`
List all bets (optionally filtered by bettor address)

## 🔐 Smart Contract Functions

### `createGame(gameId, team0, team1, gameDate, team0WinProbability)`
Create a new game with predictions (owner only)

### `placeBet(gameId, team)`
Place a bet on a game (payable function)

### `resolveGame(gameId, winner)`
Resolve a game and calculate payouts (owner only)

### `getBet(betId)`
Get bet details

### `getUserBets(user)`
Get all bets for a user

## 🎨 Features

- **AI Predictions**: Real-time predictions using the trained RNN model
- **Wallet Integration**: Connect with MetaMask, WalletConnect, and more via RainbowKit
- **Smart Contract Betting**: Decentralized betting on-chain
- **Real-time Odds**: Dynamic odds calculation based on AI predictions
- **Bet History**: Track all your bets
- **Responsive UI**: Modern, mobile-friendly interface

## 🔄 Workflow

1. **User connects wallet** → Frontend detects connection
2. **View predictions** → Backend serves RNN predictions via API
3. **Select game & team** → User chooses bet
4. **Place bet** → Transaction sent to smart contract
5. **Game resolves** → Owner calls `resolveGame()` to distribute payouts

## 🧪 Testing

### Backend
```bash
cd dapp/backend
pytest  # (if tests are added)
```

### Contracts
```bash
cd dapp/contracts
npm test
```

### Frontend
```bash
cd dapp/frontend
npm test
```

## 🚨 Important Notes

1. **Model Files**: Ensure the RNN model and scaler files are in the correct locations
2. **Contract Deployment**: Always deploy to testnet first before mainnet
3. **Security**: Never commit private keys or sensitive data
4. **Gas Costs**: Betting transactions require ETH for gas fees
5. **House Edge**: The contract includes a 5% house edge (configurable)

## 🔮 Future Enhancements

- [ ] Oracle integration for automatic game resolution
- [ ] Multi-token support (USDC, DAI, etc.)
- [ ] Betting pools and parlay bets
- [ ] Leaderboard and rewards system
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard

