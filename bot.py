import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import config
from handlers import router
from db import init_db
from payments import init_yookassa


async def main():
    logging.basicConfig(level=logging.INFO)

    # 🔹 Инициализация базы данных
    await init_db()

    # 🔹 Инициализация ЮKassa
    init_yookassa(
        config.yookassa_shop_id,
        config.yookassa_secret_key
    )

    # 🔹 Запуск Telegram-бота
    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
