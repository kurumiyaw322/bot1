# webhook_app.py
import logging
from fastapi import FastAPI, Request
from aiogram import Bot

from config import config
from db import Session, get_user_by_pending_payment, extend_sub, clear_pending_payment
from payments import init_yookassa, find_payment

app = FastAPI()
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup():
    logging.basicConfig(level=logging.INFO)
    init_yookassa(config.yookassa_shop_id, config.yookassa_secret_key)

@app.post("/yookassa/webhook")
async def yookassa_webhook(request: Request):
    payload = await request.json()

    event = payload.get("event", "")
    obj = payload.get("object", {}) or {}
    payment_id = obj.get("id", "")

    # Не интересующие события — просто OK
    if event != "payment.succeeded" or not payment_id:
        return {"ok": True}

    # Защита: перепроверяем статус в ЮKassa
    payment = await find_payment(payment_id)
    status = getattr(payment, "status", "")

    if status != "succeeded":
        return {"ok": True}

    async with Session() as session:
        u = await get_user_by_pending_payment(session, payment_id)
        if not u:
            # нет ожидающего платежа -> либо уже обработали, либо не наш клиент
            return {"ok": True}

        days = u.pending_days
        user_id = u.user_id

        await extend_sub(session, user_id, days)
        await clear_pending_payment(session, user_id)

    # Сообщаем пользователю в Telegram
    bot = Bot(token=config.bot_token)
    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"✅ Оплата подтверждена!\nПодписка продлена на {days} дней."
        )
    finally:
        await bot.session.close()

    return {"ok": True}
