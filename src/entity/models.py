from datetime import date

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import String, Text, Date, DateTime, func

class Base(DeclarativeBase):
    pass

class Contact(Base):
    __tablename__ = 'contacts'
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(25), index=True)
    last_name: Mapped[str] = mapped_column(String(25), index=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True)
    date_of_birth: Mapped[Date] = mapped_column(Date)
    description: Mapped[str] = mapped_column(Text)

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
