import discord
from discord import app_commands
from discord.ext import commands
from services.sports_api import get_nba_leaders

STAT_CHOICES = [
    app_commands.Choice(name="Points", value="pts"),
    app_commands.Choice(name="Rebounds", value="reb"),
    app_commands.Choice(name="Assists", value="ast"),
    app_commands.Choice(name="Steals", value="stl"),
    app_commands.Choice(name="Blocks", value="blk"),
]

STAT_LABELS = {
    "pts": "Points",
    "reb": "Rebounds",
    "ast": "Assists",
    "stl": "Steals",
    "blk": "Blocks",
}


class Leaders(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="leaders", description="NBA season statistical leaders.")
    @app_commands.describe(stat="Stat category to rank by")
    @app_commands.choices(stat=STAT_CHOICES)
    async def leaders(self, interaction: discord.Interaction, stat: str = "pts"):
        await interaction.response.defer()
        entries = await get_nba_leaders(stat)
        if not entries:
            await interaction.followup.send("Could not fetch league leaders right now.")
            return

        label = STAT_LABELS.get(stat, stat.upper())
        embed = discord.Embed(title=f"NBA Leaders — {label}", color=discord.Color.gold())

        lines = []
        for i, e in enumerate(entries, 1):
            player_id = e.get("player_id")
            value = round(e.get(stat, 0), 1)
            lines.append(f"`{i:>2}.` {value} — Player #{player_id}")

        embed.description = "\n".join(lines)
        embed.set_footer(text="2025-26 Season")
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Leaders(bot))
