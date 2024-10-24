from datetime import datetime
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from lecture_4.demo_service.api.main import create_app
from lecture_4.demo_service.core.users import UserService, UserInfo, UserRole, password_is_longer_than_8

app = create_app()


@pytest.fixture
def client():
    """Фикстура для создания клиента FastAPI и инициализации UserService."""
    with TestClient(app) as client:
        user_service = UserService(password_validators=[password_is_longer_than_8])
        app.state.user_service = user_service
        yield client


@pytest.fixture
def user_service():
    """Фикстура для доступа к UserService."""
    return app.state.user_service


@pytest.fixture
def admin_user(user_service):
    """Фикстура для создания администратора."""
    admin_info = UserInfo(
        username="admin",
        name="Admin User",
        birthdate=datetime(2000, 1, 1),
        role=UserRole.ADMIN,
        password="AdminPassword123"
    )
    user_service.register(admin_info)
    return admin_info


@pytest.fixture
def test_user(user_service):
    """Фикстура для создания тестового пользователя."""
    user_info = UserInfo(
        username="testuser",
        name="Test User",
        birthdate=datetime(2000, 1, 1),
        role=UserRole.USER,
        password="ValidPassword123"
    )
    return user_service.register(user_info)


def test_user_registration(client):
    """Тест регистрации нового пользователя и проверки на существующего."""

    # Тест регистрации нового пользователя
    response = client.post("/user-register", json={
        "username": "testuser",
        "name": "Test User",
        "birthdate": "2000-01-01T00:00:00",
        "password": "ValidPassword123"
    })
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

    # Тест регистрации уже существующего пользователя
    response = client.post("/user-register", json={
        "username": "testuser",
        "name": "Another Test User",
        "birthdate": "2000-01-01T00:00:00",
        "password": "AnotherValidPassword123"
    })
    assert response.status_code == 400


def test_user_retrieval(client, test_user, admin_user):
    """Тесты получения пользователя по id, username и проверка ошибок."""

    # Получение пользователя по id
    response = client.post("/user-get", params={"id": test_user.uid}, auth=("testuser", "ValidPassword123"))
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

    # Получение пользователя по username
    response = client.post("/user-get", params={"username": "testuser"}, auth=("testuser", "ValidPassword123"))
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

    # Ошибка: пользователь не найден
    response = client.post("/user-get", params={"username": "nonexistentuser"}, auth=("admin", "AdminPassword123"))
    assert response.status_code == HTTPStatus.NOT_FOUND

    # Ошибка: переданы оба параметра id и username
    response = client.post("/user-get", params={"id": 1, "username": "testuser"}, auth=("admin", "AdminPassword123"))
    assert response.status_code == 400
    assert response.json()["detail"] == "both id and username are provided"

    # Ошибка: не переданы ни id, ни username
    response = client.post("/user-get", auth=("admin", "AdminPassword123"))
    assert response.status_code == 400
    assert response.json()["detail"] == "neither id nor username are provided"


def test_user_promotion(client, admin_user, test_user):
    """Тесты повышения пользователя до администратора и проверка ошибок."""

    # Повышение пользователя до администратора
    response = client.post(f"/user-promote?id={test_user.uid}", auth=("admin", "AdminPassword123"))
    assert response.status_code == 200

    # Ошибка: несуществующий пользователь
    response = client.post("/user-promote?id=999", auth=("admin", "AdminPassword123"))
    assert response.status_code == 400


def test_user_service_password_validation(user_service):
    """Тесты для валидации паролей и поиска пользователей."""

    # Регистрация с недопустимым паролем
    user_info = UserInfo(
        username="weakpassworduser",
        name="Weak Password User",
        birthdate=datetime(2000, 1, 1),
        role=UserRole.USER,
        password="weak"
    )
    with pytest.raises(ValueError, match="invalid password"):
        user_service.register(user_info)

    # Пользователь не найден по username
    user_entity = user_service.get_by_username("nonexistentuser")
    assert user_entity is None
