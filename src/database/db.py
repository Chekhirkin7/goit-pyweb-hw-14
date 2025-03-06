import contextlib

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.conf.config import config

class DatabaseSessionManager:
    def __init__(self, url):
        self._engine = create_engine(url)
        self._session_maker = sessionmaker(autoflush=False, autocommit=False, bind=self._engine)

    @contextlib.contextmanager
    def session(self):
        if self._session_maker is None:
            raise Exception("Session manager is not initialized.")
        session = self._session_maker()
        try:
            print("Сесія створена")
            yield session
        except Exception as err:
            print(err)
            print("Помилка в сесії")
            session.rollback()
            raise
        finally:
            print("Сесія закрита")
            session.close()

session_manager = DatabaseSessionManager(config.DB_URL)

def get_db():
    with session_manager.session() as session:
        yield session