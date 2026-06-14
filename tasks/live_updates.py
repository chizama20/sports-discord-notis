import asyncio
import discord
from discord.ext import tasks
from config import LEAGUES, POLL_INTERVAL
from services.sports_api import get_scores
from db.database import (
    get_guild_channel,
    get_followers_for_teams,
    upsert_tracked_game,
    get_tracked_game,
    delete_tracked_game,
)

LIVE_STATUSES = {"1H", "2H", "HT", "ET", "P", "LIVE", "Q1", "Q2", "Q3", "Q4", "OT", "IN_PLAY"}
FINAL_STATUSES = {"FT", "AET", "PEN", "AOT", "FT_PEN", "POST", "FINAL", "F", "AOT"}


def start_live_updates(bot: discord.Client):
    @tasks.loop(seconds=POLL_INTERVAL)
    async def poll():
        for league in LEAGUES:
            try:
                games = await get_scores(league)
            except Exception as e:
                print(f"[live_updates] Error fetching {league}: {e}")
                await asyncio.sleep(7)
                continue

            await asyncio.sleep(7)  # stay under 10 req/min free tier limit

            for game in games:
                status = game["status"]
                score = f"{game['home_score']}-{game['away_score']}"
                game_id = game["game_id"]

                is_live = status in LIVE_STATUSES
                is_final = status in FINAL_STATUSES

                if not is_live and not is_final:
                    continue

                # Find a guild that has this league configured
                # For now we broadcast to all guilds that have a channel set
                for guild in bot.guilds:
                    guild_id = str(guild.id)
                    channel_id = await get_guild_channel(guild_id)
                    if not channel_id:
                        continue

                    channel = bot.get_channel(int(channel_id))
                    if not channel:
                        continue

                    stored = await get_tracked_game(game_id)
                    score_changed = stored is None or stored["last_score"] != score or stored["last_status"] != status

                    if not score_changed:
                        continue

                    await upsert_tracked_game(game_id, league, status, score, channel_id)

                    followers = await get_followers_for_teams(guild_id, league, game["home"], game["away"])
                    mentions = " ".join(f"<@{uid}>" for uid in followers) if followers else ""

                    embed = _update_embed(game, is_final)
                    content = mentions if mentions else None
                    await channel.send(content=content, embed=embed)

                    if is_final:
                        await delete_tracked_game(game_id)

    @poll.before_loop
    async def before_poll():
        await bot.wait_until_ready()

    poll.start()


def _update_embed(game: dict, is_final: bool) -> discord.Embed:
    home_score = game["home_score"] if game["home_score"] is not None else "-"
    away_score = game["away_score"] if game["away_score"] is not None else "-"
    clock = game.get("clock")
    status = game["status"]

    title = f"{game['home']} vs {game['away']}"
    score_line = f"**{home_score}** — **{away_score}**"

    if is_final:
        description = f"{score_line}\n`FINAL`"
        color = discord.Color.red()
    else:
        clock_str = f" • {clock}'" if clock else ""
        description = f"{score_line}\n`{status}`{clock_str}"
        color = discord.Color.green()

    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text=game["league"].upper())
    return embed
