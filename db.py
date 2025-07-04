import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, func, select

# --- DATABASE CONNECTION SETUP ---
DATABASE_URL = "sqlite+aiosqlite:///bot.db"  # local file database

engine = create_async_engine(
    DATABASE_URL,  # SQLAlchemy connection string
    echo=False     # disable SQL query logging (set True for debug)
)
Base = declarative_base()  # base class for ORM models
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# --- TABLE: request_details ---
class RequestDetail(Base):
    """
    Logs every request input made by a user.
    """
    __tablename__ = "request_details"

    request_id = Column(Integer, primary_key=True, autoincrement=True)  # unique id for each request
    user_id = Column(Integer, nullable=False)                           # Telegram user id
    request_amount = Column(Float, nullable=False)                      # sum of input numbers
    amount_of_numbers = Column(Integer, nullable=False)                 # count of numbers entered
    raw_entry = Column(String, nullable=False)                          # raw user text
    first_name = Column(String)                                         # Telegram first name
    last_name = Column(String)                                          # Telegram last name
    date = Column(DateTime(timezone=False), nullable=False)             # UTC+3 timestamp as DATETIME

# --- TABLE: user_summary ---
class UserSummary(Base):
    """
    Tracks summary info about each unique user.
    """
    __tablename__ = "user_summary"

    summary_id = Column(Integer, primary_key=True, autoincrement=True)  # unique summary id
    user_id = Column(Integer, nullable=False, unique=True)              # Telegram user id (1 row per user)
    total_requests = Column(Integer, default=0)                         # total requests made by user
    first_name = Column(String)                                         # Telegram first name
    last_name = Column(String)                                          # Telegram last name
    first_request = Column(DateTime(timezone=False))                    # datetime of first request
    last_request = Column(DateTime(timezone=False))                     # datetime of latest request

# --- DATABASE INITIALIZATION ---
async def init_db():
    """
    Creates all tables if they don't exist. Called once on bot startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

from datetime import datetime, timedelta

async def log_request(user_id: int, first_name: str, last_name: str, raw_entry: str, index_array: list[float]):
    """
    Logs a single user request and updates the summary table.
    """
    async with async_session() as session:
        # 1) calculate sum of input numbers and number of entries
        request_amount = sum(index_array)
        amount_of_numbers = len(index_array)

        # 2) get current time in UTC+3 as a Python datetime object
        now_utc3 = datetime.utcnow() + timedelta(hours=3)

        # 3) create a new RequestDetail row
        request = RequestDetail(
            user_id=user_id,
            request_amount=request_amount,
            amount_of_numbers=amount_of_numbers,
            raw_entry=raw_entry,
            first_name=first_name,
            last_name=last_name,
            date=now_utc3,
        )
        session.add(request)  # add to transaction

        # 4) check if user_summary already exists
        result = await session.execute(
            select(UserSummary).where(UserSummary.user_id == user_id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            # 5) update existing summary entry
            existing.total_requests += 1
            existing.first_name = first_name
            existing.last_name = last_name
            existing.last_request = now_utc3
        else:
            # 6) create a new summary entry
            summary = UserSummary(
                user_id=user_id,
                total_requests=1,
                first_name=first_name,
                last_name=last_name,
                first_request=now_utc3,
                last_request=now_utc3,
            )
            session.add(summary)

        await session.commit()  # commit both request and summary updates