import discord
from discord import app_commands
from discord.ext import commands
from config import LEAGUES
from services.sports_api import get_team_game

LEAGUE_CHOICES = [
    app_commands.Choice(name=k.upper(), value=k) for k in LEAGUES
]


class Scores(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="score", description="Get the current score for a team's game today.")
    @app_commands.describe(league="The league to search", team="Full or partial team name")
    @app_commands.choices(league=LEAGUE_CHOICES)
    async def score(self, interaction: discord.Interaction, league: str, team: str):
        await interaction.response.defer()
        game = await get_team_game(league, team)
        if not game:
            await interaction.followup.send(f"No game found for **{team}** in **{league.upper()}** today.")
            return

        embed = _game_embed(game)
        await interaction.followup.send(embed=embed)


def _game_embed(game: dict) -> discord.Embed:
    status = game["status"]
    clock = game.get("clock")

    home_score = game["home_score"] if game["home_score"] is not None else "-"
    away_score = game["away_score"] if game["away_score"] is not None else "-"

    title = f"{game['home']} vs {game['away']}"
    description = f"**{home_score}** — **{away_score}**"

    if clock:
        description += f"\n`{status}` • {clock}'"
    else:
        description += f"\n`{status}`"

    color = discord.Color.green() if status in ("1H", "2H", "HT", "ET", "P", "LIVE", "Q1", "Q2", "Q3", "Q4", "OT") else discord.Color.blurple()
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text=game["league"].upper())
    return embed


async def setup(bot: commands.Bot):
    await bot.add_cog(Scores(bot))
