import uuid
import asyncio
from yookassa import Configuration, Payment


def init_yookassa(shop_id: str, secret_key: str) -> None:
    # Настройка SDK
    Configuration.configure(shop_id, secret_key)


def _create_payment_sync(amount_rub: str, description: str, return_url: str, user_id: int):
    idempotence_key = str(uuid.uuid4())
    payload = {
        "amount": {"value": amount_rub, "currency": "RUB"},
        "capture": True,
        "confirmation": {"type": "redirect", "return_url": return_url},
        "description": description[:128],
        "metadata": {"user_id": str(user_id)},
    }
    return Payment.create(payload, idempotence_key)


async def create_payment(amount_rub: str, description: str, return_url: str, user_id: int):
    return await asyncio.to_thread(_create_payment_sync, amount_rub, description, return_url, user_id)


def _find_payment_sync(payment_id: str):
    return Payment.find_one(payment_id)


async def find_payment(payment_id: str):
    return await asyncio.to_thread(_find_payment_sync, payment_id)
