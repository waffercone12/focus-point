import discord

from discord.ext import commands

from config import DISCORD_TOKEN
from commands.optimize import register


class AlbionBot(discord.Client):

    def __init__(self):

        intents = discord.Intents.default()

        super().__init__(intents=intents)

        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self):

        register(self.tree)

        await self.tree.sync()


bot = AlbionBot()

bot.run(DISCORD_TOKEN)