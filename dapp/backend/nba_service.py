"""
NBA API Service - Fetches real-time game data from NBA API
NO API KEY REQUIRED - Free public API
"""
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone
import os
import logging
import pandas as pd
try:
    from zoneinfo import ZoneInfo
except ImportError:
    # Python < 3.9 fallback
    try:
        from backports.zoneinfo import ZoneInfo
    except ImportError:
        ZoneInfo = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NBAService:
    """Service for fetching NBA game data"""
    
    def __init__(self):
        # NBA API endpoints (free, no API key required)
        self.base_url = "https://stats.nba.com/stats"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nba.com/',
        }
        # Load ELO data once at initialization
        self.elo_data = self._load_elo_data()
    
    def get_upcoming_games(self, days_ahead: int = 7) -> List[Dict]:
        """
        Fetch upcoming NBA games (future games only, not past)
        
        Args:
            days_ahead: Number of days to look ahead for games
        
        Returns:
            List of game dictionaries with team info, dates, and stats
        """
        try:
            today = datetime.now()
            upcoming_games = []
            
            # Try using schedule endpoint first (better for upcoming games)
            schedule_games = self._get_schedule_games(days_ahead)
            if schedule_games:
                return schedule_games
            
            # Fallback: Fetch games for each day in the range
            print(f"Trying scoreboard endpoint for next {days_ahead} days...")
            for day_offset in range(days_ahead + 1):
                game_date = today + timedelta(days=day_offset)
                date_str = game_date.strftime('%m/%d/%Y')
                
                # NBA API endpoint for scoreboard
                url = f"{self.base_url}/scoreboardV2"
                params = {
                    'DayOffset': str(day_offset),
                    'LeagueID': '00',
                    'gameDate': date_str
                }
                
                try:
                    response = requests.get(url, headers=self.headers, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        games = self._parse_scoreboard(data, game_date)
                        # Filter to only include future games (not past/completed)
                        for game in games:
                            game_timestamp = game.get('gameDate', 0)
                            if game_timestamp > int(today.timestamp() * 1000):
                                upcoming_games.append(game)
                except Exception as e:
                    logger.warning(f"Error fetching games for {date_str}: {e}")
                    continue
            
            # Remove duplicates and sort by date
            seen_ids = set()
            unique_games = []
            for game in upcoming_games:
                if game['gameId'] not in seen_ids:
                    seen_ids.add(game['gameId'])
                    unique_games.append(game)
            
            # Sort by game date
            unique_games.sort(key=lambda x: x.get('gameDate', 0))
            
            if unique_games:
                logger.info(f"Found {len(unique_games)} upcoming games from API")
                return unique_games
            else:
                logger.warning("No upcoming games found from API - this might be because:")
                logger.warning("1. NBA season hasn't started yet")
                logger.warning("2. We're in off-season")
                logger.warning("3. Schedule not published for future dates")
                logger.warning("4. API temporarily unavailable")
                logger.info("Using fallback sample games...")
                return self._get_games_fallback(days_ahead)
                
        except Exception as e:
            logger.error(f"Error fetching NBA games: {e}")
            return self._get_games_fallback(days_ahead)
    
    def _get_schedule_games(self, days_ahead: int) -> List[Dict]:
        """Try to get games from schedule endpoint"""
        try:
            today = datetime.now()
            # Calculate current season
            if today.month >= 10:  # October onwards = new season
                season = f"{today.year}-{str(today.year + 1)[2:]}"
            else:
                season = f"{today.year - 1}-{str(today.year)[2:]}"
            
            # Try schedule endpoint
            url = f"{self.base_url}/scoreboardV2"
            # Get today's games first
            params = {
                'DayOffset': '0',
                'LeagueID': '00',
                'gameDate': today.strftime('%m/%d/%Y')
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Check if we got any games
                result_sets = data.get('resultSets', [])
                if result_sets:
                    game_header = None
                    for rs in result_sets:
                        if rs.get('name') == 'GameHeader':
                            game_header = rs
                            break
                    
                    if game_header and len(game_header.get('rowSet', [])) > 0:
                        # We got games, parse them
                        games = self._parse_scoreboard(data, today)
                        upcoming = [g for g in games if g.get('gameDate', 0) > int(today.timestamp() * 1000)]
                        if upcoming:
                            return upcoming
            
            return []
        except Exception as e:
            print(f"Error in schedule endpoint: {e}")
            return []
    
    def _parse_scoreboard(self, data: Dict, target_date: datetime = None) -> List[Dict]:
        """Parse NBA scoreboard API response - only returns upcoming games"""
        games = []
        
        try:
            result_sets = data.get('resultSets', [])
            if not result_sets:
                return []
            
            # Find the game header result set
            game_header = None
            for rs in result_sets:
                if rs.get('name') == 'GameHeader':
                    game_header = rs
                    break
            
            if not game_header:
                return []
            
            headers = game_header.get('headers', [])
            rows = game_header.get('rowSet', [])
            today = datetime.now()
            
            for row in rows:
                game_dict = dict(zip(headers, row))
                
                # Extract game info
                game_id = str(game_dict.get('GAME_ID', ''))
                game_date_str = game_dict.get('GAME_DATE_EST', '')
                # Try to get game time - NBA API might have START_TIME_EST or GAME_TIME_EST
                game_time_str = game_dict.get('START_TIME_EST', '') or game_dict.get('GAME_TIME_EST', '')
                game_status = game_dict.get('GAME_STATUS_TEXT', '')
                home_team_id = game_dict.get('HOME_TEAM_ID', '')
                visitor_team_id = game_dict.get('VISITOR_TEAM_ID', '')
                
                # Parse game date with time if available
                game_date = self._parse_date_with_time(game_date_str, game_time_str)
                game_datetime = datetime.fromtimestamp(game_date / 1000)
                
                # Only include games that are in the future (upcoming)
                # Exclude completed games (status like "Final", "Final/OT", etc.)
                if game_datetime <= today and ('Final' in game_status or game_status == ''):
                    continue  # Skip past/completed games
                
                # Get team abbreviations
                home_team = self._get_team_abbreviation(home_team_id)
                visitor_team = self._get_team_abbreviation(visitor_team_id)
                
                if home_team and visitor_team:
                    # Get team stats (season averages)
                    home_stats = self._get_team_season_stats(home_team_id)
                    visitor_stats = self._get_team_season_stats(visitor_team_id)
                    
                    # Get ELO ratings (you can enhance this with your ELO data)
                    home_elo = self._get_team_elo(home_team)
                    visitor_elo = self._get_team_elo(visitor_team)
                    
                    game = {
                        'gameId': game_id,
                        'team0': visitor_team,
                        'team1': home_team,
                        'gameDate': game_date,
                        'team0Stats': visitor_stats,
                        'team1Stats': home_stats,
                        'team0Elo': visitor_elo,
                        'team1Elo': home_elo,
                        'team0IsHome': False,
                        'team1IsHome': True,
                        'status': game_status,  # Add status for filtering
                    }
                    games.append(game)
            
            return games
            
        except Exception as e:
            print(f"Error parsing scoreboard: {e}")
            return []
    
    def _get_team_abbreviation(self, team_id: int) -> Optional[str]:
        """Map team ID to abbreviation"""
        team_map = {
            1610612737: 'ATL', 1610612738: 'BOS', 1610612751: 'BKN', 1610612766: 'CHA',
            1610612741: 'CHI', 1610612739: 'CLE', 1610612742: 'DAL', 1610612743: 'DEN',
            1610612765: 'DET', 1610612744: 'GSW', 1610612745: 'HOU', 1610612754: 'IND',
            1610612746: 'LAC', 1610612747: 'LAL', 1610612763: 'MEM', 1610612748: 'MIA',
            1610612749: 'MIL', 1610612750: 'MIN', 1610612740: 'NOP', 1610612752: 'NYK',
            1610612760: 'OKC', 1610612753: 'ORL', 1610612755: 'PHI', 1610612756: 'PHX',
            1610612757: 'POR', 1610612758: 'SAC', 1610612759: 'SAS', 1610612761: 'TOR',
            1610612762: 'UTA', 1610612764: 'WAS',
        }
        return team_map.get(team_id)
    
    def _get_team_season_stats(self, team_id: int) -> Dict:
        """Get team season average stats"""
        # This is a simplified version - in production, fetch from NBA API
        # For now, return reasonable defaults based on team performance
        # Model needs: FG_PCT, FG3_PCT, FT_PCT, OREB, TOV
        return {
            'PTS': 110.0,      # Average NBA team points
            'REB': 44.0,       # Average rebounds
            'AST': 25.0,       # Average assists
            'FG_PCT': 0.46,    # Average field goal percentage
            'FG3_PCT': 0.35,   # Average 3-point percentage
            'FT_PCT': 0.78,    # Average free throw percentage
            'OREB': 10.0,      # Average offensive rebounds
            'TOV': 13.0,       # Average turnovers
        }
    
    def _load_elo_data(self) -> Optional[pd.DataFrame]:
        """Load ELO data from CSV file"""
        try:
            # Try to load the ELO CSV file
            elo_paths = [
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                            "nba_elo_2025_only.csv"),
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                            "nba_elo.csv"),
            ]
            
            for elo_path in elo_paths:
                if os.path.exists(elo_path):
                    df = pd.read_csv(elo_path)
                    logger.info(f"✅ Loaded ELO data from {elo_path} ({len(df)} records)")
                    return df
            
            logger.warning("ELO data file not found, using default ELO ratings")
            return None
        except Exception as e:
            logger.warning(f"Error loading ELO data: {e}, using default ELO ratings")
            return None
    
    def _get_team_elo(self, team_abbr: str) -> float:
        """Get team ELO rating from your ELO data (most recent by date)"""
        if self.elo_data is not None:
            try:
                # Get all ELO records for this team
                team_elos = self.elo_data[
                    self.elo_data['TEAM_ABBREVIATION'] == team_abbr
                ].copy()
                
                if not team_elos.empty:
                    # Sort by date to get the most recent
                    if 'GAME_DATE' in team_elos.columns:
                        team_elos['GAME_DATE'] = pd.to_datetime(team_elos['GAME_DATE'])
                        team_elos = team_elos.sort_values('GAME_DATE', ascending=False)
                    
                    # Get the most recent ELO (first row after sorting)
                    latest_elo = team_elos.iloc[0]
                    
                    # Check which column has ELO (could be 'ELO' or 'elo_i')
                    elo_value = None
                    if 'ELO' in latest_elo:
                        elo_value = float(latest_elo['ELO'])
                    elif 'elo_i' in latest_elo:
                        elo_value = float(latest_elo['elo_i'])
                    
                    if elo_value is not None:
                        logger.debug(f"Found ELO for {team_abbr}: {elo_value:.2f}")
                        return elo_value
            except Exception as e:
                logger.warning(f"Error getting ELO for {team_abbr}: {e}")
        
        # Fallback to default ELO ratings
        default_elos = {
            'BOS': 1700, 'DEN': 1680, 'MIL': 1650, 'PHI': 1630,
            'GSW': 1620, 'LAL': 1600, 'MIA': 1580, 'PHX': 1570,
            'MIN': 1650, 'OKC': 1640, 'CLE': 1620, 'NYK': 1610,
            'ORL': 1600, 'IND': 1590, 'DAL': 1580, 'SAC': 1570,
        }
        default_elo = default_elos.get(team_abbr, 1550)
        logger.debug(f"Using default ELO for {team_abbr}: {default_elo}")
        return default_elo
    
    def _parse_date(self, date_str: str) -> int:
        """Parse date string to timestamp, including time component"""
        return self._parse_date_with_time(date_str, '')
    
    def _parse_date_with_time(self, date_str: str, time_str: str = '') -> int:
        """Parse date string to timestamp, including time component if provided"""
        try:
            # Parse the date part
            if not date_str:
                raise ValueError("Empty date string")
            
            # GAME_DATE_EST format is typically "2024-12-24" (date only)
            # Try different date formats
            dt = None
            date_formats = [
                '%Y-%m-%d',           # 2024-12-24
                '%Y-%m-%dT%H:%M:%S',  # 2024-12-24T19:30:00
                '%m/%d/%Y',           # 12/24/2024
            ]
            
            for fmt in date_formats:
                try:
                    dt = datetime.strptime(date_str.split('T')[0].split(' ')[0], fmt)
                    break
                except:
                    continue
            
            if dt is None:
                raise ValueError(f"Could not parse date: {date_str}")
            
            # If time string is provided, parse it
            if time_str:
                try:
                    # Time format might be "7:00 PM ET" or "19:00:00" or "7:00PM"
                    time_str_clean = time_str.upper().replace('ET', '').replace('EST', '').strip()
                    if 'PM' in time_str_clean or 'AM' in time_str_clean:
                        # Parse 12-hour format
                        try:
                            time_part = datetime.strptime(time_str_clean, '%I:%M %p').time()
                            dt = dt.replace(hour=time_part.hour, minute=time_part.minute, second=0)
                        except:
                            # Try without space
                            time_part = datetime.strptime(time_str_clean.replace(' ', ''), '%I:%M%p').time()
                            dt = dt.replace(hour=time_part.hour, minute=time_part.minute, second=0)
                    else:
                        # Parse 24-hour format
                        time_parts = time_str_clean.split(':')
                        if len(time_parts) >= 2:
                            hour = int(time_parts[0])
                            minute = int(time_parts[1])
                            dt = dt.replace(hour=hour, minute=minute, second=0)
                except Exception as e:
                    logger.debug(f"Could not parse time '{time_str}', using default: {e}")
                    # Default to 7:00 PM ET if time parsing fails
                    dt = dt.replace(hour=19, minute=0, second=0)
            else:
                # No time provided, default to 7:00 PM ET (typical NBA game time)
                dt = dt.replace(hour=19, minute=0, second=0)
            
            # Make datetime timezone-aware (ET/EST)
            if ZoneInfo:
                # Use zoneinfo (Python 3.9+)
                dt_et = dt.replace(tzinfo=ZoneInfo('America/New_York'))
                return int(dt_et.timestamp() * 1000)
            else:
                # Fallback: assume ET is UTC-5 (EST) or UTC-4 (EDT)
                # For simplicity, use UTC-5 (EST) - this is approximate
                dt_utc = dt.replace(tzinfo=timezone(timedelta(hours=-5)))
                return int(dt_utc.timestamp() * 1000)
        except Exception as e:
            logger.warning(f"Error parsing date '{date_str}' with time '{time_str}': {e}")
            # Default to today at 7:00 PM ET
            if ZoneInfo:
                default_dt = datetime.now(ZoneInfo('America/New_York')).replace(hour=19, minute=0, second=0, microsecond=0)
                return int(default_dt.timestamp() * 1000)
            else:
                default_dt = datetime.now(timezone(timedelta(hours=-5))).replace(hour=19, minute=0, second=0, microsecond=0)
                return int(default_dt.timestamp() * 1000)
    
    def _get_games_fallback(self, days_ahead: int) -> List[Dict]:
        """Fallback method - returns sample upcoming games when API doesn't return data"""
        # This happens when:
        # 1. NBA season hasn't started yet
        # 2. API is temporarily unavailable
        # 3. No games scheduled for the date range
        # 4. We're in off-season
        
        today = datetime.now()
        sample_games = []
        
        # Generate sample upcoming games for the next few days
        for i in range(min(3, days_ahead)):  # Max 3 sample games
            game_date = today + timedelta(days=i+1)
            # Set game time to 7:00 PM ET (typical NBA game time)
            game_date = game_date.replace(hour=19, minute=0, second=0, microsecond=0)
            # Make timezone-aware (ET)
            if ZoneInfo:
                game_date = game_date.replace(tzinfo=ZoneInfo('America/New_York'))
            else:
                game_date = game_date.replace(tzinfo=timezone(timedelta(hours=-5)))
            
            # Sample matchups
            matchups = [
                {'team0': 'LAL', 'team1': 'GSW', 'team0Elo': 1600, 'team1Elo': 1650},
                {'team0': 'BOS', 'team1': 'MIA', 'team0Elo': 1700, 'team1Elo': 1580},
                {'team0': 'DEN', 'team1': 'PHX', 'team0Elo': 1680, 'team1Elo': 1570},
            ]
            
            if i < len(matchups):
                matchup = matchups[i]
                game = {
                    'gameId': f'sample_{int(game_date.timestamp())}',
                    'team0': matchup['team0'],
                    'team1': matchup['team1'],
                    'gameDate': int(game_date.timestamp() * 1000),
                    'team0Stats': {
                        'PTS': 115, 'REB': 45, 'AST': 28, 
                        'FG_PCT': 0.48, 'FG3_PCT': 0.36, 'FT_PCT': 0.80,
                        'OREB': 11, 'TOV': 12
                    },
                    'team1Stats': {
                        'PTS': 112, 'REB': 42, 'AST': 25,
                        'FG_PCT': 0.46, 'FG3_PCT': 0.35, 'FT_PCT': 0.78,
                        'OREB': 10, 'TOV': 14
                    },
                    'team0Elo': matchup['team0Elo'],
                    'team1Elo': matchup['team1Elo'],
                    'team0IsHome': False,
                    'team1IsHome': True,
                    'status': 'Scheduled',
                }
                sample_games.append(game)
        
        print(f"Using {len(sample_games)} sample games (API returned no data)")
        return sample_games

