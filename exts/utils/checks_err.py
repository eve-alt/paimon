import discord
import genshinstats as gs
from discord.ext import commands


class NotLoggedIn(commands.CheckFailure):
    """Exception raised when user is not logged in/no data in the database."""
    pass

class AlreadyLoggedIn(commands.CheckFailure):
    """Exception raised when user is already logged in."""

class ExpiredAuthkey(commands.CheckFailure):
    """Exception raised when user's authkey has expired already."""
    pass

class AccountNotPublic(commands.CheckFailure):
    """Exception raised when user's data is not set to public."""
    pass

class AlreadyCheckedIn(commands.CheckFailure):
    """Exception raised when user has already checked-in."""
    pass

def not_checked_in():
    """Checks if the user has checked in."""
    async def predicate(ctx):
        userdata = ctx.bot.db['userdata']
        user = userdata.find_one(
            {
                'uid':ctx.author.id
            }
        )
        if user is None:
            raise NotLoggedIn(f'You haven\'t logged-in/integrated your hoyolab account with PAIMON. Please run the `{ctx.prefix}howto` for more information.')
        gs.set_cookie(user['cid'], user['authcookie'])
        checked_in = gs.get_daily_reward_info()
        if not checked_in['is_sign']:
            return True
        raise AlreadyCheckedIn('You have already checked in for today. Come back again tomorrow!')
    return commands.check(predicate)

def is_logged_in():
    """Checks if the user is logged in."""
    async def predicate(ctx):
        userdata = ctx.bot.db['userdata']
        existing = userdata.find_one(
            {
                'uid':ctx.author.id
            }
        )
        if existing:
            return True
        raise NotLoggedIn(f'You haven\'t logged-in/integrated your hoyolab account with PAIMON. Please run the `{ctx.prefix}howto` for more information.')
    return commands.check(predicate)

def not_logged_in():
    """Checks if the user is not logged in."""
    async def predicate(ctx):
        userdata = ctx.bot.db['userdata']
        existing = userdata.find_one(
            {
                'uid':ctx.author.id
            }
        )
        if not existing:
            return True
        raise AlreadyLoggedIn('You have already logged-in/integrated your hoyolab account with PAIMON.')
    return commands.check(predicate)