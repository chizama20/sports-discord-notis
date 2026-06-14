# Sports Discord Bot — Project Plan

## Overview
A Discord bot (Python, discord.py) that provides on-demand sports info via slash commands and automatically posts live updates for in-progress games. Covers NBA, NFL, and major soccer leagues (EPL, La Liga, Serie A, Bundesliga, Ligue 1, Champions League).

## Tech Stack
- **Language:** Python 3.11+
- **Discord library:** discord.py (with app_commands / slash commands, cogs)
- **Database:** SQLite (via `sqlite3` or `aiosqlite`)
- **Scheduling:** discord.py `tasks.loop`
- **Sports data:** external sports data API (TBD — needs an API key; e.g. SportRadar-style provider)
- **Config/secrets:** `.env` file with `python-dotenv`

## Folder Structure
```
nba-nfl-soccer-bot/
├── bot.py                  # entry point, loads cogs, starts bot
├── cogs/
│   ├── scores.py           # /score command
│   ├── standings.py        # /standings command
│   └── follow.py           # /follow, /unfollow, /following commands
├── services/
│   └── sports_api.py       # wrapper for fetching scores/stats/standings
├── tasks/
│   └── live_updates.py     # background polling loop for live games
├── db/
│   ├── database.py         # SQLite setup + connection helper
│   └── schema.sql           # table definitions
├── config.py                # loads env vars, constants (channel IDs, poll interval)
├── requirements.txt
├── .env.example              # template for secrets (no real values)
├── .gitignore
└── README.md
```

## Database Schema (SQLite)
**follows**
| column     | type    | notes                                |
|------------|---------|--------------------------------------|
| id         | INTEGER | primary key, autoincrement           |
| user_id    | TEXT    | Discord user ID                      |
| guild_id   | TEXT    | Discord server ID                    |
| league     | TEXT    | nba / nfl / epl / etc.                |
| team       | TEXT    | team name or abbreviation            |

**tracked_games**
| column        | type    | notes                                  |
|---------------|---------|----------------------------------------|
| game_id       | TEXT    | primary key (from sports API)          |
| league        | TEXT    |                                          |
| last_status   | TEXT    | e.g. "scheduled", "live", "final"      |
| last_score    | TEXT    | JSON or "home-away" string             |
| channel_id    | TEXT    | where updates get posted               |

**guild_config**
| column        | type    | notes                                  |
|---------------|---------|------------------------------------------|
| guild_id      | TEXT    | primary key                              |
| updates_channel_id | TEXT | default channel for live updates       |

## Slash Commands (Phase 1)
- `/score <league> <team>` — current score / status of a team's game
- `/standings <league>` — current standings table
- `/setchannel <channel>` — admin command to set the live-updates channel for the server
- `/follow <league> <team>` — subscribe a user to a team's updates (DM or mention in updates channel)
- `/unfollow <league> <team>`
- `/following` — list a user's followed teams

## Background Task: Live Updates (Phase 2)
- Runs every 60 seconds (configurable)
- For each league with games today, checks live/in-progress games via `sports_api`
- Compares current score/status to `tracked_games` table
- If changed:
  - Posts an embed to the guild's `updates_channel_id`
  - Optionally @mentions/DMs users who follow either team
  - Updates `tracked_games` row
- Handles game-final detection and stops tracking finished games after posting the final result

## Implementation Phases

### Phase 1 — Foundation
1. Scaffold project structure, `.env.example`, `requirements.txt`, `.gitignore`
2. Set up `bot.py` with basic bot login, cog loading, sync slash commands
3. Set up SQLite schema + `database.py` helper functions
4. Build `sports_api.py` wrapper — functions for `get_scores(league)`, `get_standings(league)`, `get_team_game(league, team)`

### Phase 2 — Core Commands
5. Implement `/score` command (cogs/scores.py)
6. Implement `/standings` command (cogs/standings.py)
7. Implement `/setchannel` admin command

### Phase 3 — Follow System
8. Implement `/follow`, `/unfollow`, `/following` commands (cogs/follow.py)
9. Wire follow data into DB

### Phase 4 — Live Updates Loop
10. Implement `tasks/live_updates.py` polling loop
11. Score-change detection + embed formatting
12. Game-final handling + cleanup of tracked_games

### Phase 5 — Polish
13. Error handling (API failures, rate limits, invalid team names)
14. Logging
15. README with setup/run instructions
16. (Optional) Dockerfile for deployment

## Notes for Claude Code
- Use `discord.py` 2.x with `app_commands` (slash commands), not legacy prefix commands
- Use cogs for modularity — each command group in its own file, loaded via `bot.load_extension`
- Keep `sports_api.py` provider-agnostic where possible — isolate the actual HTTP calls so the data source can be swapped later
- Use `aiosqlite` for async-safe DB access since discord.py is async
- All secrets (bot token, API keys) go in `.env`, never committed
- Start with Phase 1 + 2 to get a working bot with one command, then iterate
