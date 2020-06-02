from discord.ext import commands
import aiohttp
import discord

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_me(self, m):
        return m.author == self.bot.user

    @commands.command(no_pm=True)
    async def say(self, ctx):
        """Say command to test"""
        await ctx.send(ctx.message.clean_content.replace(ctx.invoked_with, '')[len(ctx.prefix) + 1:])