import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from src.database.db import get_db
from src.entity.models import Base, User
from src.repository.users import get_user_by_email
from src.services.auth import auth_service

# 🎯 Створюємо in-memory SQLite базу для тестування
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 🔄 Перевизначаємо БД для FastAPI
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    """Фікстура для клієнта API"""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(client):
    """Фікстура для тестового користувача"""
    db = TestingSessionLocal()
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": auth_service.get_password_hash("testpass")
    }
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

# 🛠 Тест: Реєстрація нового користувача
def test_signup(client):
    response = client.post("api/auth/signup", json={
        "username": "newuser",
        "email": "new@example.com",
        "password": "newpass"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "new@example.com"

# 🛠 Тест: Логін користувача
def test_login(client, test_user):
    response = client.post("api/auth/login", data={
        "username": "test@example.com",  # Тут передається email замість username, бо FastAPI використовує OAuth2PasswordRequestForm
        "password": "testpass"
    })
    assert response.status_code == 200
    json_response = response.json()
    assert "access_token" in json_response
    assert "refresh_token" in json_response

# 🛠 Тест: Отримання поточного користувача
def test_get_current_user(client, test_user):
    access_token = auth_service.create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("api/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == test_user.email

# 🛠 Тест: Оновлення токена
def test_refresh_token(client, test_user):
    refresh_token = auth_service.create_refresh_token(data={"sub": test_user.email})
    test_user.refresh_token = refresh_token
    db = TestingSessionLocal()
    db.add(test_user)
    db.commit()
    db.close()

    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = client.get("api/auth/refresh_token", headers=headers)
    assert response.status_code == 200
    json_response = response.json()
    assert "access_token" in json_response
    assert "refresh_token" in json_response

# 🛠 Тест: Підтвердження email
def test_confirmed_email(client, test_user):
    confirmation_token = auth_service.create_access_token(data={"sub": test_user.email})
    response = client.get(f"api/auth/confirmed_email/{confirmation_token}")
    assert response.status_code == 200
    assert response.json()["message"] in ["Email confirmed", "Your email is already confirmed"]

# 🛠 Тест: Запит на повторне підтвердження email
def test_request_email(client, test_user):
    response = client.post("api/auth/request_email", json={"email": test_user.email})
    assert response.status_code == 200
    assert response.json()["message"] in ["Check your email for confirmation.", "Your email is already confirmed"]
