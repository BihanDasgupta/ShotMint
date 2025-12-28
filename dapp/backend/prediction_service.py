"""
Prediction Service - Wraps the RNN model for making NBA game predictions
"""
import numpy as np
import pandas as pd
import joblib
import tensorflow as tf
from tensorflow.keras.models import load_model
from typing import Dict, List, Optional
import os
import logging

logger = logging.getLogger(__name__)

class PredictionService:
    """Service for making NBA game predictions using the trained RNN model"""
    
    def __init__(self, model_path: str = None, scaler_path: str = None):
        """
        Initialize the prediction service
        
        Args:
            model_path: Path to the saved RNN model (.h5 or .keras file)
            scaler_path: Path to the saved scaler (.pkl file)
        """
        # Default paths relative to project root
        if model_path is None:
            # Use the v3 model which matches the v3 scaler (7 features)
            model_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "nba_win_predictor_rnn_v3.h5"
            )
        if scaler_path is None:
            scaler_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "nba_feature_scaler_rnn_v3.pkl"
            )
        
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.model = None
        self.scaler = None
        self._load_model()
        self._load_scaler()
    
    def _load_model(self):
        """Load the trained RNN model"""
        try:
            if os.path.exists(self.model_path):
                self.model = load_model(self.model_path)
                print(f"✅ Loaded model from {self.model_path}")
            else:
                # Try alternative paths
                alt_paths = [
                    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                "models", "MintShooter-RNN.h5"),
                    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                "nba_win_predictor_rnn_v2.h5"),
                    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                "models", "MintShooter-RNN.keras"),
                ]
                for path in alt_paths:
                    if os.path.exists(path):
                        self.model = load_model(path)
                        print(f"✅ Loaded model from {path}")
                        return
                raise FileNotFoundError(f"Model not found at {self.model_path} or alternatives")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    
    def _load_scaler(self):
        """Load the feature scaler"""
        try:
            if os.path.exists(self.scaler_path):
                self.scaler = joblib.load(self.scaler_path)
                print(f"✅ Loaded scaler from {self.scaler_path}")
            else:
                # Try alternative paths
                alt_paths = [
                    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                "nba_feature_scaler_rnn_v2.pkl"),
                    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                "nba_feature_scaler_rnn.pkl"),
                ]
                for path in alt_paths:
                    if os.path.exists(path):
                        self.scaler = joblib.load(path)
                        print(f"✅ Loaded scaler from {path}")
                        return
                raise FileNotFoundError(f"Scaler not found at {self.scaler_path} or alternatives")
        except Exception as e:
            print(f"❌ Error loading scaler: {e}")
            raise
    
    def prepare_features(self, team0_stats: Dict, team1_stats: Dict, 
                        team0_elo: float, team1_elo: float, 
                        team0_is_home: bool = True) -> np.ndarray:
        """
        Prepare features for prediction
        
        Model expects 7 features (matching nba_win_predictor_rnn_v3.h5):
        1. FG_PCT_DIFF - Field goal percentage difference
        2. FG3_PCT_DIFF - 3-point percentage difference  
        3. FT_PCT_DIFF - Free throw percentage difference
        4. OREB_DIFF - Offensive rebound difference
        5. TOV_DIFF - Turnover difference
        6. ELO_DIFF - ELO rating difference
        7. TEAM0_IS_HOME - Home advantage (1 or 0)
        
        Args:
            team0_stats: Dictionary with team0 stats
            team1_stats: Dictionary with team1 stats
            team0_elo: ELO rating for team0
            team1_elo: ELO rating for team1
            team0_is_home: Whether team0 is playing at home
        
        Returns:
            Prepared feature array ready for model input
        """
        # Calculate differences (matching the model's expected features)
        fg_pct_diff = team0_stats.get('FG_PCT', 0.46) - team1_stats.get('FG_PCT', 0.46)
        fg3_pct_diff = team0_stats.get('FG3_PCT', 0.35) - team1_stats.get('FG3_PCT', 0.35)  # Default 3PT%
        ft_pct_diff = team0_stats.get('FT_PCT', 0.78) - team1_stats.get('FT_PCT', 0.78)  # Default FT%
        oreb_diff = team0_stats.get('OREB', 10) - team1_stats.get('OREB', 10)  # Default offensive rebounds
        tov_diff = team0_stats.get('TOV', 13) - team1_stats.get('TOV', 13)
        elo_diff = team0_elo - team1_elo
        team0_is_home_int = 1 if team0_is_home else 0
        
        # Create feature array in the exact order the model expects
        features = np.array([[
            fg_pct_diff,      # Feature 1: FG_PCT_DIFF
            fg3_pct_diff,     # Feature 2: FG3_PCT_DIFF
            ft_pct_diff,      # Feature 3: FT_PCT_DIFF
            oreb_diff,        # Feature 4: OREB_DIFF
            tov_diff,         # Feature 5: TOV_DIFF
            elo_diff,         # Feature 6: ELO_DIFF
            team0_is_home_int # Feature 7: TEAM0_IS_HOME
        ]])
        
        # Scale features using the scaler
        features_scaled = self.scaler.transform(features)
        
        # Reshape for RNN (batch_size, timesteps, features)
        # Model expects shape: (batch, 1, 7)
        features_rnn = features_scaled.reshape((1, 1, features_scaled.shape[1]))
        
        return features_rnn
    
    def predict(self, team0_stats: Dict, team1_stats: Dict, 
                team0_elo: float, team1_elo: float, 
                team0_is_home: bool = True) -> Dict:
        """
        Make a prediction for a game
        
        Args:
            team0_stats: Dictionary with team0 stats
            team1_stats: Dictionary with team1 stats
            team0_elo: ELO rating for team0
            team1_elo: ELO rating for team1
            team0_is_home: Whether team0 is playing at home
        
        Returns:
            Dictionary with prediction results
        """
        # Prepare features
        X = self.prepare_features(team0_stats, team1_stats, team0_elo, team1_elo, team0_is_home)
        
        # Make prediction
        prediction = self.model.predict(X, verbose=0)[0][0]
        
        # Determine predicted winner
        predicted_winner = "TEAM0" if prediction >= 0.5 else "TEAM1"
        
        # Base confidence from model prediction (how far from 50/50)
        base_confidence = abs(prediction - 0.5) * 2  # Convert to 0-1 scale
        
        # Enhance confidence based on ELO difference (larger ELO gap = higher confidence)
        elo_diff = abs(team0_elo - team1_elo)
        # Normalize ELO difference (typical range: 0-300, max ~500)
        # ELO difference of 100+ points is significant
        elo_confidence_boost = min(elo_diff / 200.0, 0.2)  # Max 20% boost
        
        # Combine base confidence with ELO-based boost
        enhanced_confidence = min(base_confidence + elo_confidence_boost, 1.0)
        
        return {
            "team0_win_probability": float(prediction),
            "team1_win_probability": float(1 - prediction),
            "predicted_winner": predicted_winner,
            "confidence": float(enhanced_confidence),
            "raw_prediction": float(prediction),
            "elo_difference": float(elo_diff)  # Include ELO diff for transparency
        }
    
    def predict_batch(self, games: List[Dict]) -> List[Dict]:
        """
        Make predictions for multiple games
        
        Args:
            games: List of game dictionaries, each with team0_stats, team1_stats, 
                   team0_elo, team1_elo, team0_is_home
        
        Returns:
            List of prediction dictionaries
        """
        predictions = []
        print(f"predict_batch called with {len(games)} games")
        for i, game in enumerate(games):
            try:
                # Validate required fields
                if not isinstance(game.get('team0_stats'), dict):
                    logger.warning(f"Game {i} missing team0_stats: {game.get('team0_stats')}")
                    continue
                if not isinstance(game.get('team1_stats'), dict):
                    logger.warning(f"Game {i} missing team1_stats: {game.get('team1_stats')}")
                    continue
                
                print(f"Predicting game {i}: {game.get('team0_name')} vs {game.get('team1_name')}")
                pred = self.predict(
                    game['team0_stats'],
                    game['team1_stats'],
                    game.get('team0_elo', 1550),
                    game.get('team1_elo', 1550),
                    game.get('team0_is_home', True)
                )
                pred['game_id'] = game.get('game_id', f'game_{i}')
                pred['team0_name'] = game.get('team0_name', 'TEAM0')
                pred['team1_name'] = game.get('team1_name', 'TEAM1')
                predictions.append(pred)
                print(f"✅ Prediction {i} successful: {pred.get('predicted_winner')} ({pred.get('confidence', 0):.2%} confidence)")
            except Exception as e:
                logger.error(f"Error predicting game {i}: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                # Continue with next game instead of failing completely
                continue
        
        print(f"Returning {len(predictions)} predictions")
        return predictions

