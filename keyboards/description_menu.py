from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def description_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Иллюстрация"), KeyboardButton(text="Редактировать")],
            [KeyboardButton(text="Опубликовать"), KeyboardButton(text="Отмена")]
        ],
        resize_keyboard=True
    )