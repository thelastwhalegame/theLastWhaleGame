import requests
from web3 import Web3
from aiogram import Bot, Dispatcher, types
from aiogram import executor
from configProd import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, API_URL, API_KEY, CONTRACT_ADDRESS, RPC_URL

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

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

async def send_telegram_message(message):
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=types.ParseMode.MARKDOWN)

@dp.message_handler(commands=['balance'])
async def balance_command(message: types.Message):
    try:
        result = interact_with_contract(API_URL, API_KEY, CONTRACT_ADDRESS)
        await send_telegram_message(result)
    except Exception as e:
        print(f"An error occurred: {e}")
        await send_telegram_message(f"An error occurred: {e}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
