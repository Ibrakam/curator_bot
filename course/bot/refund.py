import logging
from collections import defaultdict

from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from course.bot.states import UserStates
from db.service import add_refund, get_user_by_id, update_refund_status, download_media
from filter import admin_id

refund_router = Router()


def back():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text="Ortga")]])
    return keyboard


@refund_router.message(F.text == 'Qaytarish', UserStates.education_menu)
async def start_refund_process(message: types.Message, state: FSMContext):
    await message.answer("Qaytarish jarayoni. Ismingizni kiriting:", reply_markup=back())
    await state.set_state(UserStates.refund_name)


@refund_router.message(UserStates.refund_name)
async def refund_name(message: types.Message, state: FSMContext):
    if message.text == "Ortga":
        buttons = [
            [KeyboardButton(text="Menga qo'ng'iroq qiling"),
             KeyboardButton(text="Kontaktlarni olish")],
            [KeyboardButton(text='Kuratorlarning kontaktlari'),
             KeyboardButton(text='Anonim shikoyat')],
            [KeyboardButton(text='Qaytarish'),
             KeyboardButton(text='Kurs bo‘yicha savol')],
            [KeyboardButton(text="Ortga")]
        ]
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)
        await message.answer("Harakatni tanlang:", reply_markup=keyboard)
        await state.set_state(UserStates.education_menu)
        return

    await state.update_data({"name": message.text})
    await message.answer("Familiyangizni kiriting:", reply_markup=back())
    await state.set_state(UserStates.refund_surname)


@refund_router.message(UserStates.refund_surname)
async def refund_details(message: types.Message, state: FSMContext):
    if message.text == "Ortga":
        await message.answer("Qaytarish jarayoni. Ismingizni kiriting:", reply_markup=back())
        await state.set_state(UserStates.refund_name)
        return

    data = await state.get_data()
    data['surname'] = message.text

    button = [[
        KeyboardButton(text="Uzum Savdo"),
        KeyboardButton(text="SMM kursi"),
        KeyboardButton(text="Ortga")
    ]]

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=button)

    await message.answer("Qaysi kursda o'qigansiz?", reply_markup=keyboard)
    await state.update_data(data)
    await state.set_state(UserStates.refund_course)


@refund_router.message(UserStates.refund_course)
async def process_refund(message: types.Message, state: FSMContext):
    if message.text == "Ortga":
        await message.answer("Familiyangizni kiriting:", reply_markup=back())
        await state.set_state(UserStates.refund_surname)
        return

    data = await state.get_data()
    data['course'] = message.text
    await state.update_data(data)

    await message.answer("Qaysi oqimda o‘qigansiz?", reply_markup=back())
    await state.set_state(UserStates.refund_stream)


@refund_router.message(UserStates.refund_stream)
async def process_refund(message: types.Message, state: FSMContext):
    if message.text == "Ortga":
        button = [[
            KeyboardButton(text="Uzum Savdo"),
            KeyboardButton(text="SMM kursi"),
            KeyboardButton(text="Ortga")
        ]]

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=button)

        await state.set_state(UserStates.refund_course)
        await message.answer("Qaysi kursda o'qigansiz?", reply_markup=keyboard)
        return

    data = await state.get_data()
    data['stream'] = message.text

    await message.answer("Qaytarish sababini kiriting:", reply_markup=back())
    await state.update_data(data)
    await state.set_state(UserStates.refund_details)


REQUEST_MESSAGES = defaultdict(dict)

REQUEST_STATUSES = {}


@refund_router.message(UserStates.refund_details)
async def save_refund_request(message: types.Message, state: FSMContext):
    if message.text == "Ortga":
        await message.answer("Qaysi oqimda o‘qigansiz?", reply_markup=back())
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
                    text="✅ Mijoz bilan bog‘landik",
                    callback_data=f"refund_{new_refund}"
                )
            ]
        ])
        user = await get_user_by_id(message.from_user.id)
        admin_chat_id = await admin_id("refund")
        admin_message = (f"Yangi qaytarish so‘rovi!\n"
                         f"Ismi: {data['name']} {data['surname']}\n"
                         f"Telefon: {user.phone}\n"
                         f"Kurs: {data['course']}\n"
                         f"Oqim: {data['stream']}\n"
                         f"Sabab: {message.text}")
        for admin in admin_chat_id:  # admin_id теперь гарантированно int
            if isinstance(admin, (int, str)):  # Проверяем тип данных
                sent_msg = await message.bot.send_message(
                    chat_id=int(admin),  # Преобразуем в int (если строка)
                    text=admin_message,
                    reply_markup=inline_keyboard
                )
            # Запоминаем, какому админу (admin_id) какое сообщение (message_id) отправили
            REQUEST_MESSAGES[new_refund][admin_id] = sent_msg.message_id
        # Yangi qaytarish haqida administratorni xabardor qilish

        await message.answer(
            "Sizning qaytarish so‘rovingiz qabul qilindi. "
            "3-5 ish kuni ichida menejer siz bilan bog‘lanadi."
        )
    except Exception as e:
        logging.error(f"Qaytarishni saqlashda xato: {e}")
        await message.answer("Xatolik yuz berdi. Keyinroq urinib ko'ring.")
    buttons = [
        [KeyboardButton(text="Menga qo'ng'iroq qiling"),
         KeyboardButton(text="Kontaktlarni olish")],
        [KeyboardButton(text='Kuratorlarning kontaktlari'),
         KeyboardButton(text='Anonim shikoyat')],
        [KeyboardButton(text='Qaytarish'),
         KeyboardButton(text='Kurs bo‘yicha savol')],
        [KeyboardButton(text="Ortga")]
    ]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)
    await message.answer("Harakatni tanlang:", reply_markup=keyboard)
    await state.set_state(UserStates.education_menu)


@refund_router.callback_query(lambda c: c.data.startswith("refund_"))
async def process_refund_call_record(callback: types.CallbackQuery, state: FSMContext):
    # Callback_data dan so‘rov ID sini chiqaramiz
    data = callback.data
    # формат: "confirm_call_12345"
    request_id_str = data.split("_")[-1]
    request_id = int(request_id_str)
    print(f"Joriy holat: {await state.get_state()}")

    if REQUEST_STATUSES.get(request_id):
        # Уже обработана. Показываем alert.
        await callback.answer("Bu so‘rov allaqachon boshqa administrator tomonidan qayta ishlangan.",
                              show_alert=True)
        return

    # Administratorni suhbat yozuvini yuklashga taklif qilamiz
    await callback.message.answer(f"№{request_id} qaytarishga oid suhbat yozuvini yuklang")

    # Faylni kutish holatini o‘rnatamiz
    await state.set_state(UserStates.refund_request)

    # So‘rov ID sini holatda saqlaymiz
    await state.update_data({"current_request_id": request_id})

    REQUEST_STATUSES[request_id] = True

    # чтобы показать, что заявка уже в обработке (или закрыта)
    admin_msg_dict = REQUEST_MESSAGES.get(request_id, {})

    who_accepted = callback.from_user.full_name
    text_for_all = f"So‘rov №{request_id} allaqachon qabul qilingan.\nUni bajarayotgan: {who_accepted}"

    for admin, msg_id in admin_msg_dict.items():
        try:
            # Можно либо отредактировать текст, либо убрать инлайн-кнопки
            # Ниже пример замены текста (кнопку убираем вообще)
            await callback.message.bot.edit_message_text(
                chat_id=admin,
                message_id=msg_id,
                text=text_for_all
            )
        except Exception as e:
            logging.error(f"Не удалось отредактировать сообщение для админа {admin_id}: {e}")


@refund_router.message(UserStates.refund_request)
async def save_call_record(message: types.Message, state: FSMContext):
    print(await state.get_state())
    supported_media_types = ['audio', 'document', 'video', 'video_note', 'voice']

    # Kontent turini tekshiramiz
    if message.content_type in supported_media_types:
        # Ilgari saqlangan so‘rov ID sini olamiz
        state_data = await state.get_data()
        request_id = state_data.get('current_request_id')
        file_path = await download_media(message)
        state_data['file_path'] = file_path

        if file_path:
            # Tasdiqlash uchun klaviatura yaratamiz
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Qaytarishni tasdiqlash",
                        callback_data=f"confirm_refund_{request_id}"
                    ), InlineKeyboardButton(
                    text="Qaytarishni rad etish",
                    callback_data=f"reject_refund_{request_id}"
                )
                ]
            ])
            await state.update_data(state_data)
            # Tasdiqlash xabarini yuboramiz
            await message.answer(f"№{request_id} qaytarishga oid suhbat yozuvi saqlandi.", reply_markup=keyboard)

            return
    await message.answer("Iltimos, suhbat yozuvini yuklang.")
    return


@refund_router.callback_query(lambda c: c.data.startswith("confirm_refund_"))
async def close_request(callback: types.CallbackQuery, state: FSMContext):
    # Callback_data dan so‘rov ID sini chiqaramiz
    request_id = callback.data.split("_")[-1]
    data = await state.get_data()
    # So‘rovni yakuniy tasdiqlaymiz
    await update_refund_status(int(request_id), 'approved', file_path=data.get('file_path'))
    await state.clear()
    await callback.message.edit_text(f"№{request_id} qaytarish yopildi ✅")


@refund_router.callback_query(lambda c: c.data.startswith("reject_refund_"))
async def close_request(callback: types.CallbackQuery):
    # Callback_data dan so‘rov ID sini chiqaramiz
    request_id = callback.data.split("_")[-1]

    # So‘rovni rad etamiz
    await update_refund_status(int(request_id), 'rejected')

    await callback.message.edit_text(f"№{request_id} qaytarish rad etildi ❌")
