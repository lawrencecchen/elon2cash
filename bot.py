import discord
import alpaca_trade_api as trade_api
from dotenv import load_dotenv
import os

load_dotenv()

ALPACA_API_KEY = os.environ.get('ALPACA_API_KEY')
ALPACA_API_SECRET = os.environ.get('ALPACA_API_SECRET')
APCA_API_BASE_URL = os.environ.get('APCA_API_BASE_URL')
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')


api = trade_api.REST(ALPACA_API_KEY, ALPACA_API_SECRET, APCA_API_BASE_URL, 'v2')

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$clock'):
        clock = api.get_clock()
        await message.channel.send('The market is {}'.format('open.' if clock.is_open else 'closed.'))

client.run(DISCORD_TOKEN)
