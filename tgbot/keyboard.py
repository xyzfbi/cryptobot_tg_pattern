from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, \
    BotCommand


def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Timeframe ⏳"), ],
        [KeyboardButton(text="Choose coin 🪙")],
        [KeyboardButton(text="Analyze 👀")],
        [KeyboardButton(text="Help 🚑")],
    ], resize_keyboard=True , one_time_keyboard=False)

    return keyboard
def get_timeframe_keyboard():
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="15 minutes")],
        [KeyboardButton(text="1 hour")],
        [KeyboardButton(text="4 hours")],
    ], resize_keyboard=True, one_time_keyboard=True)

    return keyboard
