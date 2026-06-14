# Session Progress — June 13 2026

## What Was Built

### Core Bot (Phase 1-4 complete)
- `bot.py` — entry point, loads all cogs, syncs slash commands, starts background tasks
- `config.py` — loads `.env` vars, defines league ID map
- `db/schema.sql` + `db/database.py` — SQLite with `follows`, `tracked_games`, `guild_config` tables

### APIs in Use
| Service | Purpose | Key env var |
|---|---|---|
| discord.py 2.x | Bot framework | `DISCORD_TOKEN` |
| balldontlie.io | NBA scores, schedule, player stats | `BALLDONTLIE_KEY` |
| API-Sports | Soccer scores + standings (free tier = 100 req/day) | `API_SPORTS_KEY` |
| NewsAPI | Sports news articles | `NEWS_API_KEY` |

> Note: API-Sports free tier only covers NBA seasons up to 2024 — balldontlie handles current NBA season instead.

### Commands Built
| Command | Cog file | Status |
|---|---|---|
| `/score <league> <team>` | `cogs/scores.py` | Working |
| `/standings <league>` | `cogs/standings.py` | Working (soccer off-season, try in Aug) |
| `/gameday <league>` | `cogs/gameday.py` | Built, sync issue |
| `/schedule <team>` | `cogs/schedule.py` | Built, sync issue |
| `/player <name>` | `cogs/player.py` | Built, sync issue |
| `/leaders <stat>` | `cogs/leaders.py` | Built, sync issue (shows player IDs not names — needs fix) |
| `/follow <league> <team>` | `cogs/follow.py` | Working |
| `/unfollow <league> <team>` | `cogs/follow.py` | Working |
| `/following` | `cogs/follow.py` | Working |
| `/setchannel <channel>` | `cogs/follow.py` | Working |
| `/news <league> <query>` | `cogs/news.py` | Built, sync issue |

### Background Tasks
- `tasks/live_updates.py` — polls every 60s, posts score changes + game start notifications
- `tasks/daily_digest.py` — posts schedule every morning at 9am ET (14:00 UTC)

## Known Issues to Fix Next Session

### 1. Slash command sync (priority)
New commands added after initial bot invite aren't showing up in Discord.
- Try typing `!sync` in the server (bot owner only) to force an instant guild sync
- Or re-invite the bot using a fresh OAuth URL with `bot` + `applications.commands` scopes
- Global sync (`tree.sync()`) can take up to 1 hour to propagate

### 2. `/leaders` shows player IDs not names
balldontlie's `/season_averages` endpoint doesn't return player names, only IDs.
Fix: fetch player names separately and join, or use `/stats` endpoint which includes player objects.

### 3. Rate limit on live updates
Free API-Sports tier = 10 req/min. Added 7s sleep between league polls to stay under the cap.
If still hitting limits, increase `POLL_INTERVAL` in `config.py` (currently 60s).

## Next Features to Consider
- `/compare <player1> <player2>` — side by side NBA stat comparison
- `/recap <team>` — post-game news recap via NewsAPI
- `/playoffs` — NBA playoff bracket/series standings
- `/odds` — betting lines via The Odds API (500 req/month free)
- Auto-restart on crash (wrap `python bot.py` in a loop or use a process manager)
