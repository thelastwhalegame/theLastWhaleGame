import json
from web3 import Web3
from datetime import datetime
import requests
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from configProd import API_URL, API_KEY, CONTRACT_ADDRESS, WEB3_PROVIDER_URL, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, RPC_URL

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

def interact_with_contract_balance(api_url, api_key, contract_address):
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

def interact_with_contract_endTime(api_url, api_key, contract_address):
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
                method_name = "endTime"
                matching_methods = [item for item in contract_abi if item['type'] == 'function' and item['name'] == method_name]
                web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))
                contract = web3.eth.contract(address=contract_address, abi=contract_abi)
                if matching_methods:
                    method = matching_methods[0]
                    result = contract.functions[method['name']]().call()
                    try:
                        result = int(result)
                    except ValueError:
                        # Если не получается, попробуем распарсить как дату в формате ISO
                        try:
                            result = datetime.fromisoformat(result)
                            formatted_date_time = result.strftime('%Y-%m-%d %H:%M:%S')
                            print(formatted_date_time)
                            return formatted_date_time

                        except ValueError:
                            print(f"Failed to convert result to integer or parse as datetime: {result}")
                            raise
                    formatted_date_time = datetime.fromtimestamp(result).strftime('%Y-%m-%d %H:%M:%S')
                    return formatted_date_time
                else:
                    print(f"Method '{method_name}' not found in contract ABI.")
            else:
                return "Error: Empty ABI"
        else:
            return f"Error: {data['message']}"
    else:
        return f"Error: HTTP request failed with status code {response.status_code}"

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


def interact_with_contract_currentWinner(api_url, api_key, contract_address):
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
                method_name = "lastDepositor"
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

menu_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
menu_keyboard.add(types.KeyboardButton("/balance"))
menu_keyboard.add(types.KeyboardButton("/endTime"))
menu_keyboard.add(types.KeyboardButton("/gameStatus"))
menu_keyboard.add(types.KeyboardButton("/winner"))

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    # Приветственное сообщение с кнопками
    await message.answer("Hello! Select an option from the menu:", reply_markup=menu_keyboard)

@dp.message_handler(commands=['endTime'])
async def endtime(message: types.Message):
    try:
        result = interact_with_contract_endTime(API_URL, API_KEY, CONTRACT_ADDRESS)
        #formatted_date_time = datetime.fromtimestamp(result).strftime('%Y-%m-%d %H:%M:%S')
        await send_telegram_message(f"End time: {result}")
    except Exception as e:
        print(f"An error occurred: {e}")
        await send_telegram_message(f"An error occurred: {e}")

@dp.message_handler(commands=['balance'])
async def get_balance(message: types.Message):
    try:
        result = interact_with_contract_balance(API_URL, API_KEY, CONTRACT_ADDRESS)
        await send_telegram_message(f"{result}")
    except Exception as e:
        print(f"An error occurred: {e}")
        await send_telegram_message(f"An error occurred: {e}")


@dp.message_handler(commands=['gameStatus'])
async def game_status(message: types.Message):
    try:
        result = interact_with_contract(API_URL, API_KEY, CONTRACT_ADDRESS)
        if result:
            await send_telegram_message("Game over")
        else:
            await send_telegram_message("The game is active")
    except Exception as e:
        print(f"An error occurred: {e}")
        await send_telegram_message(f"An error occurred: {e}")

@dp.message_handler(commands=['winner'])
async def winner_status(message: types.Message):
    try:
        result = interact_with_contract_currentWinner(API_URL, API_KEY, CONTRACT_ADDRESS)
        await send_telegram_message(f"https://testnet.bscscan.com/address/{result}")
    except Exception as e:
        print(f"An error occurred: {e}")
        await send_telegram_message(f"An error occurred: {e}")

async def send_telegram_message(message):
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=types.ParseMode.MARKDOWN)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
