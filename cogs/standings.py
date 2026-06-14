import discord
from discord import app_commands
from discord.ext import commands
from services.sports_api import get_standings

SOCCER_LEAGUES = ["epl", "laliga", "seriea", "bundesliga", "ligue1", "ucl"]

LEAGUE_CHOICES = [
    app_commands.Choice(name=k.upper(), value=k) for k in SOCCER_LEAGUES
]


class Standings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="standings", description="Get current league standings (soccer only).")
    @app_commands.choices(league=LEAGUE_CHOICES)
    async def standings(self, interaction: discord.Interaction, league: str):
        await interaction.response.defer()
        table = await get_standings(league)
        if not table:
            await interaction.followup.send(f"Could not fetch standings for **{league.upper()}**.")
            return

        embed = discord.Embed(title=f"{league.upper()} Standings", color=discord.Color.gold())
        lines = []
        for entry in table[:20]:
            gd = entry["gd"]
            gd_str = f"+{gd}" if gd > 0 else str(gd)
            lines.append(
                f"`{entry['rank']:>2}.` {entry['team']:<25} "
                f"P:{entry['played']}  W:{entry['won']}  D:{entry['drawn']}  L:{entry['lost']}  "
                f"GD:{gd_str}  **{entry['points']}pts**"
            )
        embed.description = "\n".join(lines)
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Standings(bot))
