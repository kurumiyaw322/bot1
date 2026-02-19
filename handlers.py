from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime
from keyboards import manage_menu  # +++
from db import ensure_user, is_active, reset_config  # +++
from aiogram.filters import Command
from db import set_config, deactivate

from payments import init_yookassa, create_payment, find_payment
from db import Session, set_pending_payment, clear_pending_payment, extend_sub, get_user

from keyboards import pay_actions


from config import config
from keyboards import (
    main_menu,
    buy_menu,
    back_to_menu,
    links_menu,
)
from states import BuyFlow

router = Router()


# -------------------------
# START / MENU
# -------------------------
@router.message(F.text.in_({"/start", "/menu"}))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Добро пожаловать в HytaoVPN — быстрый и стабильный сервис!\n\n"
        "Выберите тариф и оформите подписку в пару кликов.\n\n"
        "Как начать пользоваться:\n\n"
        "1 Нажмите «Оплатить VPN»\n\n"
        "2 Выберите тариф\n\n"
        "3 Оплатите любым удобным способом\n\n"
        "4 Перейдите в «Профиль»\n\n"
        "5 Подключайтесь и пользуйтесь безопасным интернетом\n\n"
        "Выберите действие:\n\n",
        reply_markup=main_menu()
    )


@router.callback_query(F.data == "menu")
async def cb_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text(
        "Добро пожаловать в HytaoVPN — быстрый и стабильный сервис!\n\n"
        "Выберите тариф и оформите подписку в пару кликов.\n\n"
        "Как начать пользоваться:\n\n"
        "1 Нажмите «Оплатить VPN»\n\n"
        "2 Выберите тариф\n\n"
        "3 Оплатите любым удобным способом\n\n"
        "4 Перейдите в «Профиль»\n\n"
        "5 Подключайтесь и пользуйтесь безопасным интернетом\n\n"
        "Выберите действие:\n\n",
        reply_markup=main_menu()
    )
    await cb.answer()


# -------------------------
# BUY
# -------------------------
@router.callback_query(F.data == "buy")
async def cb_buy(cb: CallbackQuery):
    await cb.message.edit_text(
        "🛒 Купить подписку\n\nВыберите тариф:",
        reply_markup=buy_menu()
    )
    await cb.answer()



@router.callback_query(BuyFlow.choosing_tariff, F.data.startswith("buy:"))
async def cb_buy_tariff(cb: CallbackQuery, state: FSMContext):
    tariff = cb.data.split(":", 1)[1]

    # Пока без оплаты — просто заглушка
    await state.set_state(BuyFlow.awaiting_payment)
    await state.update_data(tariff=tariff)

    await cb.message.edit_text(
        "🧾 Тариф выбран.\n\n"
        f"Тариф: {tariff}\n\n"
        "Дальше подключим оплату (СБП/карты).\n"
        "Пока это заглушка.",
        reply_markup=back_to_menu()
    )
    await cb.answer()


# -------------------------
# MANAGE
# -------------------------
@router.callback_query(F.data == "manage")
async def cb_manage(cb: CallbackQuery):
    async with Session() as session:
        u = await ensure_user(session, cb.from_user.id)

    active = is_active(u)
    expires_text = u.expires_at.strftime("%Y-%m-%d %H:%M UTC") if active else "нет активной"

    cfg_status = "есть" if (u.config_link and u.config_link.strip()) else "не выдан"

    text = (
        "⚙️ Управление подпиской\n\n"
        f"Статус: {'✅ активна' if active else '⛔️ не активна'}\n"
        f"Срок до: {expires_text}\n"
        f"Конфиг: {cfg_status}\n\n"
        "Выберите действие:"
    )

    await cb.message.edit_text(text, reply_markup=manage_menu())
    await cb.answer()



@router.callback_query(F.data == "cfg:get")
async def cb_cfg_get(cb: CallbackQuery):
    async with Session() as session:
        u = await get_user(session, cb.from_user.id)

    if not u or not u.config_link.strip():
        await cb.message.edit_text(
            "📄 Конфиг ещё не выдан.\n\n"
            "Напишите в поддержку для получения доступа.",
            reply_markup=back_to_menu()
        )
        await cb.answer()
        return

    if not is_active(u):
        await cb.message.edit_text(
            "⛔️ Подписка не активна.\n\n"
            "Продлите подписку, затем конфиг будет доступен.",
            reply_markup=back_to_menu()
        )
        await cb.answer()
        return

    await cb.message.edit_text(
        "📄 Ваш конфиг для Happ (скопируйте строку и импортируйте в Happ):\n\n"
        f"`{u.config_link.strip()}`",
        parse_mode="Markdown",
        reply_markup=back_to_menu()
    )
    await cb.answer()


@router.callback_query(F.data == "cfg:reset")
async def cb_cfg_reset(cb: CallbackQuery):
    async with Session() as session:
        await reset_config(session, cb.from_user.id)

    await cb.message.edit_text(
        "⛔️ Конфиг сброшен.\n\n"
        "Напишите в поддержку, чтобы вам выдали новый конфиг для Happ.",
        reply_markup=back_to_menu()
    )
    await cb.answer()



# -------------------------
# PROFILE
# -------------------------
@router.callback_query(F.data == "profile")
async def cb_profile(cb: CallbackQuery):
    u = cb.from_user

    await cb.message.edit_text(
        "👤 Профиль\n\n"
        f"ID: {u.id}\n"
        f"Username: @{u.username or '—'}\n\n"
        "Подписка: (позже подключим БД)\n",
        reply_markup=back_to_menu()
    )
    await cb.answer()


# -------------------------
# HELP
# -------------------------
@router.callback_query(F.data == "help")
async def cb_help(cb: CallbackQuery):
    await cb.message.edit_text(
        "❓ Помощь\n\n"
        "Если не получается подключиться:\n"
        "1) Проверьте интернет\n"
        "2) Обновите Happ\n"
        "3) Проверьте что конфиг вставлен полностью\n\n"
        f"Поддержка: {config.support}",
        reply_markup=back_to_menu()
    )
    await cb.answer()


# -------------------------
# LINKS
# -------------------------
@router.callback_query(F.data == "links")
async def cb_links(cb: CallbackQuery):
    await cb.message.edit_text(
        "🔗 Полезные ссылки:",
        reply_markup=links_menu()
    )
    await cb.answer()


# -------------------------
# dev
# -------------------------

def is_admin(user_id: int) -> bool:
    return user_id in config.admin_ids

@router.message(Command("setcfg"))
async def admin_setcfg(message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("Формат: /setcfg <user_id> <config_link>")
        return

    if not parts[1].isdigit():
        await message.answer("user_id должен быть числом. Формат: /setcfg <user_id> <config_link>")
        return

    user_id = int(parts[1])
    cfg = parts[2].strip()

    async with Session() as session:
        await set_config(session, user_id, cfg)

    await message.answer(f"✅ Конфиг сохранён для user_id={user_id}")


@router.message(Command("extend"))
async def admin_extend(message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()
    if len(parts) != 3 or (not parts[1].isdigit()) or (not parts[2].isdigit()):
        await message.answer("Формат: /extend <user_id> <days>")
        return

    user_id = int(parts[1])
    days = int(parts[2])

    async with Session() as session:
        expires = await extend_sub(session, user_id, days)

    await message.answer(
        f"✅ Подписка продлена для user_id={user_id}\n"
        f"Новый срок до: {expires.strftime('%Y-%m-%d %H:%M UTC')}"
    )


@router.message(Command("deactivate"))
async def admin_deactivate(message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Формат: /deactivate <user_id>")
        return

    user_id = int(parts[1])

    async with Session() as session:
        await deactivate(session, user_id)

    await message.answer(f"✅ Подписка отключена для user_id={user_id}")


# -------------------------
# платежи
# -------------------------

@router.callback_query(F.data.in_({"pay:30", "pay:90", "pay:365"}))
async def cb_pay_create(cb: CallbackQuery):
    code = cb.data.split(":", 1)[1]

    if code == "30":
        days, amount, title = 30, "1.00", "30 дней"
    elif code == "90":
        days, amount, title = 90, "1.00", "90 дней"
    else:  # 365
        days, amount, title = 365, "1.00", "1 год"

    payment = await create_payment(
        amount_rub=amount,
        description=f"VPN подписка на {title}",
        return_url=config.yookassa_return_url,
        user_id=cb.from_user.id
    )

    payment_id = payment.id
    payment_url = payment.confirmation.confirmation_url

    async with Session() as session:
        await set_pending_payment(session, cb.from_user.id, payment_id, days, amount)

    await cb.message.edit_text(
        "💳 Платёж создан.\n\n"
        "1) Нажмите «Оплатить»\n"
        "2) После оплаты вернитесь и нажмите «Проверить оплату»",
        reply_markup=pay_actions(payment_url)
    )
    await cb.answer()



@router.callback_query(F.data == "pay:check")
async def cb_pay_check(cb: CallbackQuery):
    async with Session() as session:
        u = await get_user(session, cb.from_user.id)

        if not u or not u.pending_payment_id:
            await cb.message.edit_text(
                "🔎 Нет платежа для проверки.\n\nСоздайте оплату через «Купить подписку».",
                reply_markup=back_to_menu()
            )
            await cb.answer()
            return

        payment = await find_payment(u.pending_payment_id)
        status = getattr(payment, "status", "")

        if status == "succeeded":
            days = u.pending_days
            await extend_sub(session, cb.from_user.id, days)
            await clear_pending_payment(session, cb.from_user.id)

            await cb.message.edit_text(
                f"✅ Оплата подтверждена!\nПодписка продлена на {days} дней.",
                reply_markup=back_to_menu()
            )
            await cb.answer()
            return

        if status == "pending":
            await cb.message.edit_text(
                "⏳ Платёж ещё обрабатывается.\n\n"
                "Подождите 10–30 секунд и нажмите «Проверить оплату» снова.",
                reply_markup=back_to_menu()
            )
            await cb.answer()
            return

        if status == "canceled":
            await clear_pending_payment(session, cb.from_user.id)
            await cb.message.edit_text(
                "❌ Платёж отменён.\n\nСоздайте оплату заново через «Купить подписку».",
                reply_markup=back_to_menu()
            )
            await cb.answer()
            return

        await cb.message.edit_text(
            f"🔎 Статус платежа: {status}\n\nПроверьте позже.",
            reply_markup=back_to_menu()
        )
        await cb.answer()

