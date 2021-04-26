import discord
from discord.ext import commands
from .utils.checks_err import *
import genshinstats as gs

class Genshin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.userdata = self.bot.db['userdata']

    async def get_gid_from_cid(self, cid:int):
        gid = await self.bot.loop.run_in_executor(None, gs.get_uid_from_community, cid)
        if gid is None:
            raise AccountNotPublic()
        return gid

    async def input_data_to_db(self, uid:int, cid:int, gid:int, authcookie:str):
        self.userdata.insert_one(
            {
                'uid':uid,
                'cid':cid,
                'gid':gid,
                'authcookie':authcookie
            }
        )

    async def set_current_logged_in_user(self, uid):
        user = self.userdata.find_one({'uid':uid})
        await self.bot.loop.run_in_executor(None, gs.set_cookie, user['cid'], user['authcookie'])

    async def parse_reward(self, uid):
        user = self.userdata.find_one({'uid':uid})
        await self.bot.loop.run_in_executor(None, gs.set_cookie, user['cid'], user['authcookie'])
        loots = gs.get_daily_rewards()[0]
        streak = gs.get_daily_reward_info()['total_sign_day']
        return loots['name'], loots['cnt'], loots['img'], streak

    @not_logged_in()
    @commands.command(name='setup', aliases=['register'])
    async def _setup(self, ctx, ltuid:int, ltoken:str):
        cid = ltuid
        authcookie = ltoken
        """This is a required step to authenticate your hoyolab account to this bot."""
        await ctx.message.delete()
        gs.set_cookie(cid, authcookie)
        gid = await self.get_gid_from_cid(cid)
        await self.input_data_to_db(ctx.author.id, cid, gid, authcookie)
        await ctx.send('Success!')

    @is_logged_in()
    @not_checked_in()
    @commands.group(invoke_without_command=True, name='checkin', aliases=['signin'])
    async def _checkin(self, ctx):
        """Automatically sign-in to the daily check-in rewards from the hoyolab website."""
        await self.set_current_logged_in_user(ctx.author.id)
        await self.bot.loop.run_in_executor(None, gs.sign_in)
        name, count, image, streak = await self.parse_reward(ctx.author.id)
        e = discord.Embed(
            color = discord.Color(0x2f3136),
        ).set_author(
            name=f'You have signed in x{streak} times in this month!',
            icon_url = self.bot.user.avatar_url_as(static_format='png')
        ).add_field(
            name=f'You got {name} x{count}',
            value='\u200b'
        ).set_thumbnail(
            url=image
        )

        await ctx.send(embed=e)

    @commands.command(name='howto')
    async def _howto(self, ctx):
        e = discord.Embed(
            color=discord.Color(0x2f3136),
            title='How to use PAIMON Bot/How to integrate your Genshin Account to PAIMON Bot'
        ).add_field(
            name='**Step #1:**',
            value='Go to the [hoyolab webiste](https://hoyolab.com/genshin).',
            inline=False
        ).add_field(
            name='**Step #2:**',
            value='Log onto your account.',
            inline=False
        ).add_field(
            name='**Step #3:**',
            value='Once logged in, press F12 or right click on an empty area within the website and press inspect.',
            inline=False
        ).add_field(
            name='**Step #4:**',
            value='After opening the inspect mode, press the Application tab. For Firefox users, press the Storage tab instead.',
            inline=False
        ).add_field(
            name='**Step #5:**',
            value='When on the Application/Storage tab, click Cookies. Then underneath the "Cookies" option, you\'ll see the website\'s cookies.',
            inline=False
        ).add_field(
            name='**Step #6:**',
            value='Get the values of both `ltuid` and `ltoken` and kindly run the `setup` or `register` command, providing the proper input for the arguments.',
            inline=False
        ).set_image(
            url='https://cdn.discordapp.com/attachments/694172476934193264/836003502639022100/complete.gif'
        ).set_thumbnail(
            url='https://cdn.discordapp.com/attachments/694172476934193264/836005833048850462/d53edec176d2027dfe6e8dc35599d972_4325071795431613034.png'
        ).set_footer(
            text='If you still have any concerns, feel free to dm me anytime. -eve-alt#8626'
        )

        await ctx.send(embed=e)
        
def setup(bot):
    bot.add_cog(Genshin(bot))