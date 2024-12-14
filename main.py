import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import django


# Определяем путь к проекту
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(project_path)

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teh_course.settings')

# Настраиваем Django
django.setup()

from course.bot.main_users import main_router
from course.bot.sales import sales_router
from course.bot.refund import refund_router
from course.bot.curator import education_router


# Конфигурация
TOKEN = '5605372341:AAHFL3_VEzjxLBSXbxYIuuIJLc-OSMP-1qA'


async def main():
    bot = Bot(token=TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрация роутеров
    dp.include_router(main_router)
    dp.include_router(sales_router)
    dp.include_router(education_router)
    dp.include_router(refund_router)

    # Запуск бота
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
