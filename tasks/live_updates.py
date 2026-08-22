import asyncio
from datetime import datetime, timedelta, timezone
import discord
from discord.ext import tasks
from config import LEAGUES, POLL_INTERVAL, PREGAME_LEAD_MINUTES
from services.sports_api import get_all_games_today
from db.database import (
    get_guild_channel,
    get_followers_for_teams,
    upsert_tracked_game,
    get_tracked_game,
    delete_tracked_game,
)

HALFTIME_STATUSES = {"HT"}
IN_PROGRESS_STATUSES = {"1H", "2H", "ET", "P", "LIVE", "Q1", "Q2", "Q3", "Q4", "OT", "IN_PLAY"}
FINAL_STATUSES = {"FT", "AET", "PEN", "AOT", "FT_PEN", "POST", "FINAL", "F"}

STAGE_PREGAME = 1
STAGE_HALFTIME = 2
STAGE_FINAL = 3

LEAGUE_EMOJI = {
    "nba": "🏀",
    "nfl": "🏈",
    "epl": "⚽",
    "laliga": "⚽",
    "seriea": "⚽",
    "bundesliga": "⚽",
    "ligue1": "⚽",
    "ucl": "🏆",
}


def start_live_updates(bot: discord.Client):
    @tasks.loop(seconds=POLL_INTERVAL)
    async def poll():
        now = datetime.now(timezone.utc)
        for league in LEAGUES:
            try:
                games = await get_all_games_today(league)
            except Exception as e:
                print(f"[live_updates] Error fetching {league}: {e}")
                await asyncio.sleep(7)
                continue

            await asyncio.sleep(7)

            for game in games:
                status = game["status"]
                game_id = game["game_id"]

                if status in FINAL_STATUSES:
                    target_stage, should_notify = STAGE_FINAL, True
                elif status in HALFTIME_STATUSES:
                    target_stage, should_notify = STAGE_HALFTIME, True
                elif status in IN_PROGRESS_STATUSES:
                    # Already live with no pregame ping on record (e.g. bot was down) —
                    # backfill the stage silently, don't send a "starting soon" message late.
                    target_stage, should_notify = STAGE_PREGAME, False
                else:
                    start_time = game.get("start_time")
                    if start_time and now >= start_time - timedelta(minutes=PREGAME_LEAD_MINUTES):
                        target_stage, should_notify = STAGE_PREGAME, True
                    else:
                        target_stage, should_notify = 0, False

                if target_stage == 0:
                    continue

                stored = await get_tracked_game(game_id)
                current_stage = stored["stage"] if stored else 0
                if target_stage <= current_stage:
                    continue

                if should_notify:
                    await _notify(bot, game, league, target_stage)

                if target_stage == STAGE_FINAL:
                    await delete_tracked_game(game_id)
                else:
                    await upsert_tracked_game(game_id, league, target_stage)

    @poll.before_loop
    async def before_poll():
        await bot.wait_until_ready()

    poll.start()


async def _notify(bot: discord.Client, game: dict, league: str, stage: int):
    embed = _stage_embed(game, league, stage)
    for guild in bot.guilds:
        guild_id = str(guild.id)
        channel_id = await get_guild_channel(guild_id)
        if not channel_id:
            continue
        channel = bot.get_channel(int(channel_id))
        if not channel:
            continue
        followers = await get_followers_for_teams(guild_id, league, game["home"], game["away"])
        mentions = " ".join(f"<@{uid}>" for uid in followers) if followers else ""
        try:
            await channel.send(content=mentions or None, embed=embed)
        except discord.Forbidden:
            pass


def _stage_embed(game: dict, league: str, stage: int) -> discord.Embed:
    emoji = LEAGUE_EMOJI.get(league, "🏟️")

    if stage == STAGE_PREGAME:
        start_time = game.get("start_time")
        when = f"<t:{int(start_time.timestamp())}:t>" if start_time else "soon"
        embed = discord.Embed(
            title=f"{emoji} Starting Soon",
            description=f"**{game['away']}** @ **{game['home']}**\nTips off {when}",
            color=discord.Color.green(),
        )
    elif stage == STAGE_HALFTIME:
        embed = discord.Embed(
            title=f"{emoji} Halftime",
            description=_score_line(game),
            color=discord.Color.gold(),
        )
    else:
        embed = discord.Embed(
            title=f"{emoji} Final",
            description=_score_line(game),
            color=discord.Color.red(),
        )

    embed.set_footer(text=league.upper())
    return embed


def _score_line(game: dict) -> str:
    home_score = game["home_score"] if game["home_score"] is not None else "-"
    away_score = game["away_score"] if game["away_score"] is not None else "-"
    return f"**{game['away']}** {away_score} — {home_score} **{game['home']}**"
