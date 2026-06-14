import discord
from discord import app_commands
from discord.ext import commands
from services.sports_api import get_nba_schedule


class Schedule(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="schedule", description="Get the next 5 upcoming NBA games for a team.")
    @app_commands.describe(team="Full or partial team name (e.g. Celtics)")
    async def schedule(self, interaction: discord.Interaction, team: str):
        await interaction.response.defer()
        games = await get_nba_schedule(team)
        if not games:
            await interaction.followup.send(f"No upcoming games found for **{team}**.")
            return

        embed = discord.Embed(title=f"Upcoming games: {team}", color=discord.Color.blurple())
        for g in games:
            tip = g["time"] or g["status"]
            embed.add_field(
                name=f"{g['date']}",
                value=f"{g['away']} @ {g['home']}\n`{tip}`",
                inline=False,
            )
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Schedule(bot))
