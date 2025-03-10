import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.entity.models import Base, User
from src.schemas.user import UserSchema
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email
)

# 🎯 Створюємо in-memory SQLite базу для тестування
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TestUserRepository(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Налаштування бази даних перед запуском тестів."""
        Base.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls):
        """Прибирання після завершення всіх тестів."""
        Base.metadata.drop_all(bind=engine)

    def setUp(self):
        """Створення сесії для кожного тесту."""
        self.db = TestingSessionLocal()

    def tearDown(self):
        """Закриття сесії після кожного тесту."""
        self.db.close()

    def get_sample_user(self):
        """Приклад користувача для тестування."""
        return UserSchema(
            username="testuser",
            email="test@example.com",
            password="12345678"
        )

    def test_create_user(self):
        """Тест створення користувача."""
        sample_user = self.get_sample_user()
        user = create_user(sample_user, self.db)
        self.assertIsNotNone(user.id)
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.username, "testuser")

    def test_get_user_by_email(self):
        """Тест отримання користувача за email."""
        sample_user = self.get_sample_user()
        create_user(sample_user, self.db)
        user = get_user_by_email("test@example.com", self.db)
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test@example.com")

    def test_update_token(self):
        """Тест оновлення токена користувача."""
        sample_user = self.get_sample_user()
        user = create_user(sample_user, self.db)
        update_token(user, "new_refresh_token", self.db)
        updated_user = get_user_by_email("test@example.com", self.db)
        self.assertEqual(updated_user.refresh_token, "new_refresh_token")

    def test_confirmed_email(self):
        """Тест підтвердження email користувача."""
        sample_user = self.get_sample_user()
        create_user(sample_user, self.db)
        confirmed_email("test@example.com", self.db)
        user = get_user_by_email("test@example.com", self.db)
        self.assertTrue(user.confirmed)


if __name__ == "__main__":
    unittest.main()
