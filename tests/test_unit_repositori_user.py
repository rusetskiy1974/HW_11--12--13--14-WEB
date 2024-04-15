import unittest
from unittest.mock import MagicMock, AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.schemas.user import UserSchema
from src.repository.users import (get_user_by_email,
                                  create_user,
                                  update_token,
                                  confirmed_email,
                                  update_avatar)


class TestAsyncUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.user = User(id=1, username="test_user", password="qwerty", user_email="test@example.com",
                         role="user", confirmed=True, avatar="test_avatar")
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_user_by_email(self):
        test_email = 'test_email'
        user = User(id=1, username="test_user", password="qwerty", user_email="test_email", confirmed=True)
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        result = await get_user_by_email(test_email, self.session)
        self.assertEqual(result, user)
        self.assertEqual(result.user_email, user.user_email)
        self.assertEqual(result.username, user.username)
        self.assertEqual(result.password, user.password)
        self.assertEqual(result.confirmed, user.confirmed)
        self.assertEqual(result.id, user.id)

    async def test_get_user_by_email_not_found(self):
        test_email = 'test_email'
        user = User(id=1, username="test_user", password="qwerty", user_email="test_email", confirmed=True)
        mock_user = MagicMock()
        mock_user.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mock_user
        result = await get_user_by_email(test_email, self.session)
        self.assertEqual(result, None)

    async def test_create_user(self):
        body = UserSchema(username='test_user', user_email='example@example.com', password='qwerty')
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mocked_contact

        result = await create_user(body=body, db=self.session)

        self.assertIsInstance(result, User)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.user_email, body.user_email)
        self.assertEqual(result.password, body.password)

    async def test_update_avatar(self):
        email = "test@example.com"
        avatar_url = "avatar_url"

        mocked_user = MagicMock()
        mocked_user.get_user_by_email(email, self.session).return_value = self.user
        self.session.execute.return_value = mocked_user
        result = await update_avatar(email=email, url=avatar_url, db=self.session)
        self.assertEqual(result.avatar, avatar_url)
        self.session.commit.assert_called()
        self.session.refresh.assert_called()

    async def test_confirmed_email(self):
        email = "test@example.com"

        mocked_user = MagicMock()
        mocked_user.get_user_by_email(email, self.session).return_value = self.user
        self.session.execute.return_value = mocked_user
        result = await confirmed_email(email=email, db=self.session)
        self.assertEqual(self.user.confirmed, True)
        self.session.commit.assert_called()

    async def test_update_token(self):
        test_token = "test_token"
        result = await update_token(user=self.user, token=test_token, db=self.session)
        self.assertEqual(self.user.refresh_token, test_token)
        self.session.commit.assert_called()


if __name__ == '__main__':
    unittest.main()
