import discord
from discord import app_commands
from discord.ext import commands
from services.sports_api import get_player_stats


class Player(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="player", description="Look up NBA player season stats.")
    @app_commands.describe(name="Player name (e.g. LeBron James)")
    async def player(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer()
        result = await get_player_stats(name)
        if not result:
            await interaction.followup.send(f"No player found matching **{name}**.")
            return

        p = result["player"]
        avgs = result["averages"]
        full_name = f"{p.get('first_name', '')} {p.get('last_name', '')}".strip()
        team = p.get("team", {}).get("full_name", "No team") if p.get("team") else "No team"

        embed = discord.Embed(title=full_name, description=team, color=discord.Color.gold())

        if avgs:
            embed.add_field(name="PTS", value=round(avgs.get("pts", 0), 1), inline=True)
            embed.add_field(name="REB", value=round(avgs.get("reb", 0), 1), inline=True)
            embed.add_field(name="AST", value=round(avgs.get("ast", 0), 1), inline=True)
            embed.add_field(name="STL", value=round(avgs.get("stl", 0), 1), inline=True)
            embed.add_field(name="BLK", value=round(avgs.get("blk", 0), 1), inline=True)
            embed.add_field(name="FG%", value=f"{round((avgs.get('fg_pct') or 0) * 100, 1)}%", inline=True)
            embed.add_field(name="3P%", value=f"{round((avgs.get('fg3_pct') or 0) * 100, 1)}%", inline=True)
            embed.add_field(name="FT%", value=f"{round((avgs.get('ft_pct') or 0) * 100, 1)}%", inline=True)
            embed.add_field(name="GP", value=avgs.get("games_played", "—"), inline=True)
            embed.set_footer(text="2025-26 Season Averages")
        else:
            embed.description = f"{team}\n*No stats available for this season.*"

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Player(bot))
