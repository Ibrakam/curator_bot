import logging

from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from course.bot.states import UserStates
from db.service import add_request, download_media, update_request_status, close_request_in_database, get_contacts, \
    get_question, delete_question, save_question
from filter import admin_id

education_router = Router()


@education_router.message(F.text == "Позвоните мне", UserStates.education_menu)
async def call_me_request(message: types.Message):
    request_id = await add_request(message.from_user.id, 'curator', 'call_request')
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
        admin_chat_id = await admin_id(message.from_user.id, "support")
        await message.bot.send_message(admin_chat_id, admin_message, reply_markup=keyboard)
    except Exception as e:
        logging.error(f"Ошибка отправки сообщения администратору: {e}")


@education_router.callback_query(lambda c: c.data.startswith("confirm_call_"))
async def process_call_confirmation(callback: types.CallbackQuery, state: FSMContext):
    # Извлекаем ID заявки из callback_data
    request_id = callback.data.split("_")[-1]

    # Просим администратора загрузить запись разговора
    await callback.message.answer(f"Пожалуйста, прикрепите запись разговора по заявке No{request_id}")

    # Устанавливаем состояние ожидания файла
    await state.set_state(UserStates.waiting_for_call_record)

    # Сохраняем ID заявки в состоянии
    await state.update_data({"current_request_id": request_id})


@education_router.message(UserStates.waiting_for_call_record)
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


@education_router.callback_query(lambda c: c.data.startswith("close_request_"))
async def close_request(callback: types.CallbackQuery):
    # Извлекаем ID заявки из callback_data
    request_id = callback.data.split("_")[-1]

    # Окончательно закрываем заявку
    await close_request_in_database(int(request_id))

    await callback.message.edit_text(f"Заявка No{request_id} закрыта ✅")


@education_router.message(UserStates.education_menu, F.text == "Получить контакты")
async def get_contacts_message(message: types.Message):
    contacts = await get_contacts(role='support', contact_type='all')
    contacts_text = "\n".join([f"{i['name']}: {i['phone_number']}, {i['username']}" for i in contacts])
    await message.answer(f"Контакты поддержки:\n{contacts_text}")


@education_router.message(UserStates.education_menu, F.text == "Контакты кураторов")
async def get_contacts_message(message: types.Message):
    contacts = await get_contacts(role='curator', contact_type='all')
    contacts_text = "\n".join([f"{i['name']}: {i['phone_number']}, {i['username']}" for i in contacts])
    await message.answer(f"Контакты кураторов:\n{contacts_text}")


@education_router.message(UserStates.education_menu, F.text == "Оставить жалобу")
async def send_complaint(message: types.Message, state: FSMContext):
    await message.answer("Напишите вашу жалобу:")
    await state.set_state(UserStates.education_complaint)


@education_router.message(UserStates.education_complaint, F.text == "Анонимная жалоба")
async def process_complaint(message: types.Message, state: FSMContext):
    await message.answer("Спасибо за вашу жалобу!")
    await message.bot.send_message(await admin_id(message.from_user.id, "support"), f"Анонимная жалоба:\n{message.text}")
    await state.set_state(UserStates.education_menu)


@education_router.message(UserStates.education_menu, F.text == "Вопрос по курсу")
async def send_question(message: types.Message, state: FSMContext):
    await message.answer("Напишите ваш вопрос:")
    await state.set_state(UserStates.course_question)


@education_router.message(UserStates.course_question)
async def process_course_question(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    question_text = message.text

    # Сохраняем вопрос в базе данных
    question_id = await save_question(user_id, question_text)

    await message.answer("Ваш вопрос отправлен администратору. Ожидайте ответа.")

    # Уведомление администратора о новом вопросе
    await notify_admin_about_question(question_id, user_id, question_text, message)

    await state.set_state(UserStates.education_menu)


@education_router.message(F.text.startswith("Ответ:"))
async def admin_response_to_question(message: types.Message):
    # Предполагаем, что администратор отправляет ответ в формате "Ответ: [ID вопроса] [текст ответа]"
    try:
        # Парсим сообщение администратора
        _, question_id, *response_parts = message.text.split()
        response_text = " ".join(response_parts)

        # Получаем информацию о вопросе
        question = await get_question(int(question_id))

        if question:
            # Отправляем ответ пользователю
            await message.bot.send_message(
                chat_id=question['user_id'],
                text=f"Ответ на ваш вопрос:\n{response_text}"
            )

            # Обновляем статус вопроса
            await delete_question(int(question_id))

    except Exception as e:
        # Обработка ошибок
        await message.answer(f"Ошибка при обработке ответа: {str(e)}")


async def notify_admin_about_question(question_id, user_id, question_text, message: types.Message):
    # Отправка уведомления администратору о новом вопросе
    admin_chat_id = await admin_id(message.from_user.id, "curator")  # Замените на ID чата администратора
    await message.bot.send_message(
        chat_id=admin_chat_id,
        text=f"Новый вопрос (ID: {question_id}):\n"
             f"От пользователя (ID: {user_id}):\n"
             f"{question_text}\n\n"
             f"Чтобы ответить, отправьте: Ответ: {question_id} [ваш текст]"
    )
