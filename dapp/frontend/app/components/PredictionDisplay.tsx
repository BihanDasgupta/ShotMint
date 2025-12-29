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
      <div className="text-sm font-semibold text-emerald-200 mb-2">
        🤖 AI Prediction
      </div>

      {/* Confidence Bar */}
      <div>
        <div className="flex justify-between text-xs text-emerald-300 mb-1">
          <span>Confidence</span>
          <span className={confidenceColor}>{confidenceBar}%</span>
        </div>
        <div className="w-full bg-emerald-900/40 backdrop-blur-sm rounded-full h-2.5 border border-emerald-700/30">
          <div
            className={`h-2.5 rounded-full transition-all ${
              prediction.confidence > 0.7
                ? 'bg-gradient-to-r from-emerald-500 to-green-500'
                : prediction.confidence > 0.5
                ? 'bg-gradient-to-r from-yellow-500 to-amber-500'
                : 'bg-gradient-to-r from-orange-500 to-red-500'
            }`}
            style={{ width: `${prediction.confidence * 100}%` }}
          />
        </div>
      </div>

      {/* Win Probabilities */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-emerald-500/20 backdrop-blur-sm rounded-lg p-3 border border-emerald-400/30">
          <div className="text-xs text-emerald-200 mb-1">
            {prediction.team0_name || 'Team 0'}
          </div>
          <div className="text-2xl font-bold text-amber-300">
            {(prediction.team0_win_probability * 100).toFixed(1)}%
          </div>
        </div>
        <div className="bg-teal-500/20 backdrop-blur-sm rounded-lg p-3 border border-teal-400/30">
          <div className="text-xs text-teal-200 mb-1">
            {prediction.team1_name || 'Team 1'}
          </div>
          <div className="text-2xl font-bold text-amber-300">
            {(prediction.team1_win_probability * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Predicted Winner */}
      <div className="bg-emerald-500/25 backdrop-blur-sm rounded-lg p-3 border border-emerald-400/40 shadow-md shadow-emerald-900/20">
        <div className="text-xs text-emerald-200 mb-1">Predicted Winner</div>
        <div className="text-lg font-bold text-emerald-300">
          {prediction.predicted_winner === 'TEAM0'
            ? prediction.team0_name || 'Team 0'
            : prediction.team1_name || 'Team 1'}
        </div>
      </div>
    </div>
  );
}

