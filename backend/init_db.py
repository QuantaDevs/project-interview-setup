import os
from sqlalchemy import create_engine
from src.db.base import BaseTable


def init_db(db_url=None):
    if db_url is None:
        db_url = os.getenv("DB_URL", "sqlite:///hello.db")
    engine = create_engine(db_url)
    BaseTable.metadata.create_all(engine)
    print(f"Database initialized at: {db_url}")


if __name__ == "__main__":
    init_db()
