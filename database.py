"""
Async SQLite (via aiosqlite / SQLAlchemy 2) database layer.
All tables are created on first run.
"""
from __future__ import annotations

import time

from sqlalchemy import BigInteger, Boolean, Column, Integer, String, Text, select, func, delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

import config

# ── Engine & session factory ──────────────────────────────────────────────────
engine = create_async_engine(config.DATABASE_URL, echo=False, future=True)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


# ── ORM models ────────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id   = Column(BigInteger, primary_key=True, index=True)
    username  = Column(String(64),  nullable=True)
    full_name = Column(String(128), nullable=True)
    verified  = Column(Boolean, default=False)
    joined_at = Column(Integer, default=lambda: int(time.time()))
    last_seen = Column(Integer, default=lambda: int(time.time()))
    blocked   = Column(Boolean, default=False)


class ForceChannel(Base):
    __tablename__ = "force_channels"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    channel_id   = Column(String(64), unique=True, nullable=False)   # e.g. -1001234567890
    channel_link = Column(String(256), nullable=False)               # e.g. https://t.me/channelname
    channel_name = Column(String(128), nullable=False)


class BroadcastLog(Base):
    __tablename__ = "broadcast_logs"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    admin_id   = Column(BigInteger, nullable=False)
    message    = Column(Text, nullable=True)
    sent_count = Column(Integer, default=0)
    fail_count = Column(Integer, default=0)
    timestamp  = Column(Integer, default=lambda: int(time.time()))


# ── Init ──────────────────────────────────────────────────────────────────────
async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ── User helpers ──────────────────────────────────────────────────────────────
async def get_or_create_user(user_id: int, username: str | None, full_name: str) -> User:
    async with async_session_factory() as session:
        user = await session.get(User, user_id)
        if user is None:
            user = User(user_id=user_id, username=username, full_name=full_name)
            session.add(user)
        else:
            user.username  = username
            user.full_name = full_name
            user.last_seen = int(time.time())
        await session.commit()
        return user


async def set_user_verified(user_id: int, verified: bool) -> None:
    async with async_session_factory() as session:
        user = await session.get(User, user_id)
        if user:
            user.verified  = verified
            user.last_seen = int(time.time())
            await session.commit()


async def is_user_verified(user_id: int) -> bool:
    async with async_session_factory() as session:
        user = await session.get(User, user_id)
        return bool(user and user.verified)


async def get_all_verified_users() -> list[int]:
    async with async_session_factory() as session:
        result = await session.execute(
            select(User.user_id).where(User.verified == True, User.blocked == False)
        )
        return [row[0] for row in result.fetchall()]


async def get_user_count() -> dict:
    async with async_session_factory() as session:
        total = (await session.execute(
            select(func.count()).select_from(User)
        )).scalar()
        verified = (await session.execute(
            select(func.count()).select_from(User).where(User.verified == True)
        )).scalar()
        return {"total": total or 0, "verified": verified or 0}


async def block_user(user_id: int) -> None:
    async with async_session_factory() as session:
        user = await session.get(User, user_id)
        if user:
            user.blocked = True
            await session.commit()


# ── Force-channel helpers ─────────────────────────────────────────────────────
async def get_force_channels() -> list[ForceChannel]:
    async with async_session_factory() as session:
        result = await session.execute(select(ForceChannel))
        return list(result.scalars().all())


async def add_force_channel(channel_id: str, channel_link: str, channel_name: str) -> bool:
    """Returns True on success, False if already exists."""
    # FIX: was using __import__("sqlalchemy").select(...) hack — replaced with clean import at top
    async with async_session_factory() as session:
        existing = await session.execute(
            select(ForceChannel).where(ForceChannel.channel_id == channel_id)
        )
        if existing.scalar():
            return False
        session.add(ForceChannel(
            channel_id=channel_id,
            channel_link=channel_link,
            channel_name=channel_name,
        ))
        await session.commit()
        return True


async def remove_force_channel(channel_id: str) -> bool:
    async with async_session_factory() as session:
        result = await session.execute(
            select(ForceChannel).where(ForceChannel.channel_id == channel_id)
        )
        ch = result.scalar()
        if not ch:
            return False
        await session.execute(delete(ForceChannel).where(ForceChannel.channel_id == channel_id))
        await session.commit()
        return True


# ── Broadcast log helpers ─────────────────────────────────────────────────────
async def log_broadcast(admin_id: int, message: str, sent: int, failed: int) -> None:
    async with async_session_factory() as session:
        session.add(BroadcastLog(
            admin_id=admin_id,
            message=message[:500],
            sent_count=sent,
            fail_count=failed,
        ))
        await session.commit()
