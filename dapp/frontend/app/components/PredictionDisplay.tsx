'use client';

interface PredictionDisplayProps {
  prediction: {
    team0_win_probability: number;
    team1_win_probability: number;
    predicted_winner: string;
    confidence: number;
    team0_name?: string;
    team1_name?: string;
  };
}

export default function PredictionDisplay({ prediction }: PredictionDisplayProps) {
  const confidenceColor =
    prediction.confidence > 0.7
      ? 'text-green-400'
      : prediction.confidence > 0.5
      ? 'text-yellow-400'
      : 'text-orange-400';

  const confidenceBar = (prediction.confidence * 100).toFixed(1);

  return (
    <div className="mt-4 space-y-3">
      <div className="text-sm font-semibold text-blue-200 mb-2">
        🤖 AI Prediction
      </div>

      {/* Confidence Bar */}
      <div>
        <div className="flex justify-between text-xs text-blue-300 mb-1">
          <span>Confidence</span>
          <span className={confidenceColor}>{confidenceBar}%</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2">
          <div
            className={`h-2 rounded-full ${
              prediction.confidence > 0.7
                ? 'bg-green-500'
                : prediction.confidence > 0.5
                ? 'bg-yellow-500'
                : 'bg-orange-500'
            }`}
            style={{ width: `${prediction.confidence * 100}%` }}
          />
        </div>
      </div>

      {/* Win Probabilities */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-blue-500/20 rounded-lg p-3">
          <div className="text-xs text-blue-200 mb-1">
            {prediction.team0_name || 'Team 0'}
          </div>
          <div className="text-2xl font-bold text-white">
            {(prediction.team0_win_probability * 100).toFixed(1)}%
          </div>
        </div>
        <div className="bg-purple-500/20 rounded-lg p-3">
          <div className="text-xs text-purple-200 mb-1">
            {prediction.team1_name || 'Team 1'}
          </div>
          <div className="text-2xl font-bold text-white">
            {(prediction.team1_win_probability * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Predicted Winner */}
      <div className="bg-green-500/20 rounded-lg p-3 border border-green-500/30">
        <div className="text-xs text-green-200 mb-1">Predicted Winner</div>
        <div className="text-lg font-bold text-green-300">
          {prediction.predicted_winner === 'TEAM0'
            ? prediction.team0_name || 'Team 0'
            : prediction.team1_name || 'Team 1'}
        </div>
      </div>
    </div>
  );
}

