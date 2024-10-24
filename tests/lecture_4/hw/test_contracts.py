from datetime import datetime

import pytest
from pydantic import ValidationError

from lecture_4.demo_service.api.contracts import RegisterUserRequest, UserResponse
from lecture_4.demo_service.core.users import UserEntity, UserInfo, UserRole


def test_register_user_request_valid():
    """Тест для успешного создания RegisterUserRequest."""
    data = {
        "username": "testuser",
        "name": "Test User",
        "birthdate": datetime(2000, 1, 1),
        "password": "superSecret"
    }
    request = RegisterUserRequest(**data)

    assert request.username == data["username"]
    assert request.name == data["name"]
    assert request.birthdate == data["birthdate"]


def test_register_user_request_invalid():
    """Тест на создание RegisterUserRequest с некорректными данными."""
    with pytest.raises(ValidationError):
        RegisterUserRequest(
            username="testuser",
            name="Test User",
            birthdate="invalid_date",
            password="superSecret"
        )


def test_user_response_from_user_entity():
    """Тест создания UserResponse из UserEntity."""
    user_info = UserInfo(
        username="testuser",
        name="Test User",
        birthdate=datetime(2000, 1, 1),
        role=UserRole.USER,
        password="superSecret"
    )
    user_entity = UserEntity(uid=1, info=user_info)
    user_response = UserResponse.from_user_entity(user_entity)

    # Проверка соответствия данных между UserEntity и UserResponse
    assert user_response.uid == user_entity.uid
    assert user_response.username == user_entity.info.username
    assert user_response.name == user_entity.info.name
    assert user_response.birthdate == user_entity.info.birthdate
    assert user_response.role == user_entity.info.role
