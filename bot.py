import discord, datetime, aiohttp, sys, traceback, json
from discord.ext import commands
from pymongo import MongoClient as mc

intents = discord.Intents.all()

class Paimon(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix='pai!',
            owner_ids={745315772943040563, 760518922407247872},
            intents=intents
        )

        with open('configvars.json', 'r')as f:
            self.config = json.load(f)
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.db = mc(self.config['mongourl'])['gachi_impact']

        exts = [
            'exts.genshin',
            'jishaku',
            'exts.errorhandler'
        ]

        for ext in exts:
            try:
                self.load_extension(ext)
                print(f'Loaded {ext}')
            except Exception as error:
                print(f'{ext} could not be loaded: {error}')

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()

        print('I AM UP ADVENTURE LETS FUCK SOME PEOPLE UP')

    async def on_command_error(self, ctx, error):
        error = getattr(error, 'original', error)
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send("Can't use this command in dms.")
        elif isinstance(error, commands.DisabledCommand):
            await ctx.author.send("This command is disabled.")
        elif isinstance(error, commands.CommandInvokeError):
            original = error.original
            if not isinstance(original, discord.HTTPException):
                print(f'In {ctx.command.qualified_name}:', file=sys.stderr)
                traceback.print_tb(original.__traceback__)
                print(f'{original.__class__.__name__}: {original}', file=sys.stderr)
        else:
            raise error

    async def close(self):
        await super().close()
        await self.session.close()

    def run(self):
        super().run(self.config['token'])