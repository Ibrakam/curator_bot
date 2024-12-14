import logging

from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from course.bot.states import UserStates
from db.service import add_refund, get_user_by_id, update_refund_status
from filter import admin_id

refund_router = Router()


def back():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text="Назад")]])
    return keyboard


@refund_router.message(F.text == 'Возврат', UserStates.education_menu)
async def start_refund_process(message: types.Message, state: FSMContext):
    await message.answer("Процесс возврата. Введите ваше имя:", reply_markup=back())
    await state.set_state(UserStates.refund_name)


@refund_router.message(UserStates.refund_name)
async def refund_name(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        buttons = [
            [KeyboardButton(text="Позвоните мне"),
             KeyboardButton(text="Получить контакты")],
            [KeyboardButton(text='Контакты кураторов'),
             KeyboardButton(text='Анонимная жалоба')],
            [KeyboardButton(text='Возврат'),
             KeyboardButton(text='Вопрос по курсу')],
            [KeyboardButton(text="Назад")]
        ]
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)
        await message.answer("Выберите действие:", reply_markup=keyboard)
        await state.set_state(UserStates.education_menu)
        return

    await state.update_data({"name": message.text})
    await message.answer("Введите вашу фамилию:", reply_markup=back())
    await state.set_state(UserStates.refund_surname)


@refund_router.message(UserStates.refund_surname)
async def refund_details(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await message.answer("Процесс возврата. Введите ваше имя:", reply_markup=back())
        await state.set_state(UserStates.refund_name)
        return

    data = await state.get_data()
    data['surname'] = message.text

    button = [[
        KeyboardButton(text="Узум Савдо"),
        KeyboardButton(text="СММ курс"),
        KeyboardButton(text="Назад")
    ]]

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=button)

    await message.answer("На каком курсе вы обучались?", reply_markup=keyboard)
    await state.update_data(data)
    await state.set_state(UserStates.refund_course)


@refund_router.message(UserStates.refund_course)
async def process_refund(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await message.answer("Введите вашу фамилию:", reply_markup=back())
        await state.set_state(UserStates.refund_surname)
        return

    data = await state.get_data()
    data['course'] = message.text
    await state.update_data(data)

    await message.answer("На каком потоке вы учились?", reply_markup=back())
    await state.set_state(UserStates.refund_stream)


@refund_router.message(UserStates.refund_stream)
async def process_refund(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        button = [[
            KeyboardButton(text="Узум Савдо"),
            KeyboardButton(text="СММ курс"),
            KeyboardButton(text="Назад")
        ]]

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=button)

        await state.set_state(UserStates.refund_course)
        await message.answer("На каком курсе вы обучались?", reply_markup=keyboard)
        return

    data = await state.get_data()
    data['stream'] = message.text

    await message.answer("Укажите причину возврата:", reply_markup=back())
    await state.update_data(data)
    await state.set_state(UserStates.refund_details)


@refund_router.message(UserStates.refund_details)
async def save_refund_request(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await message.answer("На каком потоке вы учились?", reply_markup=back())
        await state.set_state(UserStates.refund_stream)
        return

    data = await state.get_data()

    try:
        new_refund = await add_refund(user_id=message.from_user.id, name=data['name'], surname=data['surname'],
                                      course=data['course'],
                                      stream=data['stream'], reason=message.text)
        inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Связались с клиентом",
                    callback_data=f"refund_{new_refund}"
                )
            ]
        ])
        user = await get_user_by_id(message.from_user.id)
        admin_chat_id = await admin_id(message.from_user.id, "refund")
        # Уведомление администратора о новом возврате
        await message.bot.send_message(admin_chat_id,
                                       f"🔔 Новый запрос на возврат!\n"
                                       f"Имя: {data['name']} {data['surname']}\n"
                                       f"Телефон: {user.phone}\n"
                                       f"Курс: {data['course']}\n"
                                       f"Поток: {data['stream']}\n"
                                       f"Причина: {message.text}",
                                       reply_markup=inline_keyboard
                                       )

        await message.answer(
            "Ваш запрос на возврат принят. "
            "В течение 3-5 рабочих дней с вами свяжется менеджер."
        )
    except Exception as e:
        logging.error(f"Ошибка при сохранении возврата: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")
    buttons = [
        [KeyboardButton(text="Позвоните мне"),
         KeyboardButton(text="Получить контакты")],
        [KeyboardButton(text='Контакты кураторов'),
         KeyboardButton(text='Анонимная жалоба')],
        [KeyboardButton(text='Возврат'),
         KeyboardButton(text='Вопрос по курсу')],
        [KeyboardButton(text="Назад")]
    ]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)
    await message.answer("Выберите действие:", reply_markup=keyboard)
    await state.set_state(UserStates.education_menu)


@refund_router.callback_query(lambda c: c.data.startswith("refund_"))
async def process_refund_call_record(callback: types.CallbackQuery, state: FSMContext):
    # Извлекаем ID заявки из callback_data
    request_id = callback.data.split("_")[-1]
    print(f"Current state: {await state.get_state()}")

    # Просим администратора загрузить запись разговора
    await callback.message.answer(f"Пожалуйста, прикрепите запись разговора по возврату No{request_id}")

    # Устанавливаем состояние ожидания файла
    await state.set_state(UserStates.refund_request)

    # Сохраняем ID заявки в состоянии
    await state.update_data({"current_request_id": request_id})


@refund_router.message(UserStates.refund_request)
async def save_call_record(message: types.Message, state: FSMContext):
    print(await state.get_state())
    if message.content_type in ['audio', 'document', 'video', 'video_note', 'voice']:
        # Получаем сохраненный ранее ID заявки
        state_data = await state.get_data()
        request_id = state_data.get('current_request_id')

        # Сохраняем файл
        # file = await download_media(message)

        # Создаем клавиатуру для подтверждения
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Одобрить возврат",
                    callback_data=f"confirm_refund_{request_id}"
                ), InlineKeyboardButton(
                    text="Отклонить возврат",
                    callback_data=f"reject_refund_{request_id}"
                )
            ]
        ])

        # Отправляем сообщение с подтверждением
        await message.answer(f"Запись разговора для возврата No{request_id} сохранена.", reply_markup=keyboard)

        # Очищаем состояние
        await state.clear()
        return
    await message.answer("Пожалуйста, прикрепите запись разговора.")
    return


@refund_router.callback_query(lambda c: c.data.startswith("confirm_refund_"))
async def close_request(callback: types.CallbackQuery):
    # Извлекаем ID заявки из callback_data
    request_id = callback.data.split("_")[-1]

    # Окончательно закрываем заявку
    await update_refund_status(int(request_id), 'approved')

    await callback.message.edit_text(f"Возврат No{request_id} закрыт ✅")


@refund_router.callback_query(lambda c: c.data.startswith("reject_refund_"))
async def close_request(callback: types.CallbackQuery):
    # Извлекаем ID заявки из callback_data
    request_id = callback.data.split("_")[-1]

    # Окончательно закрываем заявку
    await update_refund_status(int(request_id), 'rejected')

    await callback.message.edit_text(f"Возврат No{request_id} отклонен ❌")
