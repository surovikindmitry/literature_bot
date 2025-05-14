from aiogram import Router, types
from aiogram.filters import Command
from keyboards.main_menu import main_keyboard

router = Router()

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "📚 Помощь по использованию бота:\n\n"
        "1. Нажмите 'Начать' для запуска процесса\n"
        "2. Введите автора и название книги в указанном формате\n"
        "3. После проверки формата нажмите 'Запрос' для получения описания\n"
        "4. Вы получите цитату из книги и мотивирующее описание\n"
        "5. Дополнительные опции:\n"
        "   - Добавить иллюстрацию\n"
        "   - Отредактировать текст\n"
        "   - Опубликовать в канале\n\n"
        "Бот использует современные нейросети для генерации содержательных описаний литературных произведений."
    )
    await message.answer(help_text, reply_markup=main_keyboard())