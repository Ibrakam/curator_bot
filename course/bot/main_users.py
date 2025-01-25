from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from course.bot.states import UserStates

from db.service import add_user, update_user, get_all_complaint

main_router = Router()


@main_router.message(CommandStart())
async def start_registration(message: types.Message, state: FSMContext):
    button = [[
        KeyboardButton(text="TELEFON RAQAMNI YUBORISH☎️", request_contact=True)
    ]]
    kb = ReplyKeyboardMarkup(resize_keyboard=True,
                             keyboard=button)
    user = await add_user(message.from_user.id)
    if user:
        buttons = [
            [KeyboardButton(text="Savdo bo‘limi"),
             KeyboardButton(text="Ta’lim bo‘limi")],
            [KeyboardButton(text="Shikoyat qoldirish")]
        ]
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)

        await message.answer("Bo‘limni tanlang:", reply_markup=keyboard)
        await state.clear()
    else:
        await message.answer("Salom! Avval telefon raqamingizni kiriting:", reply_markup=kb)
        await state.set_state(UserStates.registration_phone)


@main_router.message(UserStates.registration_phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.set_data({"phone": message.contact.phone_number})
    await message.answer("Endi ismingiz va familiyangizni kiriting:")
    await state.set_state(UserStates.registration_name)


@main_router.message(UserStates.registration_name)
async def process_full_name(message: types.Message, state: FSMContext):
    # Ma'lumotlarni bazaga saqlash
    data = await state.get_data()
    await update_user(message.from_user.id, phone_number=data["phone"], full_name=message.text,
                      username=message.from_user.username or '')

    # Asosiy menyu
    buttons = [
        [KeyboardButton(text="Savdo bo‘limi"),
         KeyboardButton(text="Ta’lim bo‘limi")],
        [KeyboardButton(text="Shikoyat qoldirish")]
    ]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)

    await message.answer("Bo‘limni tanlang:", reply_markup=keyboard)
    await state.clear()


# Savdo bo‘limi uchun handlerlar
@main_router.message(F.text == 'Savdo bo‘limi')
async def sales_department(message: types.Message, state: FSMContext):
    buttons = [
        [KeyboardButton(text="Menga qo‘ng‘iroq qiling"),
         KeyboardButton(text="Kontaktlarni olish")],
        [KeyboardButton(text="Telegramda yozish"),
         KeyboardButton(text="Shikoyat qoldirish")],
        [KeyboardButton(text="Orqaga")]
    ]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)

    await message.answer("Harakatni tanlang:", reply_markup=keyboard)
    await state.set_state(UserStates.sales_menu)


# Обработчики для отдела обучения

@main_router.message(F.text == 'Ta’lim bo‘limi')
async def education_department(message: types.Message, state: FSMContext):
    buttons = [
        [KeyboardButton(text="Menga qo‘ng‘iroq qiling"),
         KeyboardButton(text="Kontaktlarni olish")],
        [KeyboardButton(text='Kuratorlar kontaktlari'),
         KeyboardButton(text='Anonim shikoyat')],
        [KeyboardButton(text='Qaytish'),
         KeyboardButton(text='Kurs bo‘yicha savol')],
        [KeyboardButton(text="Orqaga")]
    ]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)

    await message.answer("Harakatni tanlang:", reply_markup=keyboard)
    await state.set_state(UserStates.education_menu)


@main_router.message(F.text == 'Orqaga', UserStates.sales_menu)
async def go_back(message: types.Message, state: FSMContext):
    buttons = [
        [KeyboardButton(text="Savdo bo‘limi"),
         KeyboardButton(text="Ta’lim bo‘limi")],
        [KeyboardButton(text="Shikoyat qoldirish")]
    ]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)

    await message.answer("Bo‘limni tanlang:", reply_markup=keyboard)
    await state.clear()


@main_router.message(F.text == 'Orqaga', UserStates.education_menu)
async def go_back_edu(message: types.Message, state: FSMContext):
    buttons = [
        [KeyboardButton(text="Savdo bo‘limi"),
         KeyboardButton(text="Ta’lim bo‘limi")],
        [KeyboardButton(text="Shikoyat qoldirish")]
    ]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)

    await message.answer("Bo‘limni tanlang:", reply_markup=keyboard)
    await state.clear()


@main_router.message(Command("get_all_complaint"))
async def get_all_complaints(message: types.Message):
    complaints = await get_all_complaint()
    text = "Barcha shikoyatlar:\n"
    for i in complaints:
        text += f"Ariza ID: {i['id']}\nShikoyat matni: {i['complaint']}\nFoydalanuvchi: {i['user_info'].phone} {i['user_info'].full_name}\n\n"
    await message.answer(text)


@main_router.message(F.text == "Shikoyat qoldirish")
async def send_complaint(message: types.Message, state: FSMContext):
    await message.answer("Shikoyatingizni yozing:")
    await state.set_state(UserStates.sales_complaint)
