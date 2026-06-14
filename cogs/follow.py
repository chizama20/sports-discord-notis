import discord
from discord import app_commands
from discord.ext import commands
from config import LEAGUES
from db.database import add_follow, remove_follow, get_follows, set_guild_channel

LEAGUE_CHOICES = [
    app_commands.Choice(name=k.upper(), value=k) for k in LEAGUES
]


class Follow(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="follow", description="Follow a team to get live update mentions.")
    @app_commands.describe(league="The league", team="Full or partial team name")
    @app_commands.choices(league=LEAGUE_CHOICES)
    async def follow(self, interaction: discord.Interaction, league: str, team: str):
        added = await add_follow(
            str(interaction.user.id), str(interaction.guild_id), league, team.lower()
        )
        if added:
            await interaction.response.send_message(
                f"You're now following **{team}** in **{league.upper()}**.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"You're already following **{team}** in **{league.upper()}**.", ephemeral=True
            )

    @app_commands.command(name="unfollow", description="Unfollow a team.")
    @app_commands.choices(league=LEAGUE_CHOICES)
    async def unfollow(self, interaction: discord.Interaction, league: str, team: str):
        removed = await remove_follow(
            str(interaction.user.id), str(interaction.guild_id), league, team.lower()
        )
        if removed:
            await interaction.response.send_message(
                f"Unfollowed **{team}** in **{league.upper()}**.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"You weren't following **{team}** in **{league.upper()}**.", ephemeral=True
            )

    @app_commands.command(name="following", description="List all teams you're following.")
    async def following(self, interaction: discord.Interaction):
        follows = await get_follows(str(interaction.user.id), str(interaction.guild_id))
        if not follows:
            await interaction.response.send_message("You're not following any teams yet.", ephemeral=True)
            return
        lines = [f"• **{f['team']}** ({f['league'].upper()})" for f in follows]
        embed = discord.Embed(
            title="Your followed teams",
            description="\n".join(lines),
            color=discord.Color.blurple(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="setchannel", description="Set the channel for live score updates (admin only).")
    @app_commands.describe(channel="The channel to post live updates in")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setchannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await set_guild_channel(str(interaction.guild_id), str(channel.id))
        await interaction.response.send_message(
            f"Live updates will be posted in {channel.mention}.", ephemeral=True
        )

    @setchannel.error
    async def setchannel_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("You need **Manage Server** permission to use this.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Follow(bot))
