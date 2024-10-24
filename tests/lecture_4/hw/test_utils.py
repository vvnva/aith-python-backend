import pytest
from datetime import datetime
from fastapi import HTTPException
from lecture_4.demo_service.api.utils import (
    password_is_longer_than_8,
    requires_author,
    requires_admin
)
from lecture_4.demo_service.core.users import UserRole, UserEntity, UserInfo


@pytest.fixture
def mock_user_service(mocker):
    return mocker.Mock()


@pytest.fixture
def mock_valid_credentials(mocker):
    credentials = mocker.Mock()
    credentials.username = "testuser"
    credentials.password = "superSecret"
    return credentials


@pytest.fixture
def mock_invalid_credentials(mocker):
    credentials = mocker.Mock()
    credentials.username = "wronguser"
    credentials.password = "wrongPassword"
    return credentials


@pytest.fixture
def valid_user_entity():
    return UserEntity(
        uid=1,
        info=UserInfo(
            username="testuser",
            name="Test User",
            birthdate=datetime(2000, 1, 1),
            role=UserRole.USER,
            password="superSecret"
        )
    )


@pytest.fixture
def admin_user_entity():
    return UserEntity(
        uid=1,
        info=UserInfo(
            username="admin",
            name="Admin User",
            birthdate=datetime(2000, 1, 1),
            role=UserRole.ADMIN,
            password="AdminPassword123"
        )
    )


@pytest.fixture
def regular_user_entity():
    return UserEntity(
        uid=2,
        info=UserInfo(
            username="testuser",
            name="Test User",
            birthdate=datetime(2000, 1, 1),
            role=UserRole.USER,
            password="ValidPassword123"
        )
    )


def test_password_is_longer_than_8_valid():
    """Тест, что функция возвращает True для пароля длиной больше 8 символов"""
    assert password_is_longer_than_8("validPassword123") is True


def test_password_is_longer_than_8_invalid():
    """Тест, что функция возвращает False для пароля длиной меньше 8 символов"""
    assert password_is_longer_than_8("short") is False


def test_requires_author_success(mock_user_service, mock_valid_credentials, valid_user_entity):
    """Тест успешной аутентификации пользователя через requires_author"""
    mock_user_service.get_by_username.return_value = valid_user_entity

    user_entity = requires_author(mock_valid_credentials, mock_user_service)
    assert user_entity.uid == 1


def test_requires_author_unauthorized(mock_user_service, mock_invalid_credentials):
    """Тест, что вызывается исключение HTTPException при неудачной аутентификации"""
    mock_user_service.get_by_username.return_value = None

    with pytest.raises(HTTPException):
        requires_author(mock_invalid_credentials, mock_user_service)


def test_requires_admin_success(admin_user_entity):
    """Тест успешной проверки прав администратора через requires_admin"""
    result = requires_admin(admin_user_entity)
    assert result == admin_user_entity


def test_requires_admin_forbidden(regular_user_entity):
    """Тест, что вызывается исключение HTTPException при отсутствии прав администратора"""
    with pytest.raises(HTTPException) as exc_info:
        requires_admin(regular_user_entity)

    assert exc_info.value.status_code == 403
