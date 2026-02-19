from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def manage_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📄 Получить конфиг (Happ)", callback_data="cfg:get")],
        [InlineKeyboardButton(text="⛔️ Сбросить конфиг", callback_data="cfg:reset")],
        [InlineKeyboardButton(text="🔄 Продлить подписку", callback_data="buy")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu")],
    ])

def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Купить подписку", callback_data="buy")],
        [InlineKeyboardButton(text="⚙️ Управление подпиской", callback_data="manage")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")],
        [InlineKeyboardButton(text="🔗 Полезные ссылки", callback_data="links")],
    ])

def back_to_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="menu")]
    ])

def buy_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ 30 дней — 199₽", callback_data="pay:30")],
        [InlineKeyboardButton(text="✅ 90 дней — 549₽", callback_data="pay:90")],
        [InlineKeyboardButton(text="✅ 1 год — 2299₽", callback_data="pay:365")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu")],
    ])

def pay_menu(invoice_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я оплатил(а)", callback_data=f"paid:{invoice_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="menu")],
    ])

TG_CHANNEL_URL = "https://t.me/your_channel"        # <- заменить
SUPPORT_CHAT_URL = "https://t.me/your_support"      # <- заменить
SETUP_GUIDE_URL = "https://example.com/happ-setup"  # <- заменить

def links_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📣 Telegram-канал", url=TG_CHANNEL_URL)],
        [InlineKeyboardButton(text="💬 Чат поддержки", url=SUPPORT_CHAT_URL)],
        [InlineKeyboardButton(text="📌 Инструкция (Happ)", url=SETUP_GUIDE_URL)],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu")],
    ])

def pay_actions(payment_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить", url=payment_url)],
        [InlineKeyboardButton(text="🔎 Проверить оплату", callback_data="pay:check")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu")],
    ])

