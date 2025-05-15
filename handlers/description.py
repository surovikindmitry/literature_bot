import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton  # Добавлено
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.main_menu import main_keyboard
from keyboards.description_menu import description_keyboard
import aiohttp
from config import config

router = Router()

class DescriptionState(StatesGroup):
    waiting_for_book = State()
    waiting_for_edit = State()
    waiting_for_image = State()

@router.message(F.text == "Начать")
async def start_description(message: Message, state: FSMContext):
    await message.answer(
        "Введите автора и название книги в формате:\n"
        "Автор - Название книги\n"
        "или\n"
        "Автор \"Название книги\"",
        reply_markup=ReplyKeyboardRemove()  # Убрано types.
    )
    await state.set_state(DescriptionState.waiting_for_book)

@router.message(DescriptionState.waiting_for_book)
async def process_book(message: Message, state: FSMContext):
    input_text = message.text.strip()

    # Разделяем на автора и название по кавычкам или дефису с учетом пробелов
    if '"' in input_text:
        parts = re.split(r'"(.+?)"', input_text)  # Ищем текст в кавычках
        if len(parts) >= 3:
            author = parts[0].strip()
            book = parts[1].strip()
        else:
            await message.answer("❌ Неверный формат. Используйте: Автор \"Название книги\"")
            return
    else:
        # Разделяем по первому дефису/тире, если нет кавычек
        parts = re.split(r'\s*[-—]\s*', input_text, maxsplit=1)
        if len(parts) == 2:
            author, book = parts[0].strip(), parts[1].strip()
        else:
            await message.answer("❌ Неверный формат. Используйте: Автор - Название книги")
            return

    # Проверка минимальной длины
    if len(author) < 2 or len(book) < 2:
        await message.answer("❌ Автор и название должны быть не короче 2 символов.")
        return

    await state.update_data(author=author, book=book)

    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Запрос"), KeyboardButton(text="Отмена")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        f"✅ Принято:\nАвтор: {author}\nКнига: {book}\n\n"
        "Нажмите 'Запрос' для генерации описания или 'Отмена' для возврата.",
        reply_markup=markup
    )

@router.message(F.text == "Запрос")
async def make_ai_request(message: Message, state: FSMContext):
    data = await state.get_data()
    author = data.get('author')
    book = data.get('book')

    prompt = config.AI_PROMPT.format(book=book, author=author)

    await message.answer("⏳ Генерирую описание...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": config.AI_MODEL,
                        "messages": [{"role": "user", "content": prompt}]
                    }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    ai_response = result['choices'][0]['message']['content']

                    # Форматируем ответ
                    formatted_text = format_ai_response(book, author, ai_response)

                    await state.update_data(
                        formatted_text=formatted_text,
                        raw_text=ai_response,
                        photo=None
                    )
                    await message.answer(
                        formatted_text,
                        parse_mode="HTML",
                        reply_markup=description_keyboard()
                    )
                else:
                    error = await response.text()
                    await message.answer(
                        f"❌ Ошибка нейросети: {error}",
                        reply_markup=main_keyboard()
                    )
    except Exception as e:
        await message.answer(
            f"❌ Ошибка соединения: {str(e)}",
            reply_markup=main_keyboard()
        )

    await state.set_state(DescriptionState.waiting_for_edit)


def format_ai_response(book, author, ai_response):
    # Извлекаем цитату (первое предложение в кавычках)
    quote_match = re.search(r'"([^"]*)"', ai_response)
    quote = quote_match.group(1) if quote_match else "Интересная цитата из книги"

    # Описание - всё после цитаты
    description = ai_response[quote_match.end() + 1:] if quote_match else ai_response
    description = description.strip()

    return (
        f"<b>📖 {book}</b>\n"
        f"<i>✍️ {author}</i>\n\n"
        f"<b><i>📌 \"{quote}\"</i></b>\n\n"
        f"{description}"
    )
def extract_quote(text):
    quote_match = re.search(r'"([^"]*)"', text)
    return quote_match.group(1) if quote_match else "Цитата из книги"

def extract_description(text):
    parts = re.split(r'"[^"]*"', text, 1)
    return parts[-1].strip() if len(parts) > 1 else text