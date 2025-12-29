'use client';

interface GameCardProps {
  game: {
    gameId: string;
    team0: string;
    team1: string;
    gameDate: number;
  };
}

export default function GameCard({ game }: GameCardProps) {
  // Convert timestamp to proper date
  // gameDate is in milliseconds (from backend)
  const gameDate = new Date(game.gameDate);
  
  // Check if the date is valid
  if (isNaN(gameDate.getTime())) {
    return <div>Invalid date</div>;
  }
  
  // Format date with timezone - convert to ET (Eastern Time) for NBA games
  const formattedDate = gameDate.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
    timeZone: 'America/New_York' // NBA games are typically in ET
  });
  
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <div className="text-sm text-amber-200">
          {formattedDate}
        </div>
        <div className="text-xs text-amber-300 bg-amber-500/20 backdrop-blur-sm px-2 py-1 rounded border border-amber-400/30">
          {game.gameId}
        </div>
      </div>
      <div className="flex items-center justify-center space-x-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-amber-300">{game.team0}</div>
          <div className="text-xs text-amber-200 mt-1">Team 0</div>
        </div>
        <div className="text-3xl font-bold text-amber-300">VS</div>
        <div className="text-center">
          <div className="text-2xl font-bold text-amber-300">{game.team1}</div>
          <div className="text-xs text-amber-200 mt-1">Team 1</div>
        </div>
      </div>
    </div>
  );
}

