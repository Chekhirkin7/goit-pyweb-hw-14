import unittest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.entity.models import Base, Contact
from src.schemas.app_hw import ContactSchema
from src.repository.app_hw import (
    get_contacts, get_contact_by_id, get_contact_by_firstname,
    get_contact_by_lastname, add_contact, update_contact, delete_contact, add_avatar_url
)

# Створюємо in-memory SQLite базу для тестування
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TestContactRepository(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Ініціалізація бази даних перед тестами."""
        Base.metadata.create_all(bind=engine)
        cls.session = TestingSessionLocal()

    @classmethod
    def tearDownClass(cls):
        """Закриття сесії та видалення бази після тестів."""
        cls.session.close()
        Base.metadata.drop_all(bind=engine)

    def setUp(self):
        """Очистка перед кожним тестом."""
        self.session.query(Contact).delete()
        self.session.commit()

        self.sample_contact = ContactSchema(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="+123456789",
            date_of_birth=date(1990, 5, 17),
            description="Test contact"
        )

    def test_add_contact(self):
        contact = add_contact(self.sample_contact, self.session, user_id=1)
        self.assertIsNotNone(contact.id)
        self.assertEqual(contact.first_name, "John")

    def test_get_contacts(self):
        add_contact(self.sample_contact, self.session, user_id=1)
        contacts = get_contacts(limit=10, offset=0, db=self.session, user_id=1)
        self.assertEqual(len(contacts), 1)

    def test_get_contact_by_id(self):
        contact = add_contact(self.sample_contact, self.session, user_id=1)
        found = get_contact_by_id(contact.id, self.session, user_id=1)
        self.assertIsNotNone(found)
        self.assertEqual(found.first_name, "John")

    def test_get_contact_by_firstname(self):
        add_contact(self.sample_contact, self.session, user_id=1)
        contacts = get_contact_by_firstname("John", self.session, user_id=1)
        self.assertEqual(len(contacts), 1)

    def test_get_contact_by_lastname(self):
        add_contact(self.sample_contact, self.session, user_id=1)
        contacts = get_contact_by_lastname("Doe", self.session, user_id=1)
        self.assertEqual(len(contacts), 1)

    def test_update_contact(self):
        contact = add_contact(self.sample_contact, self.session, user_id=1)
        updated_data = ContactSchema(
            first_name="Jane",
            last_name="Doe",
            email="jane.doe@example.com",
            phone_number="+987654321",
            date_of_birth=date(1992, 6, 10),
            description="Updated contact"
        )
        updated_contact = update_contact(contact.id, updated_data, self.session, user_id=1)
        self.assertEqual(updated_contact.first_name, "Jane")
        self.assertEqual(updated_contact.email, "jane.doe@example.com")

    def test_delete_contact(self):
        contact = add_contact(self.sample_contact, self.session, user_id=1)
        deleted_contact = delete_contact(contact.id, self.session, user_id=1)
        self.assertIsNotNone(deleted_contact)
        self.assertIsNone(get_contact_by_id(contact.id, self.session, user_id=1))

    def test_add_avatar_url(self):
        contact = add_contact(self.sample_contact, self.session, user_id=1)
        updated_contact = add_avatar_url(contact.id, "https://avatar.com/john.jpg", self.session)
        self.assertEqual(updated_contact.avatar, "https://avatar.com/john.jpg")


if __name__ == "__main__":
    unittest.main()
