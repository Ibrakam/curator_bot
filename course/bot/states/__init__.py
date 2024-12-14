from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    # Регистрация
    registration_phone = State()
    registration_name = State()

    # Отдел продаж
    sales_menu = State()
    sales_call_request = State()
    sales_complaint = State()
    waiting_for_call_record = State()

    # Отдел обучения
    education_menu = State()
    course_selection = State()
    course_uzum_savdo = State()
    course_smm = State()
    education_call_request = State()
    education_complaint = State()
    refund_name = State()
    refund_surname = State()
    refund_course = State()
    refund_stream = State()
    refund_request = State()
    refund_details = State()
    course_question = State()