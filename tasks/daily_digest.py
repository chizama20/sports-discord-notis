import datetime
import discord
from discord.ext import tasks
from config import LEAGUES
from services.sports_api import get_all_games_today
from db.database import get_all_guild_configs

LEAGUE_EMOJI = {
    "nba": "🏀", "nfl": "🏈", "epl": "⚽", "laliga": "⚽",
    "seriea": "⚽", "bundesliga": "⚽", "ligue1": "⚽", "ucl": "🏆",
}

# Posts at 9:00 AM ET (14:00 UTC)
DIGEST_TIME = datetime.time(hour=14, minute=0, tzinfo=datetime.timezone.utc)


def start_daily_digest(bot: discord.Client):
    @tasks.loop(time=DIGEST_TIME)
    async def digest():
        configs = await get_all_guild_configs()
        if not configs:
            return

        all_games: dict[str, list] = {}
        for league in LEAGUES:
            try:
                games = await get_all_games_today(league)
                if games:
                    all_games[league] = games
            except Exception as e:
                print(f"[daily_digest] Error fetching {league}: {e}")

        if not all_games:
            return

        embed = _build_digest_embed(all_games)

        for config in configs:
            channel = bot.get_channel(int(config["updates_channel_id"]))
            if channel:
                try:
                    await channel.send(embed=embed)
                except discord.Forbidden:
                    pass

    @digest.before_loop
    async def before_digest():
        await bot.wait_until_ready()

    digest.start()


def _build_digest_embed(all_games: dict[str, list]) -> discord.Embed:
    today = datetime.date.today().strftime("%A, %B %d %Y")
    embed = discord.Embed(
        title=f"🗓️ Today's Sports Schedule — {today}",
        color=discord.Color.blurple(),
    )

    for league, games in all_games.items():
        emoji = LEAGUE_EMOJI.get(league, "🏟️")
        lines = []
        for g in games:
            status = g.get("status", "")
            if status in ("NS", "Scheduled", ""):
                lines.append(f"• {g['away']} @ {g['home']}")
            else:
                lines.append(f"• {g['away']} @ {g['home']} `{status}`")

        if lines:
            embed.add_field(
                name=f"{emoji} {league.upper()}",
                value="\n".join(lines),
                inline=False,
            )

    embed.set_footer(text="Updates post automatically when games go live.")
    return embed
