'use client';

import { format } from 'date-fns';

interface GameCardProps {
  game: {
    gameId: string;
    team0: string;
    team1: string;
    gameDate: number;
  };
}

export default function GameCard({ game }: GameCardProps) {
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <div className="text-sm text-blue-200">
          {format(new Date(game.gameDate), 'MMM d, yyyy h:mm a')}
        </div>
        <div className="text-xs text-blue-300 bg-blue-500/20 px-2 py-1 rounded">
          {game.gameId}
        </div>
      </div>
      <div className="flex items-center justify-center space-x-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-white">{game.team0}</div>
          <div className="text-xs text-blue-200 mt-1">Team 0</div>
        </div>
        <div className="text-3xl font-bold text-blue-300">VS</div>
        <div className="text-center">
          <div className="text-2xl font-bold text-white">{game.team1}</div>
          <div className="text-xs text-blue-200 mt-1">Team 1</div>
        </div>
      </div>
    </div>
  );
}

