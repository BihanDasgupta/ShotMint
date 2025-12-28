"""
Enhanced NBA Service - Alternative implementation using nba_api library
Install with: pip install nba-api
"""
try:
    from nba_api.stats.endpoints import scoreboard, schedule
    from nba_api.stats.static import teams
    NBA_API_AVAILABLE = True
except ImportError:
    NBA_API_AVAILABLE = False
    print("nba-api library not installed. Install with: pip install nba-api")
    print("Falling back to direct API calls...")

from typing import List, Dict
from datetime import datetime, timedelta

class EnhancedNBAService:
    """Enhanced NBA service using nba_api library (better for schedules)"""
    
    def __init__(self):
        self.use_library = NBA_API_AVAILABLE
    
    def get_upcoming_games(self, days_ahead: int = 7) -> List[Dict]:
        """Get upcoming games using nba_api library if available"""
        if not self.use_library:
            return []
        
        try:
            today = datetime.now()
            upcoming_games = []
            
            # Get current season
            if today.month >= 10:
                season = f"{today.year}-{str(today.year + 1)[2:]}"
            else:
                season = f"{today.year - 1}-{str(today.year)[2:]}"
            
            # Try to get schedule
            try:
                schedule_data = schedule.Schedule(season=season)
                schedule_df = schedule_data.get_data_frames()[0]
                
                # Filter for upcoming games
                for _, row in schedule_df.iterrows():
                    game_date_str = row.get('GAME_DATE', '')
                    if not game_date_str:
                        continue
                    
                    try:
                        game_date = datetime.strptime(game_date_str, '%Y-%m-%dT%H:%M:%S')
                        if game_date > today and (game_date - today).days <= days_ahead:
                            # This is an upcoming game
                            home_team = row.get('HOME_TEAM_NAME', '')
                            visitor_team = row.get('VISITOR_TEAM_NAME', '')
                            
                            # Convert team names to abbreviations
                            home_abbr = self._team_name_to_abbr(home_team)
                            visitor_abbr = self._team_name_to_abbr(visitor_team)
                            
                            if home_abbr and visitor_abbr:
                                game = {
                                    'gameId': str(row.get('GAME_ID', '')),
                                    'team0': visitor_abbr,
                                    'team1': home_abbr,
                                    'gameDate': int(game_date.timestamp() * 1000),
                                    'team0Stats': self._get_default_stats(),
                                    'team1Stats': self._get_default_stats(),
                                    'team0Elo': 1550,  # Default, can be enhanced
                                    'team1Elo': 1550,
                                    'team0IsHome': False,
                                    'team1IsHome': True,
                                    'status': 'Scheduled',
                                }
                                upcoming_games.append(game)
                    except:
                        continue
                
                # Sort by date
                upcoming_games.sort(key=lambda x: x.get('gameDate', 0))
                return upcoming_games[:10]  # Limit to 10 games
                
            except Exception as e:
                print(f"Error getting schedule: {e}")
                return []
                
        except Exception as e:
            print(f"Error in enhanced service: {e}")
            return []
    
    def _team_name_to_abbr(self, team_name: str) -> str:
        """Convert team name to abbreviation"""
        if not team_name:
            return None
        
        team_map = {
            'Atlanta Hawks': 'ATL', 'Boston Celtics': 'BOS', 'Brooklyn Nets': 'BKN',
            'Charlotte Hornets': 'CHA', 'Chicago Bulls': 'CHI', 'Cleveland Cavaliers': 'CLE',
            'Dallas Mavericks': 'DAL', 'Denver Nuggets': 'DEN', 'Detroit Pistons': 'DET',
            'Golden State Warriors': 'GSW', 'Houston Rockets': 'HOU', 'Indiana Pacers': 'IND',
            'LA Clippers': 'LAC', 'Los Angeles Lakers': 'LAL', 'Memphis Grizzlies': 'MEM',
            'Miami Heat': 'MIA', 'Milwaukee Bucks': 'MIL', 'Minnesota Timberwolves': 'MIN',
            'New Orleans Pelicans': 'NOP', 'New York Knicks': 'NYK', 'Oklahoma City Thunder': 'OKC',
            'Orlando Magic': 'ORL', 'Philadelphia 76ers': 'PHI', 'Phoenix Suns': 'PHX',
            'Portland Trail Blazers': 'POR', 'Sacramento Kings': 'SAC', 'San Antonio Spurs': 'SAS',
            'Toronto Raptors': 'TOR', 'Utah Jazz': 'UTA', 'Washington Wizards': 'WAS',
        }
        return team_map.get(team_name)
    
    def _get_default_stats(self) -> Dict:
        """Get default team stats"""
        return {
            'PTS': 110.0,
            'REB': 44.0,
            'AST': 25.0,
            'FG_PCT': 0.46,
            'TOV': 13.0,
        }

