import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
API_SPORTS_KEY = os.getenv("API_SPORTS_KEY")
BALLDONTLIE_KEY = os.getenv("BALLDONTLIE_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

POLL_INTERVAL = 60  # seconds between live update checks

LEAGUES = {
    "nba": 12,
    "nfl": 1,
    "epl": 39,
    "laliga": 140,
    "seriea": 135,
    "bundesliga": 78,
    "ligue1": 61,
    "ucl": 2,
}
