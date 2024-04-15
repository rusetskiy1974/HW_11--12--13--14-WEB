from unittest import mock

import pytest
from unittest.mock import Mock, patch
from fastapi import BackgroundTasks
from sqlalchemy import select

from src.conf import messages
from src.entity.models import User
from src.services.auth import auth_service

from tests.conftest import TestingSessionLocal

user_data = {"username": "test_user", "user_email": "test_user@example.com", "password": "123456789", "confirmed": True}
background_tasks = BackgroundTasks()


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)

    response = client.post("api/auth/signup", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data['user']['username'] == user_data['username']
    assert data['user']['user_email'] == user_data['user_email']
    assert 'password' not in data['user']
    assert 'avatar' in data['user']
    assert mock_send_email.called


def test_signup_user_exist(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)

    response = client.post("api/auth/signup", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    print(data)
    assert data['detail'] == messages.ACCOUNT_EXISTS


def test_not_confirmed_login(client):
    response = client.post("api/auth/login",
                           data={"username": user_data["user_email"], "password": user_data["password"]})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data['detail'] == messages.NOT_CONFIRMED_EMAIL


@pytest.mark.asyncio
async def test_login(client):
    async with (TestingSessionLocal() as session):
        current_user = await session.execute(select(User).where(User.user_email == user_data["user_email"]))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post("api/auth/login",
                           data={"username": user_data["user_email"], "password": user_data["password"]})
    assert response.status_code == 200, response.text
    data = response.json()
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert 'token_type' in data


def test_login_wrong_email(client):
    response = client.post("api/auth/login",
                           data={"username": "user_email", "password": user_data["password"]})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data['detail'] == messages.INVALID_EMAIL


def test_login_wrong_password(client):
    response = client.post("api/auth/login",
                           data={"username": user_data["user_email"], "password": "password"})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data['detail'] == messages.INVALID_PASSWORD


@pytest.mark.asyncio
async def test_logout(client, monkeypatch):
    current_user = User(**user_data, refresh_token="test_refresh_token")
    async with (TestingSessionLocal() as session):
        mock_get_current_user = Mock(current_user)
        monkeypatch.setattr("src.services.auth.auth_service.get_current_user", mock_get_current_user)
        mock_get_current_user.refresh_token = None
        await session.commit()

    response = client.post("api/auth/logout")
    assert response.status_code == 401, response.text
    assert mock_get_current_user.refresh_token is None


@patch("src.routes.auth.auth_service.decode_refresh_token")
@patch("src.routes.auth.repository_users.get_user_by_email")
@patch("src.routes.auth.repository_users.update_token")
@patch("src.routes.auth.get_refresh_token")
def test_refresh_token_success(mock_get_refresh_token, mock_update_token, mock_get_user_by_email,
                               mock_decode_refresh_token, client):
    # Фіктивні дані для тесту
    fake_token = "fake_refresh_token"
    fake_email = "test@example.com"
    fake_user = User(id=1, user_email=fake_email, refresh_token=fake_token)
    fake_access_token = "fake_access_token"
    fake_refresh_token = "fake_new_refresh_token"

    # Налаштування моків
    mock_get_refresh_token.return_value = fake_token
    mock_decode_refresh_token.return_value = fake_email
    mock_get_user_by_email.return_value = fake_user

    # Мокування функції створення токенів
    if mock_get_user_by_email.refresh_token == fake_token:
        with patch("src.routes.auth.auth_service.create_access_token") as mock_create_access_token, \
                patch("src.routes.auth.auth_service.create_refresh_token") as mock_create_refresh_token:
            mock_create_access_token.return_value = fake_access_token
            mock_create_refresh_token.return_value = fake_refresh_token

            response = client.get("api/auth/refresh_token")

            assert response.status_code == 200

            assert response.json() == {"access_token": fake_access_token, "refresh_token": fake_refresh_token,
                                       "token_type": "bearer"}
            # Перевірка викликів моків
            mock_get_refresh_token.assert_called_once()
            mock_decode_refresh_token.assert_called_once_with(fake_token)
            mock_get_user_by_email.assert_called_once_with(fake_email, mock.ANY)  # Перевірка передачі бази даних
            mock_update_token.assert_called_once_with(fake_user, fake_refresh_token,
                                                      mock.ANY)  # Перевірка передачі бази даних


@patch("src.routes.auth.auth_service.decode_refresh_token")
@patch("src.routes.auth.repository_users.get_user_by_email")
@patch("src.routes.auth.repository_users.update_token")
@patch("src.routes.auth.get_refresh_token")
def test_refresh_token_fail(mock_get_refresh_token, mock_update_token, mock_get_user_by_email,
                            mock_decode_refresh_token, client):
    # Фіктивні дані для тесту
    fake_token = "fake_refresh_token"
    fake_email = "test@example.com"
    fake_user = User(id=1, user_email=fake_email, refresh_token=fake_token)
    fake_access_token = "fake_access_token"
    fake_refresh_token = "fake_new_refresh_token"

    # Налаштування моків
    mock_get_refresh_token.return_value = fake_token
    mock_decode_refresh_token.return_value = fake_email
    mock_get_user_by_email.return_value = fake_user
    mock_update_token.return_value = None
    # Мокування функції створення токенів
    if mock_get_user_by_email.refresh_token == fake_token:
        with patch("src.routes.auth.auth_service.create_access_token") as mock_create_access_token, \
                patch("src.routes.auth.auth_service.create_refresh_token") as mock_create_refresh_token:
            mock_create_access_token.return_value = fake_access_token
            mock_create_refresh_token.return_value = fake_refresh_token

            response = client.get("api/auth/refresh_token")
            assert response.status_code == 401
            assert response.json() == {"detail": messages.INVALID_REFRESH_TOKEN}
            # Перевірка викликів моків
            mock_get_refresh_token.assert_called_once()
            mock_decode_refresh_token.assert_called_once_with(fake_token)
            mock_get_user_by_email.assert_called_once_with(fake_email, mock.ANY)  # Перевірка передачі бази даних
            mock_update_token.assert_called_once_with(fake_user, fake_refresh_token,
                                                      mock.ANY)  # Перевірка передачі бази даних


