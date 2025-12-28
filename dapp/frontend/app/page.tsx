'use client';

import { useState, useEffect } from 'react';
import { useAccount, useConnect, useDisconnect } from 'wagmi';
import { ConnectButton } from '@rainbow-me/rainbowkit';
import axios from 'axios';
import GameCard from './components/GameCard';
import PredictionDisplay from './components/PredictionDisplay';
import BettingInterface from './components/BettingInterface';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const { address, isConnected } = useAccount();
  const [games, setGames] = useState<any[]>([]);
  const [predictions, setPredictions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Fetch real-time games from API
  useEffect(() => {
    const fetchGames = async () => {
      try {
        const response = await axios.get(`${API_URL}/games/upcoming?days_ahead=7`);
        if (response.data.games && response.data.games.length > 0) {
          setGames(response.data.games);
        } else {
          // Fallback to sample games if API returns empty
          console.log('No games from API, using sample data');
          setGames([
            {
              gameId: 'game_001',
              team0: 'Lakers',
              team1: 'Warriors',
              gameDate: new Date('2025-01-15').getTime(),
          team0Stats: { PTS: 115, REB: 45, AST: 28, FG_PCT: 0.48, FG3_PCT: 0.36, FT_PCT: 0.80, OREB: 11, TOV: 12 },
          team1Stats: { PTS: 112, REB: 42, AST: 25, FG_PCT: 0.46, FG3_PCT: 0.35, FT_PCT: 0.78, OREB: 10, TOV: 14 },
              team0Elo: 1600,
              team1Elo: 1650,
              team0IsHome: true,
            },
          ]);
        }
      } catch (error) {
        console.error('Error fetching games:', error);
        // Fallback to sample games on error
        setGames([
          {
            gameId: 'game_001',
            team0: 'Lakers',
            team1: 'Warriors',
            gameDate: new Date('2025-01-15').getTime(),
          team0Stats: { PTS: 115, REB: 45, AST: 28, FG_PCT: 0.48, FG3_PCT: 0.36, FT_PCT: 0.80, OREB: 11, TOV: 12 },
          team1Stats: { PTS: 112, REB: 42, AST: 25, FG_PCT: 0.46, FG3_PCT: 0.35, FT_PCT: 0.78, OREB: 10, TOV: 14 },
            team0Elo: 1600,
            team1Elo: 1650,
            team0IsHome: true,
          },
        ]);
      }
    };

    fetchGames();
    // Refresh games every 5 minutes
    const interval = setInterval(fetchGames, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchPredictions = async () => {
    if (games.length === 0) return;
    
    setLoading(true);
    try {
      // Prepare games for prediction API
      const gamesForPrediction = games.map((game) => {
        // Ensure all required fields exist with defaults
        return {
          team0_stats: game.team0Stats || { PTS: 110, REB: 44, AST: 25, FG_PCT: 0.46, FG3_PCT: 0.35, FT_PCT: 0.78, OREB: 10, TOV: 13 },
          team1_stats: game.team1Stats || { PTS: 110, REB: 44, AST: 25, FG_PCT: 0.46, FG3_PCT: 0.35, FT_PCT: 0.78, OREB: 10, TOV: 13 },
          team0_elo: game.team0Elo || 1550,
          team1_elo: game.team1Elo || 1550,
          team0_is_home: game.team0IsHome !== undefined ? game.team0IsHome : false,
          team0_name: game.team0 || 'Team 0',
          team1_name: game.team1 || 'Team 1',
          game_id: game.gameId || `game_${Date.now()}`,
        };
      });

      console.log('Fetching predictions for', gamesForPrediction.length, 'games');
      const response = await axios.post(`${API_URL}/predict/batch`, {
        games: gamesForPrediction,
      });
      
      console.log('Predictions received:', response.data);
      setPredictions(response.data);
    } catch (error: any) {
      console.error('Error fetching predictions:', error);
      console.error('Error details:', error.response?.data || error.message);
      // Set empty predictions on error so UI doesn't break
      setPredictions([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (games.length > 0) {
      console.log('Games loaded, fetching predictions...', games);
      fetchPredictions();
    }
  }, [games.length]); // Only depend on games.length to avoid infinite loops

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-5xl font-bold text-white mb-2">
                🏀 ShotMint
              </h1>
              <p className="text-xl text-blue-200">
                AI-Powered NBA Betting dApp
              </p>
            </div>
            <ConnectButton />
          </div>
        </header>

        {/* Stats Banner */}
        <div className="bg-white/10 backdrop-blur-lg rounded-lg p-6 mb-8 border border-white/20">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-white">
                {predictions.length}
              </div>
              <div className="text-blue-200">Games Analyzed</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white">
                {predictions.filter((p) => p.confidence > 0.7).length}
              </div>
              <div className="text-blue-200">High Confidence</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white">
                {isConnected ? '✅' : '❌'}
              </div>
              <div className="text-blue-200">Wallet Status</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white">RNN</div>
              <div className="text-blue-200">AI Model</div>
            </div>
          </div>
        </div>

        {/* Games Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {games.map((game, index) => {
            const prediction = predictions.find((p) => p.game_id === game.gameId);
            return (
              <div
                key={game.gameId || index}
                className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 hover:bg-white/15 transition-all"
              >
                <GameCard game={game} />
                {prediction && (
                  <div className="mt-4">
                    <PredictionDisplay prediction={prediction} />
                    {isConnected && (
                      <BettingInterface
                        game={game}
                        prediction={prediction}
                        userAddress={address || ''}
                      />
                    )}
                  </div>
                )}
                {!prediction && loading && (
                  <div className="mt-4 text-center text-blue-200">
                    🤖 Loading AI prediction...
                  </div>
                )}
                {!prediction && !loading && (
                  <div className="mt-4 space-y-2">
                    <div className="text-center text-yellow-200 text-sm bg-yellow-500/10 p-3 rounded-lg">
                      ⚠️ Prediction not available
                    </div>
                    <button
                      onClick={() => fetchPredictions()}
                      className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm"
                    >
                      🔄 Retry Prediction
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {!isConnected && (
          <div className="mt-8 bg-yellow-500/20 border border-yellow-500/50 rounded-lg p-4 text-center">
            <p className="text-yellow-200">
              🔒 Connect your wallet to place bets
            </p>
          </div>
        )}
      </div>
    </main>
  );
}

