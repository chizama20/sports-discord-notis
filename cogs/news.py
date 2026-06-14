import discord
from discord import app_commands
from discord.ext import commands
from config import LEAGUES
from services.sports_api import get_news, LEAGUE_NEWS_QUERY

LEAGUE_CHOICES = [
    app_commands.Choice(name=k.upper(), value=k) for k in LEAGUES
]


class News(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="news", description="Get the latest sports news for a team or league.")
    @app_commands.describe(
        query="Team name (e.g. 'Celtics') or leave blank to use the league",
        league="Filter by league",
    )
    @app_commands.choices(league=LEAGUE_CHOICES)
    async def news(self, interaction: discord.Interaction, league: str, query: str = ""):
        await interaction.response.defer()

        search = query.strip() if query.strip() else LEAGUE_NEWS_QUERY.get(league, league)
        articles = await get_news(search)

        if not articles:
            await interaction.followup.send(f"No news found for **{search}**.")
            return

        embed = discord.Embed(
            title=f"Latest news: {search}",
            color=discord.Color.blurple(),
        )

        for article in articles:
            embed.add_field(
                name=f"{article['title']}",
                value=f"*{article['source']}* · {article['published']}\n[Read more]({article['url']})",
                inline=False,
            )

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(News(bot))
