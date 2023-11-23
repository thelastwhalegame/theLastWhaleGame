import discord
from discord.ext import tasks, commands
import requests
import sqlite3
from web3 import Web3
from configProd import DISCORD_BOT_TOKEN, CONTRACT_ADDRESS, BSCSCAN_API_KEY

intents = discord.Intents.default()
intents.message_content = True
intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Connect to the SQLite database
conn = sqlite3.connect('transactions.db')
cursor = conn.cursor()

# Create the 'transactions' table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    hash TEXT PRIMARY KEY
)
''')
conn.commit()

# Global variable for context
global_ctx = None

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    check_transactions.start()

@bot.event
async def on_message(message):
    print(f"Received message: {message.content}")
    global global_ctx
    global_ctx = message.channel  # Save the message context
    await bot.process_commands(message)

@tasks.loop(seconds=10)
async def check_transactions():
    bscscan_url = f"https://api-testnet.bscscan.com/api?module=account&action=txlist&address={CONTRACT_ADDRESS}&startblock=0&endblock=999999999&sort=asc&apikey={BSCSCAN_API_KEY}"

    try:
        response = requests.get(bscscan_url)
        response.raise_for_status()
        transactions = response.json().get('result', [])

        for tx in transactions:
            # Check if the transaction has been processed
            if not is_transaction_processed(tx['hash']):
                channel = global_ctx  # Use the saved context
                if channel:
                    balance = await get_bsc_balance()  # No need to pass the context
                    await channel.send(
                        f'New transaction on the smart contract! \nTransaction: https://testnet.bscscan.com/tx/{tx["hash"]}. \nBalance {balance} BNB')
                else:
                    print(f"Channel not found.")

                # Add the transaction hash to the database
                add_transaction(tx['hash'])
    except requests.exceptions.RequestException as e:
        print(f"Error querying BscScan API: {e}")

async def get_bsc_balance():
    try:
        web3 = Web3(Web3.HTTPProvider("https://data-seed-prebsc-1-s1.binance.org:8545/"))

        if web3.is_connected():
            checksum_address = Web3.to_checksum_address(CONTRACT_ADDRESS)
            balance_wei = web3.eth.get_balance(checksum_address)
            balance_bnb = Web3.from_wei(balance_wei, 'ether')

            return f"Balance of the contract {CONTRACT_ADDRESS}: {balance_bnb} BNB"
        else:
            return "Failed to connect to Binance Smart Chain."
    except Exception as e:
        print(f"Error getting balance: {e}")
        return "An error occurred while getting the balance."

def is_transaction_processed(tx_hash):
    # Check if the transaction has been processed
    cursor.execute('SELECT * FROM transactions WHERE hash = ?', (tx_hash,))
    return cursor.fetchone() is not None

def add_transaction(tx_hash):
    # Add the transaction hash to the database
    cursor.execute('INSERT INTO transactions VALUES (?)', (tx_hash,))
    conn.commit()

@bot.command(name='start_tracking')
async def start_tracking(ctx):
    try:
        check_transactions.start()
        await ctx.send('Transaction tracking started!')
    except Exception as e:
        await ctx.send(f'An error occurred: {str(e)}')

@bot.command(name='stop_tracking')
async def stop_tracking(ctx):
    check_transactions.stop()
    await ctx.send('Transaction tracking stopped!')

# Run the bot
bot.run(DISCORD_BOT_TOKEN)
