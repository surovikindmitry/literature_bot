import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
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
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(DescriptionState.waiting_for_book)


@router.message(DescriptionState.waiting_for_book)
async def process_book(message: Message, state: FSMContext):
    input_text = message.text.strip()

    # Улучшенная проверка формата
    if '-' in input_text:
        parts = [part.strip() for part in input_text.split('-', 1)]
    elif '"' in input_text:
        parts = [part.strip() for part in input_text.split('"', 1)]
        parts[1] = parts[1].replace('"', '')
    else:
        await message.answer(
            "❌ Неверный формат. Используйте:\n"
            "Автор - Название книги\n"
            "или\n"
            "Автор \"Название книги\""
        )
        return

    if len(parts) != 2 or len(parts[0]) < 2 or len(parts[1]) < 2:
        await message.answer(
            "❌ Недостаточно данных. Укажите автора (минимум 2 символа) "
            "и название книги (минимум 2 символа)."
        )
        return

    author, book = parts

    await state.update_data(author=author, book=book)

    markup = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Запрос"), types.KeyboardButton(text="Отмена")]
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
        f"<b><font color='#00e600'>{book} - {author}</font></b>\n\n"
        f"<b><i>\"{quote}\"</i></b>\n\n"
        f"{description}"
    )

def extract_quote(text):
    quote_match = re.search(r'"([^"]*)"', text)
    return quote_match.group(1) if quote_match else "Цитата из книги"

def extract_description(text):
    parts = re.split(r'"[^"]*"', text, 1)
    return parts[-1].strip() if len(parts) > 1 else text