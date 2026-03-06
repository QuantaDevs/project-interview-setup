from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column


class Base(object):
    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime, default=datetime.now(timezone.utc), nullable=True
    )


BaseTable = declarative_base(cls=Base)


class Greeting(BaseTable):
    """A simple table to verify SQLAlchemy + SQLite works."""
    __tablename__ = "greetings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message: Mapped[str] = mapped_column(String(255))
