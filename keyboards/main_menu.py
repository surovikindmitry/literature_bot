from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Начать"), KeyboardButton(text="Помощь")]
        ],
        resize_keyboard=True
    )