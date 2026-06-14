import aiohttp
from config import API_SPORTS_KEY, BALLDONTLIE_KEY, LEAGUES

BASE_URL = "https://v3.football.api-sports.io"
BDL_URL = "https://api.balldontlie.io/v1"
NFL_URL = "https://v1.american-football.api-sports.io"

SOCCER_LEAGUES = {"epl", "laliga", "seriea", "bundesliga", "ligue1", "ucl"}


def _soccer_headers():
    return {"x-apisports-key": API_SPORTS_KEY}


def _nba_headers():
    return {"Authorization": f"Bearer {BALLDONTLIE_KEY}"}


def _nfl_headers():
    return {"x-apisports-key": API_SPORTS_KEY}


async def _get(session: aiohttp.ClientSession, url: str, params: dict, headers: dict) -> dict:
    async with session.get(url, params=params, headers=headers) as resp:
        data = await resp.json()
        print(f"[API] {url} params={params} status={resp.status} results={data.get('results')} errors={data.get('errors')}")
        resp.raise_for_status()
        return data


async def get_scores(league: str) -> list[dict]:
    """Return today's games for a league. Each item is a normalized game dict."""
    async with aiohttp.ClientSession() as session:
        if league in SOCCER_LEAGUES:
            return await _get_soccer_scores(session, league)
        elif league == "nba":
            return await _get_nba_scores(session)
        elif league == "nfl":
            return await _get_nfl_scores(session)
    return []


async def _get_soccer_scores(session: aiohttp.ClientSession, league: str) -> list[dict]:
    league_id = LEAGUES[league]
    data = await _get(
        session,
        f"{BASE_URL}/fixtures",
        {"league": league_id, "live": "all"},
        _soccer_headers(),
    )
    return [_normalize_soccer(f, league) for f in data.get("response", [])]


async def _get_nba_scores(session: aiohttp.ClientSession) -> list[dict]:
    from datetime import date
    today = date.today().isoformat()
    data = await _get(
        session,
        f"{BDL_URL}/games",
        {"dates[]": today, "per_page": 100},
        _nba_headers(),
    )
    return [_normalize_nba(g) for g in data.get("data", [])]


async def _get_nfl_scores(session: aiohttp.ClientSession) -> list[dict]:
    from datetime import date
    today = date.today().isoformat()
    data = await _get(
        session,
        f"{NFL_URL}/games",
        {"date": today},
        _nfl_headers(),
    )
    return [_normalize_nfl(g) for g in data.get("response", [])]


async def get_team_game(league: str, team: str) -> dict | None:
    """Return the most recent or live game for a specific team name (case-insensitive partial match)."""
    games = await get_scores(league)
    team_lower = team.lower()
    for game in games:
        if team_lower in game["home"].lower() or team_lower in game["away"].lower():
            return game
    return None


async def get_standings(league: str) -> list[dict]:
    """Return current standings for soccer leagues. NBA/NFL standings TBD."""
    if league not in SOCCER_LEAGUES:
        return []
    async with aiohttp.ClientSession() as session:
        from datetime import date
        season = date.today().year
        data = await _get(
            session,
            f"{BASE_URL}/standings",
            {"league": LEAGUES[league], "season": season},
            _soccer_headers(),
        )
        try:
            table = data["response"][0]["league"]["standings"][0]
            return [_normalize_standing(s) for s in table]
        except (IndexError, KeyError):
            return []


def _normalize_soccer(fixture: dict, league: str) -> dict:
    teams = fixture.get("teams", {})
    goals = fixture.get("goals", {})
    status = fixture.get("fixture", {}).get("status", {})
    return {
        "game_id": str(fixture["fixture"]["id"]),
        "league": league,
        "home": teams.get("home", {}).get("name", "?"),
        "away": teams.get("away", {}).get("name", "?"),
        "home_score": goals.get("home"),
        "away_score": goals.get("away"),
        "status": status.get("short", "NS"),
        "clock": status.get("elapsed"),
    }


_BDL_STATUS_MAP = {
    "Final": "FT",
    "Halftime": "HT",
    "1st Qtr": "Q1",
    "2nd Qtr": "Q2",
    "3rd Qtr": "Q3",
    "4th Qtr": "Q4",
    "OT": "OT",
}


def _normalize_nba(game: dict) -> dict:
    raw_status = game.get("status", "")
    status = _BDL_STATUS_MAP.get(raw_status, "NS")
    clock = game.get("time") or None
    if clock and clock.strip() == "":
        clock = None
    return {
        "game_id": str(game.get("id")),
        "league": "nba",
        "home": game.get("home_team", {}).get("full_name", "?"),
        "away": game.get("visitor_team", {}).get("full_name", "?"),
        "home_score": game.get("home_team_score"),
        "away_score": game.get("visitor_team_score"),
        "status": status,
        "clock": clock,
    }


def _normalize_nfl(game: dict) -> dict:
    return {
        "game_id": str(game.get("id")),
        "league": "nfl",
        "home": game.get("teams", {}).get("home", {}).get("name", "?"),
        "away": game.get("teams", {}).get("away", {}).get("name", "?"),
        "home_score": game.get("scores", {}).get("home", {}).get("total"),
        "away_score": game.get("scores", {}).get("away", {}).get("total"),
        "status": game.get("game", {}).get("status", {}).get("short", ""),
        "clock": game.get("game", {}).get("status", {}).get("timer"),
    }


def _normalize_standing(entry: dict) -> dict:
    return {
        "rank": entry.get("rank"),
        "team": entry.get("team", {}).get("name", "?"),
        "played": entry.get("all", {}).get("played"),
        "won": entry.get("all", {}).get("win"),
        "drawn": entry.get("all", {}).get("draw"),
        "lost": entry.get("all", {}).get("lose"),
        "gd": entry.get("goalsDiff"),
        "points": entry.get("points"),
    }
