"""
Simple test script for the prediction API
"""
import requests
import json

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{API_URL}/health")
    print(f"Health check: {response.status_code}")
    print(response.json())
    print()

def test_prediction():
    """Test single prediction"""
    payload = {
        "team0_stats": {
            "PTS": 115.0,
            "REB": 45.0,
            "AST": 28.0,
            "FG_PCT": 0.48,
            "TOV": 12.0
        },
        "team1_stats": {
            "PTS": 112.0,
            "REB": 42.0,
            "AST": 25.0,
            "FG_PCT": 0.46,
            "TOV": 14.0
        },
        "team0_elo": 1600.0,
        "team1_elo": 1650.0,
        "team0_is_home": True,
        "team0_name": "Lakers",
        "team1_name": "Warriors"
    }
    
    response = requests.post(f"{API_URL}/predict", json=payload)
    print(f"Prediction: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def test_batch_prediction():
    """Test batch prediction"""
    payload = {
        "games": [
            {
                "team0_stats": {"PTS": 115.0, "REB": 45.0, "AST": 28.0, "FG_PCT": 0.48, "TOV": 12.0},
                "team1_stats": {"PTS": 112.0, "REB": 42.0, "AST": 25.0, "FG_PCT": 0.46, "TOV": 14.0},
                "team0_elo": 1600.0,
                "team1_elo": 1650.0,
                "team0_is_home": True,
                "team0_name": "Lakers",
                "team1_name": "Warriors",
                "game_id": "test_001"
            },
            {
                "team0_stats": {"PTS": 118.0, "REB": 48.0, "AST": 30.0, "FG_PCT": 0.50, "TOV": 10.0},
                "team1_stats": {"PTS": 110.0, "REB": 40.0, "AST": 22.0, "FG_PCT": 0.44, "TOV": 15.0},
                "team0_elo": 1700.0,
                "team1_elo": 1550.0,
                "team0_is_home": False,
                "team0_name": "Celtics",
                "team1_name": "Heat",
                "game_id": "test_002"
            }
        ]
    }
    
    response = requests.post(f"{API_URL}/predict/batch", json=payload)
    print(f"Batch Prediction: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

if __name__ == "__main__":
    print("Testing ShotMint API\n")
    print("=" * 50)
    
    try:
        test_health()
        test_prediction()
        test_batch_prediction()
        print("✅ All tests passed!")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API. Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

