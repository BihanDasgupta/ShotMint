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
    <div className="mt-6 bg-emerald-500/10 backdrop-blur-xl rounded-lg p-4 border border-emerald-400/30 shadow-lg shadow-emerald-900/10">
      <div className="text-sm font-semibold text-emerald-200 mb-4">
        💰 Place Your Bet
      </div>

      {/* Team Selection */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <button
          onClick={() => setSelectedTeam('TEAM0')}
          className={`p-3 rounded-lg border-2 transition-all backdrop-blur-sm ${
            selectedTeam === 'TEAM0'
              ? 'border-emerald-500 bg-emerald-500/30 shadow-md shadow-emerald-900/20'
              : 'border-emerald-700/50 bg-emerald-900/20'
          }`}
        >
          <div className="text-amber-300 font-bold">{game.team0}</div>
          <div className="text-xs text-emerald-200 mt-1">
            Odds: {team0Odds}x
          </div>
        </button>
        <button
          onClick={() => setSelectedTeam('TEAM1')}
          className={`p-3 rounded-lg border-2 transition-all backdrop-blur-sm ${
            selectedTeam === 'TEAM1'
              ? 'border-teal-500 bg-teal-500/30 shadow-md shadow-teal-900/20'
              : 'border-teal-700/50 bg-teal-900/20'
          }`}
        >
          <div className="text-amber-300 font-bold">{game.team1}</div>
          <div className="text-xs text-teal-200 mt-1">
            Odds: {team1Odds}x
          </div>
        </button>
      </div>

      {/* Bet Amount */}
      <div className="mb-4">
        <label className="block text-xs text-emerald-200 mb-2">
          Bet Amount (ETH)
        </label>
        <input
          type="number"
          step="0.001"
          min="0.001"
          value={betAmount}
          onChange={(e) => setBetAmount(e.target.value)}
          className="w-full bg-emerald-900/30 backdrop-blur-sm text-amber-300 rounded-lg px-4 py-2 border border-emerald-600/50 focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
          placeholder="0.01"
        />
      </div>

      {/* Potential Payout */}
      {parseFloat(betAmount) > 0 && (
        <div className="mb-4 p-3 bg-emerald-500/20 backdrop-blur-sm rounded-lg border border-emerald-400/40 shadow-md shadow-emerald-900/20">
          <div className="text-xs text-emerald-200 mb-1">Potential Payout</div>
          <div className="text-lg font-bold text-emerald-300">
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
        className={`w-full py-3 rounded-lg font-bold transition-all shadow-lg ${
          isLoading
            ? 'bg-emerald-800/50 text-emerald-300/50 cursor-not-allowed'
            : 'bg-gradient-to-r from-emerald-600 to-teal-600 text-amber-300 hover:from-emerald-700 hover:to-teal-700 shadow-emerald-900/40 hover:shadow-emerald-900/60'
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

