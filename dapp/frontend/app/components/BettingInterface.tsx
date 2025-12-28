'use client';

import { useState, useEffect } from 'react';
import { useWriteContract, useWaitForTransactionReceipt } from 'wagmi';
import { parseEther } from 'viem';
import axios from 'axios';

const CONTRACT_ADDRESS = process.env.NEXT_PUBLIC_CONTRACT_ADDRESS || '0x0000000000000000000000000000000000000000';
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ABI for the betting contract (simplified)
const CONTRACT_ABI = [
  {
    inputs: [
      { internalType: 'string', name: 'gameId', type: 'string' },
      { internalType: 'string', name: 'team', type: 'string' },
    ],
    name: 'placeBet',
    outputs: [],
    stateMutability: 'payable',
    type: 'function',
  },
] as const;

interface BettingInterfaceProps {
  game: {
    gameId: string;
    team0: string;
    team1: string;
  };
  prediction: {
    predicted_winner: string;
    team0_win_probability: number;
    team1_win_probability: number;
  };
  userAddress: string;
}

export default function BettingInterface({
  game,
  prediction,
  userAddress,
}: BettingInterfaceProps) {
  const [betAmount, setBetAmount] = useState('0.01');
  const [selectedTeam, setSelectedTeam] = useState<'TEAM0' | 'TEAM1'>(
    prediction.predicted_winner as 'TEAM0' | 'TEAM1'
  );
  const [isPlacing, setIsPlacing] = useState(false);

  // Calculate odds based on probability
  const calculateOdds = (probability: number) => {
    // Simple odds calculation: 1 / probability
    return (1 / probability).toFixed(2);
  };

  const team0Odds = calculateOdds(prediction.team0_win_probability);
  const team1Odds = calculateOdds(prediction.team1_win_probability);

  const { writeContract, data: hash, isPending: isWriteLoading } = useWriteContract();

  const { isLoading: isTxLoading, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  // Handle successful transaction
  useEffect(() => {
    if (isSuccess && hash && isPlacing) {
      (async () => {
        // Record bet in backend
        try {
          await axios.post(`${API_URL}/bets`, {
            game_id: game.gameId,
            bettor_address: userAddress,
            team: selectedTeam,
            amount: parseFloat(betAmount),
            odds: parseFloat(selectedTeam === 'TEAM0' ? team0Odds : team1Odds),
          });
        } catch (error) {
          console.error('Error recording bet:', error);
        }
        setIsPlacing(false);
        alert('Bet placed successfully!');
      })();
    }
  }, [isSuccess, hash, isPlacing, game.gameId, userAddress, selectedTeam, betAmount, team0Odds, team1Odds]);

  const handlePlaceBet = async () => {
    if (CONTRACT_ADDRESS === '0x0000000000000000000000000000000000000000') {
      alert('Please connect your wallet and ensure contract is deployed');
      return;
    }

    if (parseFloat(betAmount) <= 0) {
      alert('Please enter a valid bet amount');
      return;
    }

    setIsPlacing(true);
    try {
      writeContract({
        address: CONTRACT_ADDRESS as `0x${string}`,
        abi: CONTRACT_ABI,
        functionName: 'placeBet',
        args: [game.gameId, selectedTeam],
        value: parseEther(betAmount),
      });
    } catch (error) {
      console.error('Error placing bet:', error);
      setIsPlacing(false);
      alert('Failed to place bet');
    }
  };

  const isLoading = isWriteLoading || isTxLoading || isPlacing;

  return (
    <div className="mt-6 bg-white/5 rounded-lg p-4 border border-white/10">
      <div className="text-sm font-semibold text-blue-200 mb-4">
        💰 Place Your Bet
      </div>

      {/* Team Selection */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <button
          onClick={() => setSelectedTeam('TEAM0')}
          className={`p-3 rounded-lg border-2 transition-all ${
            selectedTeam === 'TEAM0'
              ? 'border-blue-500 bg-blue-500/20'
              : 'border-gray-600 bg-gray-700/20'
          }`}
        >
          <div className="text-white font-bold">{game.team0}</div>
          <div className="text-xs text-blue-200 mt-1">
            Odds: {team0Odds}x
          </div>
        </button>
        <button
          onClick={() => setSelectedTeam('TEAM1')}
          className={`p-3 rounded-lg border-2 transition-all ${
            selectedTeam === 'TEAM1'
              ? 'border-purple-500 bg-purple-500/20'
              : 'border-gray-600 bg-gray-700/20'
          }`}
        >
          <div className="text-white font-bold">{game.team1}</div>
          <div className="text-xs text-purple-200 mt-1">
            Odds: {team1Odds}x
          </div>
        </button>
      </div>

      {/* Bet Amount */}
      <div className="mb-4">
        <label className="block text-xs text-blue-200 mb-2">
          Bet Amount (ETH)
        </label>
        <input
          type="number"
          step="0.001"
          min="0.001"
          value={betAmount}
          onChange={(e) => setBetAmount(e.target.value)}
          className="w-full bg-gray-800 text-white rounded-lg px-4 py-2 border border-gray-600 focus:border-blue-500 focus:outline-none"
          placeholder="0.01"
        />
      </div>

      {/* Potential Payout */}
      {parseFloat(betAmount) > 0 && (
        <div className="mb-4 p-3 bg-green-500/10 rounded-lg border border-green-500/30">
          <div className="text-xs text-green-200 mb-1">Potential Payout</div>
          <div className="text-lg font-bold text-green-300">
            {(
              parseFloat(betAmount) *
              parseFloat(selectedTeam === 'TEAM0' ? team0Odds : team1Odds)
            ).toFixed(4)}{' '}
            ETH
          </div>
        </div>
      )}

      {/* Place Bet Button */}
      <button
        onClick={handlePlaceBet}
        disabled={isLoading}
        className={`w-full py-3 rounded-lg font-bold transition-all ${
          isLoading
            ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
            : 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700'
        }`}
      >
        {isLoading ? 'Processing...' : 'Place Bet'}
      </button>

      {CONTRACT_ADDRESS === '0x0000000000000000000000000000000000000000' && (
        <div className="mt-2 text-xs text-yellow-400 text-center">
          ⚠️ Contract not deployed. Update NEXT_PUBLIC_CONTRACT_ADDRESS
        </div>
      )}
    </div>
  );
}

