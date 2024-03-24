from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Date
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = 'contacts'
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), index=True)
    last_name: Mapped[str] = mapped_column(String(50), index=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(50), index=True)
    birth_date: Mapped[str] = mapped_column(Date)
    friend_status: Mapped[bool] = mapped_column(default=False)
