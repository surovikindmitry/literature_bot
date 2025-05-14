from aiogram import Router, types
from aiogram.filters import Command
from keyboards.main_menu import main_keyboard

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_text = (
        "📚 Добро пожаловать в бот описания произведений литературы!\n\n"
        "Я могу создать описание книги с цитатой с помощью нейросети.\n\n"
        "Формат ввода:\n"
        "• Автор - Название книги\n"
        "• Автор \"Название книги\"\n\n"
        "Например:\n"
        "Достоевский - Преступление и наказание\n"
        "Толстой \"Война и мир\"\n\n"
        "Нажмите 'Начать' для старта или 'Помощь' для инструкций."
    )
    await message.answer(welcome_text, reply_markup=main_keyboard())