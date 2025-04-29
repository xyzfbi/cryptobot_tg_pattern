from aiogram import Bot, Router, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from dotenv import load_dotenv
import asyncio
import os
import logging
import keyboard as kb
import src.receive_bybit as rcv_bybit
import src.find_trend as find_trend
import src.data_to_jpg as graph
import csv

def load_valid_coins(csv_path="coins.csv"):
    coins = set()
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            coin = row["symbol"].strip().upper()
            coins.add(coin)
    return coins

load_dotenv()  # енв файлик
TOKEN = os.getenv("API_KEY")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
router = Router()  # a router

VALID_COINS = load_valid_coins()
user_states = {}
user_data = {}
STATE_IDLE = "idle"
STATE_WAITING_COIN = "waiting_coin"


@router.message(Command(commands="start"))
async def send_welcome(message: Message):
    user_id = message.chat.id
    user_states[user_id] = STATE_IDLE

    keyboard = kb.get_main_keyboard()
    user_name = message.from_user.username
    welcome_text = (f"Hi, @{user_name}!"
                        f"\n\nI am a bot for analyzing cryptocurrency movements using patterns and technical analysis😎!"
                        f"\n\nAvailable commands: /start, /help"
                        f"\nPlease choose one of the following commands by the keyboard below"
                        f"\n\nMade by HSE students.")

    await message.reply(welcome_text, reply_markup=keyboard)

@router.message(lambda message: message.text.strip().lower() in ["help", "/help"])
async def send_help(message: Message):
    keyboard = kb.get_main_keyboard()
    help_text =("Instruction for using our bot: \n\n"
                "1. /start - run the bot and show main menu\n"
                "2. /help - show this help message\n\n"
                "3. Timeframe - by the click show timeframes to analyze: 15 minutes, 1 hour, 4 hours\n"
                "After choice, bot will confirm it and show the check with in the box of the selected timeframe.\n\n"
                "4. Choose coin - click to enter short name of pair of coin (BTCUSDT, SOLUSDT, DOGEUSDT)\n"
                "If the coin exist - bot confirm it, otherwise, the bot will prompt you to enter again \n\n"
                "5. Analyze - starting to analyze your coin, after the process - show you a plot with next movement of crypto\n")
    await message.reply(help_text, reply_markup=keyboard)
def analyzer(symbol, timeframe):
    timeframes = {
        '15 minutes': 15,
        '1 hour': 60,
        '4 hours': 240,
        '1 day': 'D'
    }

    keys = list(timeframes.values()) # 15 60 'D'
    cur_tf = timeframes[timeframe] # 15

    idx = keys.index(cur_tf) # 0
    next_tf = keys[idx + 1]

    analyze_obj = find_trend.TradingStrategy(symbol, cur_tf, next_tf)
    return analyze_obj, cur_tf, next_tf

@router.message()
async def handle_message(message: Message):
    user_id = message.chat.id
    text = message.text.strip()

    user_data.setdefault(user_id, {"symbol": "", "timeframe": ""})

    if user_id not in user_states:
        user_states[user_id] = STATE_IDLE

    if user_states.get(user_id, STATE_IDLE) == STATE_WAITING_COIN:
        coin = text.upper()
        if coin in VALID_COINS:
            user_data[user_id]["symbol"] = coin + "USDT"
            await message.answer("Coin selected", reply_markup=kb.get_main_keyboard())
        else:
            await message.answer("Entered nonexistent coin")
        user_states[user_id] = STATE_IDLE
        return

    if text == "Timeframe":

        await message.answer("Choose timeframe:", reply_markup=kb.get_timeframe_keyboard())

    elif text in ["15 minutes", "1 hour", "4 hours"]:
        user_data[user_id]["timeframe"] = text
        await message.answer(f"Selected timeframe - {text}", reply_markup=kb.get_main_keyboard())

    elif text == "Choose coin":

        user_states[user_id] = STATE_WAITING_COIN
        await message.answer("Enter coin name", reply_markup=None)

    elif text == "Analyze":
        symbol = user_data[user_id].get("symbol")
        timeframe = user_data[user_id].get("timeframe")
        if not symbol or not timeframe:
            await message.answer("Please select a coin and a timeframe before analyzing.",
                                 reply_markup=kb.get_main_keyboard())
            return

        await message.answer("Analyzing your coin", reply_markup=None)

        result_obj, current_timeframe, next_timeframe = analyzer(symbol, timeframe)

        data_obj = rcv_bybit.CandlesData(symbol)
        for_jpg_data = data_obj.get_pattern_indicators_data(timeframe=current_timeframe)

        buf_jpg = graph.depict_candle_graph(for_jpg_data, l_tf=current_timeframe, h_tf=next_timeframe)


        result_text = result_obj.get_res_text()
        await message.answer_photo(photo=FSInputFile(buf_jpg, filename="graph.jpg"),caption= result_text, reply_markup=kb.get_main_keyboard())

    else:
        await message.answer("Please use the menu buttons.", reply_markup=kb.get_main_keyboard())

async def main():
    dp = Dispatcher()
    dp.include_router(router)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
