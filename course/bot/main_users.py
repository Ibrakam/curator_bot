from aiogram import types, Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from course.bot.states import UserStates

from db.service import add_user, update_user

main_router = Router()


@main_router.message(CommandStart())
async def start_registration(message: types.Message, state: FSMContext):
    button = [[
        KeyboardButton(text="ОТПРАВИТЬ НОМЕР ТЕЛЕФОНА☎️", request_contact=True)
    ]]
    kb = ReplyKeyboardMarkup(resize_keyboard=True,
                             keyboard=button)
    user = await add_user(message.from_user.id)
    if user:
        buttons = [
            [KeyboardButton(text="Отдел продаж"),
             KeyboardButton(text="Отдел обучения")]
        ]
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)

        await message.answer("Выберите отдел:", reply_markup=keyboard)
        await state.clear()
    else:
        await message.answer("Привет! Для начала введите ваш номер телефона:", reply_markup=kb)
        await state.set_state(UserStates.registration_phone)


@main_router.message(UserStates.registration_phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.set_data({"phone": message.contact.phone_number})
    await message.answer("Теперь введите ваше имя и фамилию:")
    await state.set_state(UserStates.registration_name)


@main_router.message(UserStates.registration_name)
async def process_full_name(message: types.Message, state: FSMContext):
    # Сохраняем данные в базу
    data = await state.get_data()
    await update_user(message.from_user.id, phone_number=data["phone"], full_name=message.text)

    # Главное меню
    buttons = [
        [KeyboardButton(text="Отдел продаж"),
         KeyboardButton(text="Отдел обучения")]
    ]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)

    await message.answer("Выберите отдел:", reply_markup=keyboard)
    await state.clear()


# Обработчики для отдела продаж
@main_router.message(F.text == 'Отдел продаж')
async def sales_department(message: types.Message, state: FSMContext):
    buttons = [
        [KeyboardButton(text="Позвоните мне"),
         KeyboardButton(text="Получить контакты")],
        [KeyboardButton(text="Написать в Telegram"),
         KeyboardButton(text="Оставить жалобу")],
        [KeyboardButton(text="Назад")]
    ]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)

    await message.answer("Выберите действие:", reply_markup=keyboard)
    await state.set_state(UserStates.sales_menu)


# Обработчики для отдела обучения
@main_router.message(F.text == 'Отдел обучения')
async def education_department(message: types.Message, state: FSMContext):
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

    await message.answer("Выберите действие:", reply_markup=keyboard)
    await state.set_state(UserStates.education_menu)


@main_router.message(F.text == 'Назад', UserStates.sales_menu)
async def go_back(message: types.Message, state: FSMContext):
    buttons = [
        [KeyboardButton(text="Отдел продаж"),
         KeyboardButton(text="Отдел обучения")]
    ]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)

    await message.answer("Выберите отдел:", reply_markup=keyboard)
    await state.clear()


@main_router.message(F.text == 'Назад', UserStates.education_menu)
async def go_back_edu(message: types.Message, state: FSMContext):
    buttons = [
        [KeyboardButton(text="Отдел продаж"),
         KeyboardButton(text="Отдел обучения")]
    ]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)

    await message.answer("Выберите отдел:", reply_markup=keyboard)
    await state.clear()
