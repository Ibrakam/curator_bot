import logging

from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from course.bot.states import UserStates
from db.service import add_request, update_request_status, close_request_in_database, download_media, get_contacts, \
    get_user_by_id
from filter import admin_id

sales_router = Router()


@sales_router.message(F.text == "Позвоните мне", UserStates.sales_menu)
async def call_me_request(message: types.Message):
    request_id = await add_request(message.from_user.id, 'sales_department', 'call_request')
    await message.answer(f"Ваша заявка No {request_id} принята. Мы свяжемся с вами в ближайшее время.")

    # Создаем инлайн-клавиатуру для администратора
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Связались с клиентом",
                callback_data=f"confirm_call_{request_id}"
            )
        ]
    ])

    admin_message = (f"Новая заявка No{request_id}\n"
                     f"Пользователь: {message.from_user.full_name}\n"
                     f"ID пользователя: {message.from_user.id}\n"
                     f"Тип заявки: Обратный звонок")

    try:
        admin_chat_id = await admin_id(message.from_user.id, "sales_department")
        await message.bot.send_message(admin_chat_id, admin_message, reply_markup=keyboard)
    except Exception as e:
        logging.error(f"Ошибка отправки сообщения администратору: {e}")


@sales_router.callback_query(lambda c: c.data.startswith("confirm_call_"))
async def process_call_confirmation(callback: types.CallbackQuery, state: FSMContext):
    # Извлекаем ID заявки из callback_data
    request_id = callback.data.split("_")[-1]

    # Просим администратора загрузить запись разговора
    await callback.message.answer(f"Пожалуйста, прикрепите запись разговора по заявке No{request_id}")

    # Устанавливаем состояние ожидания файла
    await state.set_state(UserStates.waiting_for_call_record)

    # Сохраняем ID заявки в состоянии
    await state.update_data({"current_request_id": request_id})


@sales_router.message(UserStates.waiting_for_call_record)
async def save_call_record(message: types.Message, state: FSMContext):
    if message.content_type in ['audio', 'document', 'video', 'video_note', 'voice']:
        # Получаем сохраненный ранее ID заявки
        state_data = await state.get_data()
        request_id = state_data.get('current_request_id')

        # Сохраняем файл
        file = await download_media(message)

        # Обновляем статус заявки в базе данных
        await update_request_status(request_id, 'completed', file_path=file)

        # Создаем клавиатуру для подтверждения
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Заявка закрыта",
                    callback_data=f"close_request_{request_id}"
                )
            ]
        ])

        # Отправляем сообщение с подтверждением
        await message.answer(f"Запись разговора для заявки No{request_id} сохранена.", reply_markup=keyboard)

        # Очищаем состояние
        await state.clear()
        return
    await message.answer("Пожалуйста, прикрепите запись разговора.")
    return


@sales_router.callback_query(lambda c: c.data.startswith("close_request_"))
async def close_request(callback: types.CallbackQuery):
    # Извлекаем ID заявки из callback_data
    request_id = callback.data.split("_")[-1]

    # Окончательно закрываем заявку
    await close_request_in_database(int(request_id))

    await callback.message.edit_text(f"Заявка No{request_id} закрыта ✅")


@sales_router.message(UserStates.sales_menu, F.text == "Получить контакты")
async def get_contacts_message(message: types.Message):
    contacts = await get_contacts()
    contacts_text = "\n".join([f"{i['name']}: {i['phone_number']}" for i in contacts])
    await message.answer(f"Контакты отдела продаж:\n{contacts_text}")


@sales_router.message(UserStates.sales_menu, F.text == "Написать в Telegram")
async def go_to_telegram(message: types.Message):
    contacts = await get_contacts(contact_type="username")
    contacts_text = "\n".join([f"{i['name']}: {i['username']}" for i in contacts])
    await message.answer(f"Отдел продаж в Telegram:\n{contacts_text}")


@sales_router.message(UserStates.sales_menu, F.text == "Оставить жалобу")
async def send_complaint(message: types.Message, state: FSMContext):
    await message.answer("Напишите вашу жалобу:")
    await state.set_state(UserStates.sales_complaint)


@sales_router.message(UserStates.sales_complaint)
async def process_complaint(message: types.Message, state: FSMContext):
    await message.answer("Спасибо за вашу жалобу!")
    user = await get_user_by_id(message.from_user.id)
    print(user)
    print(f"Жалоба от {user.full_name}: {message.text}")
    admin_chat_id = await admin_id(message.from_user.id, "sales_department")
    await message.bot.send_message(admin_chat_id, f"Жалоба от {user.full_name}:\n{message.text}")
    await state.set_state(UserStates.sales_menu)

