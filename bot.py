import os
import certifi
os.environ["SSL_CERT_FILE"] = certifi.where()

import asyncio
import logging
import discord
from discord.ext import commands
from config import DISCORD_TOKEN
from db.database import init_db
from tasks.live_updates import start_live_updates

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

COGS = [
    "cogs.scores",
    "cogs.standings",
    "cogs.follow",
]


class SportsBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await init_db()
        for cog in COGS:
            await self.load_extension(cog)
            logging.info(f"Loaded cog: {cog}")
        await self.tree.sync()
        logging.info("Slash commands synced.")

    async def on_ready(self):
        logging.info(f"Logged in as {self.user} (ID: {self.user.id})")
        start_live_updates(self)


async def main():
    bot = SportsBot()
    async with bot:
        await bot.start(DISCORD_TOKEN)


asyncio.run(main())
