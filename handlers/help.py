from aiogram import Router, types
from aiogram.filters import Command
from keyboards.main_menu import main_keyboard

router = Router()

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "📚 Помощь по использованию бота:\n\n"
        "1. Нажмите 'Начать' для запуска\n"
        "2. Введите автора и название книги в формате:\n"
        "   • Автор - Название книги\n"
        "   • Автор \"Название книги\"\n"
        "   Пример: Толстой \"Война и мир\"\n\n"
        "3. После проверки нажмите 'Запрос' для генерации\n"
        "4. Вы получите:\n"
        "   • Цитату из книги (выделенную курсивом)\n"
        "   • Краткое мотивирующее описание (до 350 слов)\n\n"
        "5. Дополнительные опции:\n"
        "   🖼 Иллюстрация - добавить изображение к посту\n"
        "   ✏️ Редактировать - изменить текст описания\n"
        "   📢 Опубликовать - отправить в телеграм-канал\n\n"
        "Бот использует нейросети через сервис OpenRouter.ai"
    )
    await message.answer(help_text, reply_markup=main_keyboard())