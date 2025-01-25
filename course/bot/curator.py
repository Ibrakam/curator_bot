import logging

from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from course.bot.states import UserStates
from db.service import add_request, download_media, update_request_status, close_request_in_database, get_contacts, \
    get_question, delete_question, save_question, save_complaint, get_answer, delete_answer
from filter import admin_id

education_router = Router()


@education_router.message(F.text == "Menga qo'ng'iroq qiling", UserStates.education_menu)
async def call_me_request(message: types.Message):
    request_id = await add_request(message.from_user.id, 'curator', 'call_request')
    await message.answer(f"Sizning No {request_id} arizangiz qabul qilindi. Tez orada siz bilan bog'lanamiz.")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Mijoz bilan bog'landik",
                callback_data=f"confirm_call_{request_id}"
            )
        ]
    ])

    admin_message = (f"Yangi ariza No{request_id}\n"
                     f"Foydalanuvchi: {message.from_user.full_name}\n"
                     f"Foydalanuvchi ID: {message.from_user.id}\n"
                     f"Ariza turi: Qayta qo'ng'iroq")

    try:
        admin_chat_id = await admin_id("support")
        await message.bot.send_message(admin_chat_id, admin_message, reply_markup=keyboard)
    except Exception as e:
        logging.error(f"Administratorga xabar yuborishda xatolik: {e}")


@education_router.callback_query(lambda c: c.data.startswith("confirm_call_"))
async def process_call_confirmation(callback: types.CallbackQuery, state: FSMContext):
    request_id = callback.data.split("_")[-1]
    await callback.message.answer(f"Iltimos, No{request_id} ariza bo'yicha suhbat yozuvini biriktiring")
    await state.set_state(UserStates.waiting_for_call_record)
    await state.update_data({"current_request_id": request_id})


@education_router.message(UserStates.waiting_for_call_record)
async def save_call_record(message: types.Message, state: FSMContext):
    if message.content_type in ['audio', 'document', 'video', 'video_note', 'voice']:
        state_data = await state.get_data()
        request_id = state_data.get('current_request_id')
        file = await download_media(message)
        await update_request_status(request_id, 'completed', file_path=file)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Ariza yopildi",
                    callback_data=f"close_request_{request_id}"
                )
            ]
        ])

        await message.answer(f"No{request_id} ariza uchun suhbat yozuvi saqlandi.", reply_markup=keyboard)
        await state.clear()
        return
    await message.answer("Iltimos, suhbat yozuvini biriktiring.")
    return


@education_router.callback_query(lambda c: c.data.startswith("close_request_"))
async def close_request(callback: types.CallbackQuery):
    request_id = callback.data.split("_")[-1]
    await close_request_in_database(int(request_id))
    await callback.message.edit_text(f"No{request_id} ariza yopildi ✅")


@education_router.message(UserStates.education_menu, F.text == "Kontaktlarni olish")
async def get_contacts_message(message: types.Message):
    contacts = await get_contacts(role='support', contact_type='all')
    contacts_text = "\n".join([f"{i['name']}: {i['phone_number']}, {i['username']}" for i in contacts])
    await message.answer(f"Qo'llab-quvvatlash kontaktlari:\n{contacts_text}")


@education_router.message(UserStates.education_menu, F.text == "Kuratorlar kontaktlari")
async def get_contacts_message(message: types.Message):
    contacts = await get_contacts(role='curator', contact_type='all')
    contacts_text = "\n".join([f"{i['name']}: {i['phone_number']}, {i['username']}" for i in contacts])
    await message.answer(f"Kuratorlar kontaktlari:\n{contacts_text}")


@education_router.message(UserStates.education_menu, F.text == "Anonim shikoyat")
async def send_complaint(message: types.Message, state: FSMContext):
    await message.answer("Shikoyatingizni yozing:")
    await state.set_state(UserStates.education_complaint)


@education_router.message(UserStates.education_complaint)
async def process_complaint(message: types.Message, state: FSMContext):
    await message.answer("Shikoyatingiz uchun rahmat!")
    user_id = message.from_user.id
    complaint = message.text
    complaint_id = await save_complaint(user_id, complaint)
    await notify_admin_about_complaint(complaint, user_id, complaint_id, message)
    await state.set_state(UserStates.education_menu)


@education_router.message(F.text.startswith("Shikoyatga javob:"))
async def admin_response_to_question(message: types.Message, state: FSMContext):
    try:
        _, _, _, answer_id, *response_parts = message.text.split()
        response_text = " ".join(response_parts)
        answer = await get_answer(int(answer_id))

        if answer:
            await message.bot.send_message(
                chat_id=answer['user_id'],
                text=f"Sizning shikoyatingizga javob:\n{response_text}"
            )
            await delete_answer(int(answer_id))
            await state.clear()
    except Exception as e:
        await message.answer(f"Javobni qayta ishlashda xatolik: {str(e)}")


async def notify_admin_about_complaint(complaint, user_id, complaint_id, message: types.Message):
    admin_chat_id = await admin_id("support")
    await message.bot.send_message(
        chat_id=admin_chat_id,
        text=f"Yangi shikoyat (ID: {complaint_id}):\n"
             f"Foydalanuvchidan (ID: {user_id}):\n"
             f"{complaint}\n\n"
             f"Javob berish uchun yuboring: Shikoyatga javob: {complaint_id} [javob matni]"
    )


@education_router.message(UserStates.education_menu, F.text == "Kurs bo'yicha savol")
async def send_question(message: types.Message, state: FSMContext):
    await message.answer("Savolingizni yozing:")
    await state.set_state(UserStates.course_question)


@education_router.message(UserStates.course_question)
async def process_course_question(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    question_text = message.text
    question_id = await save_question(user_id, question_text)
    await message.answer("Savolingiz administratorga yuborildi. Javobni kuting.")
    await notify_admin_about_question(question_id, user_id, question_text, message)
    await state.set_state(UserStates.education_menu)


@education_router.message(F.text.startswith("Javob:"))
async def admin_response_to_question(message: types.Message):
    try:
        _, question_id, *response_parts = message.text.split()
        response_text = " ".join(response_parts)
        question = await get_question(int(question_id))

        if question:
            await message.bot.send_message(
                chat_id=question['user_id'],
                text=f"Savolingizga javob:\n{response_text}"
            )
            await delete_question(int(question_id))

    except Exception as e:
        await message.answer(f"Javobni qayta ishlashda xatolik: {str(e)}")


async def notify_admin_about_question(question_id, user_id, question_text, message: types.Message):
    admin_chat_id = await admin_id("curator")
    await message.bot.send_message(
        chat_id=admin_chat_id,
        text=f"Yangi savol (ID: {question_id}):\n"
             f"Foydalanuvchidan (ID: {user_id}):\n"
             f"{question_text}\n\n"
             f"Javob berish uchun yuboring: Javob: {question_id} [javob matni]"
    )
