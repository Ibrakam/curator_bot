import logging

from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from course.bot.states import UserStates
from db.service import add_request, update_request_status, close_request_in_database, download_media, get_contacts, \
    get_user_by_id, add_complaint
from filter import admin_id

sales_router = Router()


@sales_router.message(F.text == "Menga qo‘ng‘iroq qiling", UserStates.sales_menu)
async def call_me_request(message: types.Message):
    request_id = await add_request(message.from_user.id, 'sales_department', 'call_request')
    await message.answer(f"Sizning № {request_id} so‘rovingiz qabul qilindi. Tez orada siz bilan bog‘lanamiz.")

    # Admin uchun inline-klaviatura yaratamiz
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Mijoz bilan bog‘landik",
                callback_data=f"confirm_call_{request_id}"
            )
        ]
    ])

    admin_message = (f"Yangi so‘rov №{request_id}\n"
                     f"Foydalanuvchi: {message.from_user.full_name}\n"
                     f"Foydalanuvchi ID: {message.from_user.id}\n"
                     f"So‘rov turi: Qayta qo‘ng‘iroq")

    try:
        admin_chat_id = await admin_id(message.from_user.id, "sales_department")
        await message.bot.send_message(admin_chat_id, admin_message, reply_markup=keyboard)
    except Exception as e:
        logging.error(f"Admin uchun xabar yuborishda xatolik: {e}")


@sales_router.callback_query(lambda c: c.data.startswith("confirm_call_"))
async def process_call_confirmation(callback: types.CallbackQuery, state: FSMContext):
    # Callback_data dan so‘rov ID sini chiqaramiz
    request_id = callback.data.split("_")[-1]

    # Adminni suhbat yozuvini yuklashini so‘raymiz
    await callback.message.answer(f"Iltimos, №{request_id} so‘rov bo‘yicha suhbat yozuvini biriktiring")

    # Faylni kutish holatini o‘rnatamiz
    await state.set_state(UserStates.waiting_for_call_record)

    # Holatda so‘rov ID sini saqlaymiz
    await state.update_data({"current_request_id": request_id})


@sales_router.message(UserStates.waiting_for_call_record)
async def save_call_record(message: types.Message, state: FSMContext):
    supported_media_types = ['audio', 'document', 'video', 'video_note', 'voice']

    # Kontent turini tekshiramiz
    if message.content_type in supported_media_types:
        try:
            # Oldindan saqlangan so‘rov ID sini olamiz
            state_data = await state.get_data()
            request_id = state_data.get('current_request_id')

            if not request_id:
                await message.answer("Tegishli so‘rovni topib bo‘lmadi. Iltimos, jarayonni qayta boshlang.")
                return

            # Faylni saqlash
            file_path = await download_media(message)

            if file_path:
                # So‘rov holatini bazada yangilash
                await update_request_status(request_id, 'completed', file_path=file_path)

                # Tasdiqlash uchun klaviatura yaratamiz
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✅ So‘rov yopildi",
                            callback_data=f"close_request_{request_id}"
                        )
                    ]
                ])

                # Tasdiqlash xabarini yuboramiz
                await message.answer(f"№{request_id} so‘rov bo‘yicha suhbat yozuvi saqlandi.", reply_markup=keyboard)

                # Holatni tozalaymiz
                await state.clear()
            else:
                await message.answer("Faylni saqlashning imkoni bo‘lmadi. Qayta urinib ko‘ring.")

        except Exception as e:
            logging.error(f"Mediafaylni qayta ishlashda xatolik: {e}")
            await message.answer("Faylni qayta ishlashda xatolik yuz berdi. Qayta urinib ko‘ring.")
    else:
        await message.answer("Iltimos, suhbat yozuvini (audio, video yoki ovozli xabar) biriktiring.")


@sales_router.callback_query(lambda c: c.data.startswith("close_request_"))
async def close_request(callback: types.CallbackQuery):
    # Callback_data dan so‘rov ID sini chiqaramiz
    request_id = callback.data.split("_")[-1]

    # So‘rovni yakuniy yopamiz
    await close_request_in_database(int(request_id))

    await callback.message.edit_text(f"№{request_id} so‘rov yopildi ✅")


@sales_router.message(UserStates.sales_menu, F.text == "Kontaktlarni olish")
async def get_contacts_message(message: types.Message):
    contacts = await get_contacts()
    contacts_text = "\n".join([f"{i['name']}: {i['phone_number']}" for i in contacts])
    await message.answer(f"Savdo bo‘limining kontaktlari:\n{contacts_text}")


@sales_router.message(UserStates.sales_menu, F.text == "Telegramda yozish")
async def go_to_telegram(message: types.Message):
    contacts = await get_contacts(contact_type="username")
    contacts_text = "\n".join([f"{i['name']}: {i['username']}" for i in contacts])
    await message.answer(f"Savdo bo‘limi Telegramda:\n{contacts_text}")


@sales_router.message(UserStates.sales_menu, F.text == "Shikoyat qoldirish")
async def send_complaint(message: types.Message, state: FSMContext):
    await message.answer("Shikoyatingizni yozing:")
    await state.set_state(UserStates.sales_complaint)


@sales_router.message(UserStates.sales_complaint)
async def process_complaint(message: types.Message, state: FSMContext):
    await message.answer("Shikoyatingiz uchun rahmat!")

    user = await get_user_by_id(message.from_user.id)
    await add_complaint(user.user_id, message.text)
    admin_chat_id = await admin_id(message.from_user.id, "sales_department")
    print(user.full_name, user.username)
    await message.bot.send_message(admin_chat_id, f"Shikoyat {user.full_name}, @{user.username} dan:\n{message.text}")
    await state.set_state(UserStates.sales_menu)
