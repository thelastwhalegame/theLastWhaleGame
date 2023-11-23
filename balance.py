import discord
from discord.ext import commands
import requests
from web3 import Web3
from configProd import DISCORD_BOT_TOKEN, API_URL, API_KEY, CONTRACT_ADDRESS, RPC_URL

intents = discord.Intents.default()
intents.message_content = True
intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

def interact_with_contract(api_url, api_key, contract_address):
    params = {"module": "contract", "action": "getabi", "address": contract_address, "apikey": api_key}
    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["status"] == "1":
            contract_abi = data["result"]
            web3 = Web3(Web3.HTTPProvider(RPC_URL))
            balance = web3.eth.get_balance(contract_address)
            balance_bnb = web3.from_wei(balance, 'ether')
            return f"Balance: {balance_bnb} BNB"
        else:
            return f"Error: {data['message']}"
    else:
        return f"Error: HTTP request failed with status code {response.status_code}"

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command(name='balance')
async def balance(ctx):
    try:
        result = interact_with_contract(API_URL, API_KEY, CONTRACT_ADDRESS)
        await ctx.send(result)
    except Exception as e:
        print(f"An error occurred: {e}")
        await ctx.send(f"An error occurred: {e}")

bot.run(DISCORD_BOT_TOKEN)
