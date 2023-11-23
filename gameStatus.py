import json
import discord
from discord.ext import commands
import requests
from web3 import Web3
from datetime import datetime
from configProd import API_URL, API_KEY, CONTRACT_ADDRESS, WEB3_PROVIDER_URL, BOT_TOKEN

intents = discord.Intents.default()
intents.message_content = True
intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

def interact_with_contract(api_url, api_key, contract_address):
    params = {
        "module": "contract",
        "action": "getabi",
        "address": contract_address,
        "apikey": api_key,
    }

    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["status"] == "1":
            contract_abi = json.loads(data["result"])
            if contract_abi:
                method_name = "isGameEnded"
                matching_methods = [item for item in contract_abi if item['type'] == 'function' and item['name'] == method_name]
                web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))
                contract = web3.eth.contract(address=contract_address, abi=contract_abi)
                if matching_methods:
                    method = matching_methods[0]
                    result = contract.functions[method['name']]().call()

                    return result
                else:
                    print(f"Method '{method_name}' not found in contract ABI.")
            else:
                return "Error: Empty ABI"
        else:
            return f"Error: {data['message']}"
    else:
        return f"Error: HTTP request failed with status code {response.status_code}"

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command(name='gameStatus')
async def balance(ctx):
    api_url = API_URL
    api_key = API_KEY
    contract_address = CONTRACT_ADDRESS

    try:
        result = interact_with_contract(api_url, api_key, contract_address)
        if result:
            await ctx.send("Game over")
        else:
            await ctx.send("The game is active")
    except Exception as e:
        print(f"An error occurred: {e}")
        await ctx.send(f"An error occurred: {e}")

# Bot token
bot.run(BOT_TOKEN)