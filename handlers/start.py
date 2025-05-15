from aiogram import Router, types
from aiogram.filters import Command
from keyboards.main_menu import main_keyboard

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_text = (
    "📚 Добро пожаловать! Введите автора и книгу в формате:\n\n"
    "Через дефис:\n"
    "Федор Достоевский - Преступление и наказание\n\n"
    "В кавычках:\n"
    "Джоан Роулинг \"Гарри Поттер и Дары Смерти\""
    "Нажмите 'Начать' для старта или 'Помощь' для инструкций."
    )
    await message.answer(welcome_text, reply_markup=main_keyboard())