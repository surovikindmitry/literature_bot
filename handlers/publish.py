from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from handlers.description import DescriptionState
from keyboards.main_menu import main_keyboard
from config import config

router = Router()


# ... (импорты остаются теми же)

@router.message(F.text == "Опубликовать")
async def publish_to_channel(message: Message, state: FSMContext):
    data = await state.get_data()
    formatted_text = data.get('formatted_text')
    photo = data.get('photo')

    if not formatted_text:
        await message.answer("❌ Нет текста для публикации.")
        return

    try:
        if photo:
            await message.bot.send_photo(
                chat_id=config.ADMIN_CHANNEL_ID,
                photo=photo,
                caption=formatted_text,
                parse_mode="HTML"
            )
        else:
            await message.bot.send_message(
                chat_id=config.ADMIN_CHANNEL_ID,
                text=formatted_text,
                parse_mode="HTML"
            )

        await message.answer(
            "✅ Пост успешно опубликован в канале!",
            reply_markup=main_keyboard()
        )
    except Exception as e:
        await message.answer(
            f"❌ Ошибка публикации: {str(e)}",
            reply_markup=main_keyboard()
        )

    await state.clear()


@router.message(F.text == "Иллюстрация")
async def request_image(message: Message, state: FSMContext):
    await message.answer(
        "🖼 Пришлите изображение, которое будет добавлено к посту.",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(DescriptionState.waiting_for_image)


@router.message(DescriptionState.waiting_for_image, F.photo)
async def process_image(message: Message, state: FSMContext):
    photo = message.photo[-1].file_id
    data = await state.get_data()

    await state.update_data(photo=photo)

    await message.answer_photo(
        photo,
        caption=data['formatted_text'],
        parse_mode="HTML",
        reply_markup=description_keyboard()
    )

    await state.set_state(DescriptionState.waiting_for_edit)


@router.message(F.text == "Редактировать")
async def request_edit(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(
        "✏️ Пришлите исправленный текст описания:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(DescriptionState.waiting_for_edit)


@router.message(DescriptionState.waiting_for_edit, F.text)
async def process_edit(message: Message, state: FSMContext):
    edited_text = message.text
    data = await state.get_data()

    # Обновляем текст, сохраняя структуру
    formatted_text = (
        f"<b><font color='#00e600'>{data['book']} - {data['author']}</font></b>\n\n"
        f"<b><i>\"{extract_quote(edited_text)}\"</i></b>\n\n"
        f"{extract_description(edited_text)}"
    )

    await state.update_data(formatted_text=formatted_text, raw_text=edited_text)

    if data.get('photo'):
        await message.answer_photo(
            data['photo'],
            caption=formatted_text,
            parse_mode="HTML",
            reply_markup=description_keyboard()
        )
    else:
        await message.answer(
            formatted_text,
            parse_mode="HTML",
            reply_markup=description_keyboard()
        )

    await state.set_state(DescriptionState.waiting_for_edit)