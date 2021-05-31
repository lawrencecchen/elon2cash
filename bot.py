#Elon2Cash Trading Discord Bot lmao hi
from logging import error
import alpaca_trade_api as trade_api
from dotenv import load_dotenv
import os
from discord.ext import commands
from db import init_db, buy, sell, get_portfolio,get_current_holdings


#initialize database
load_dotenv()
init_db()

ALPACA_API_KEY = os.environ.get('ALPACA_API_KEY')
ALPACA_API_SECRET = os.environ.get('ALPACA_API_SECRET')
APCA_API_BASE_URL = os.environ.get('APCA_API_BASE_URL')
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')

api = trade_api.REST(ALPACA_API_KEY, ALPACA_API_SECRET, APCA_API_BASE_URL, 'v2')

bot = commands.Bot(command_prefix='!')

@bot.command()
async def clock(ctx):
    clock = api.get_clock()
    await ctx.send('The market is {}'.format('open.' if clock.is_open else 'closed.'))

bot.run(DISCORD_TOKEN)
