# client id: 545188c06166f3d1b1107127871ca61c
# secret: f012f21654a549ab286466fb28fb276e3c4c1021
# https://github.com/alpacahq/alpaca-trade-api-python/

import discord
import alpaca_trade_api as trade_api

API_KEY = "545188c06166f3d1b1107127871ca61c"
API_SECRET = "f012f21654a549ab286466fb28fb276e3c4c1021"
APCA_API_BASE_URL = "https://paper-api.alpaca.markets"

api = trade_api.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, 'v2')

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

client.run('ODQ4MDU4MDM5NjU5MjY2MDc4.YLHFmA.-PgPrPZlZgbhGukDR6hlse-0mFQ')
