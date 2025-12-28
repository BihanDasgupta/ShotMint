"""
FastAPI Backend for ShotMint dApp
Serves predictions and manages betting data
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from prediction_service import PredictionService
from nba_service import NBAService
import os

app = FastAPI(title="ShotMint API", version="1.0.0")

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
prediction_service = PredictionService()
nba_service = NBAService()

# Request/Response Models
class TeamStats(BaseModel):
    # Core stats
    PTS: float = 0.0
    REB: float = 0.0
    AST: float = 0.0
    FG_PCT: float = 0.0
    TOV: float = 0.0
    # Additional stats needed for model (7 features)
    FG3_PCT: float = 0.35  # 3-point percentage (default NBA average)
    FT_PCT: float = 0.78   # Free throw percentage (default NBA average)
    OREB: float = 10.0     # Offensive rebounds (default NBA average)

class PredictionRequest(BaseModel):
    team0_stats: TeamStats
    team1_stats: TeamStats
    team0_elo: float
    team1_elo: float
    team0_is_home: bool = True
    team0_name: Optional[str] = "TEAM0"
    team1_name: Optional[str] = "TEAM1"
    game_id: Optional[str] = None

class BatchPredictionRequest(BaseModel):
    games: List[PredictionRequest]

class PredictionResponse(BaseModel):
    team0_win_probability: float
    team1_win_probability: float
    predicted_winner: str
    confidence: float
    raw_prediction: float
    team0_name: Optional[str] = None
    team1_name: Optional[str] = None
    game_id: Optional[str] = None

class BetRequest(BaseModel):
    game_id: str
    bettor_address: str
    team: str  # "TEAM0" or "TEAM1"
    amount: float  # Amount in ETH or native token
    odds: float  # Odds multiplier

class BetResponse(BaseModel):
    bet_id: str
    game_id: str
    bettor_address: str
    team: str
    amount: float
    odds: float
    timestamp: int

# In-memory storage for bets (in production, use a database)
bets_db: Dict[str, BetResponse] = {}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "ShotMint Prediction API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Make a single game prediction
    """
    try:
        # Pydantic 2.5.0 uses model_dump()
        team0_stats = request.team0_stats.model_dump()
        team1_stats = request.team1_stats.model_dump()
        
        result = prediction_service.predict(
            team0_stats=team0_stats,
            team1_stats=team1_stats,
            team0_elo=request.team0_elo,
            team1_elo=request.team1_elo,
            team0_is_home=request.team0_is_home
        )
        result["team0_name"] = request.team0_name
        result["team1_name"] = request.team1_name
        result["game_id"] = request.game_id
        return PredictionResponse(**result)
    except Exception as e:
        import traceback
        print(f"ERROR in single prediction: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/predict/batch", response_model=List[PredictionResponse])
async def predict_batch(request: BatchPredictionRequest):
    """
    Make predictions for multiple games
    """
    try:
        games = []
        for game in request.games:
            # Pydantic 2.5.0 uses model_dump()
            games.append({
                "team0_stats": game.team0_stats.model_dump(),
                "team1_stats": game.team1_stats.model_dump(),
                "team0_elo": game.team0_elo,
                "team1_elo": game.team1_elo,
                "team0_is_home": game.team0_is_home,
                "team0_name": game.team0_name,
                "team1_name": game.team1_name,
                "game_id": game.game_id
            })
        
        print(f"Making predictions for {len(games)} games...")
        print(f"First game sample: {games[0] if games else 'No games'}")
        results = prediction_service.predict_batch(games)
        print(f"Successfully generated {len(results)} predictions")
        if results:
            print(f"First result sample: {results[0]}")
        else:
            print("WARNING: predict_batch returned empty list!")
        return [PredictionResponse(**result) for result in results]
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR in batch prediction: {str(e)}")
        print(f"Traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")

@app.post("/bets", response_model=BetResponse)
async def create_bet(bet: BetRequest):
    """
    Create a new bet (stores in memory, in production this would interact with smart contract)
    """
    import time
    bet_id = f"bet_{int(time.time())}_{bet.bettor_address[:8]}"
    
    bet_response = BetResponse(
        bet_id=bet_id,
        game_id=bet.game_id,
        bettor_address=bet.bettor_address,
        team=bet.team,
        amount=bet.amount,
        odds=bet.odds,
        timestamp=int(time.time())
    )
    
    bets_db[bet_id] = bet_response
    return bet_response

@app.get("/bets/{bet_id}", response_model=BetResponse)
async def get_bet(bet_id: str):
    """Get a bet by ID"""
    if bet_id not in bets_db:
        raise HTTPException(status_code=404, detail="Bet not found")
    return bets_db[bet_id]

@app.get("/bets", response_model=List[BetResponse])
async def list_bets(bettor_address: Optional[str] = None):
    """List all bets, optionally filtered by bettor address"""
    bets = list(bets_db.values())
    if bettor_address:
        bets = [bet for bet in bets if bet.bettor_address.lower() == bettor_address.lower()]
    return bets

@app.get("/games/upcoming")
async def get_upcoming_games(days_ahead: int = 7):
    """
    Get upcoming NBA games with real-time data
    
    Args:
        days_ahead: Number of days to look ahead for games (default: 7)
    
    Returns:
        List of upcoming games with team stats and ELO ratings
    """
    try:
        games = nba_service.get_upcoming_games(days_ahead=days_ahead)
        
        # If no games found, return empty list (frontend will handle gracefully)
        if not games:
            return {
                "games": [],
                "message": "No upcoming games found. Check NBA schedule or try again later."
            }
        
        return {
            "games": games,
            "count": len(games),
            "message": f"Found {len(games)} upcoming game(s)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching games: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

