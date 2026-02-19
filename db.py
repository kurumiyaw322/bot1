from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import Integer, String, DateTime, select
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

Base = declarative_base()


def utcnow() -> datetime:
    """
    ВАЖНО:
    SQLite чаще всего хранит datetime как naive.
    Поэтому мы везде используем naive UTC (datetime.utcnow()).
    """
    return datetime.utcnow()


class UserSub(Base):

    pending_payment_id: Mapped[str] = mapped_column(String, default="")
    pending_days: Mapped[int] = mapped_column(Integer, default=0)
    pending_amount: Mapped[str] = mapped_column(String, default="")  # "10.00"

    __tablename__ = "user_subs"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    config_link: Mapped[str] = mapped_column(String, default="")

    # naive datetime (UTC)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(),
        default=lambda: datetime(1970, 1, 1)
    )


engine = create_async_engine("sqlite+aiosqlite:///bot.db")
Session = async_sessionmaker(engine, expire_on_commit=False)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_user(session: AsyncSession, user_id: int) -> Optional[UserSub]:
    res = await session.execute(select(UserSub).where(UserSub.user_id == user_id))
    return res.scalar_one_or_none()

async def get_user_by_pending_payment(session: AsyncSession, payment_id: str) -> Optional[UserSub]:
    res = await session.execute(
        select(UserSub).where(UserSub.pending_payment_id == payment_id)
    )
    return res.scalar_one_or_none()


async def ensure_user(session: AsyncSession, user_id: int) -> UserSub:
    u = await get_user(session, user_id)
    if u is None:
        u = UserSub(user_id=user_id)
        session.add(u)
        await session.commit()
    return u


def is_active(u: UserSub) -> bool:
    return u.expires_at > utcnow()


async def set_config(session: AsyncSession, user_id: int, config_link: str) -> None:
    u = await ensure_user(session, user_id)
    u.config_link = config_link.strip()
    await session.commit()


async def reset_config(session: AsyncSession, user_id: int) -> None:
    """
    Для MVP сброс = удалить конфиг.
    Новый выдаётся вручную через поддержку/админа.
    """
    u = await ensure_user(session, user_id)
    u.config_link = ""
    await session.commit()


async def extend_sub(session: AsyncSession, user_id: int, days: int) -> datetime:
    u = await ensure_user(session, user_id)

    now = utcnow()
    base = u.expires_at if u.expires_at > now else now
    u.expires_at = base + timedelta(days=days)

    await session.commit()
    return u.expires_at


async def deactivate(session: AsyncSession, user_id: int) -> None:
    u = await ensure_user(session, user_id)
    u.expires_at = datetime(1970, 1, 1)
    await session.commit()


async def set_pending_payment(session: AsyncSession, user_id: int, payment_id: str, days: int, amount: str) -> None:
    u = await ensure_user(session, user_id)
    u.pending_payment_id = payment_id
    u.pending_days = days
    u.pending_amount = amount
    await session.commit()

async def clear_pending_payment(session: AsyncSession, user_id: int) -> None:
    u = await ensure_user(session, user_id)
    u.pending_payment_id = ""
    u.pending_days = 0
    u.pending_amount = ""
    await session.commit()
