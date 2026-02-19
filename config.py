import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    bot_token: str = os.getenv("BOT_TOKEN")
    support: str = os.getenv("SUPPORT_USERNAME", "@support")

    tg_channel: str = os.getenv("TG_CHANNEL_URL", "")
    setup_guide: str = os.getenv("SETUP_GUIDE_URL", "")

    yookassa_shop_id: str = os.getenv("YOOKASSA_SHOP_ID", "")
    yookassa_secret_key: str = os.getenv("YOOKASSA_SECRET_KEY", "")
    yookassa_return_url: str = os.getenv("YOOKASSA_RETURN_URL", "https://t.me/")

    admin_ids_raw: str = os.getenv("ADMIN_IDS", "")
    admin_ids: set[int] = None  # будет заполнено ниже


config = Config()

if not config.bot_token:
    raise RuntimeError("BOT_TOKEN not set in .env")

config.admin_ids = set(
    int(x.strip()) for x in config.admin_ids_raw.split(",")
    if x.strip().isdigit()
)

admin_ids_raw: str = os.getenv("ADMIN_IDS", "")
admin_ids: set[int] = set(int(x.strip()) for x in admin_ids_raw.split(",") if x.strip().isdigit())
