import discord
from discord import app_commands
from discord.ext import commands
from config import LEAGUES
from services.sports_api import get_all_games_today

LEAGUE_CHOICES = [
    app_commands.Choice(name=k.upper(), value=k) for k in LEAGUES
]

LEAGUE_EMOJI = {
    "nba": "🏀", "nfl": "🏈", "epl": "⚽", "laliga": "⚽",
    "seriea": "⚽", "bundesliga": "⚽", "ligue1": "⚽", "ucl": "🏆",
}

STATUS_LIVE = {"1H", "2H", "HT", "ET", "P", "LIVE", "Q1", "Q2", "Q3", "Q4", "OT"}
STATUS_FINAL = {"FT", "AET", "PEN", "FINAL", "F"}


class Gameday(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="gameday", description="See all games today for a league.")
    @app_commands.choices(league=LEAGUE_CHOICES)
    async def gameday(self, interaction: discord.Interaction, league: str = "nba"):
        await interaction.response.defer()
        games = await get_all_games_today(league)
        emoji = LEAGUE_EMOJI.get(league, "🏟️")

        if not games:
            await interaction.followup.send(f"No games scheduled today for **{league.upper()}**.")
            return

        embed = discord.Embed(
            title=f"{emoji} {league.upper()} — Today's Games",
            color=discord.Color.blurple(),
        )

        for game in games:
            status = game["status"]
            home_score = game.get("home_score")
            away_score = game.get("away_score")

            if status in STATUS_LIVE:
                clock = f" {game['clock']}'" if game.get("clock") else ""
                score = f"{away_score} - {home_score}"
                value = f"`🟢 LIVE {status}{clock}` — {score}"
            elif status in STATUS_FINAL:
                value = f"`🔴 FINAL` — {away_score} - {home_score}"
            else:
                value = f"`🕐 Scheduled`"

            embed.add_field(
                name=f"{game['away']} @ {game['home']}",
                value=value,
                inline=False,
            )

        from datetime import date
        embed.set_footer(text=date.today().strftime("%A, %B %d %Y"))
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Gameday(bot))
