import discord
import genshinstats as gs
from discord.ext import commands
from .utils.checks_err import *

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        error = getattr(error, 'original', error)

        e = discord.Embed(
            title='Error!',
            description=f'{error}',
            color=discord.Color(0x2f3136)
        ).set_thumbnail(url='https://media.discordapp.net/attachments/694172476934193264/835482065503256616/angrypaimong.png')

        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))