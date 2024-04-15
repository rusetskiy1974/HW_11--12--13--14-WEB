import unittest
from datetime import date
from unittest.mock import MagicMock, AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema
from src.repository.contacts import (
    days_to_birthday,
    get_contacts_birthday,
    get_contacts,
    get_all_contacts,
    get_contacts_first_name,
    get_contacts_last_name,
    get_contact_email,
    get_contact,
    create_contact,
    update_contact,
    delete_contact,
)


class TestAsyncContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.user = User(id=1, username="test_user", password="qwerty", user_email="test_email",
                         confirmed=True)
        self.session = AsyncMock(spec=AsyncSession)

    async def test_contacts_birthday(self):
        limit = 10
        offset = 0
        contacts = [Contact(id=1, first_name="test_first_name1", last_name="test_last_name1", email="test_email1",
                            phone="test_phone1", birth_date=date(2000, 1, 1), user=self.user),
                    Contact(id=2, first_name="test_first_name2", last_name="test_last_name2", email="test_email2",
                            phone="test_phone2", birth_date=date(2001, 1, 1), user=self.user), ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        results = await get_contacts_birthday(offset=offset, limit=limit, user=self.user, db=self.session)
        select_true_contacts = [contact for contact in contacts if days_to_birthday(contact.birth_date) <= 7]
        self.assertEqual(results, select_true_contacts)

    async def test_get_contacts(self):
        limit = 10
        offset = 0
        contacts = [Contact(id=1, first_name="test_first_name1", last_name="test_last_name1", email="test_email1",
                            phone="test_phone1", user=self.user),
                    Contact(id=2, first_name="test_first_name2", last_name="test_last_name2", email="test_email2",
                            phone="test_phone2", user=self.user), ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(offset=offset, limit=limit, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_all_contacts(self):
        limit = 10
        offset = 0
        contacts = [Contact(id=1, first_name="test_first_name1", last_name="test_last_name1", email="test_email1",
                            phone="test_phone1", user=self.user),
                    Contact(id=2, first_name="test_first_name2", last_name="test_last_name2", email="test_email2",
                            phone="test_phone2", user=self.user), ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_all_contacts(offset=offset, limit=limit, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contacts_by_first_name(self):
        limit = 10
        offset = 0
        first_name = "test_first_name"
        contacts = [Contact(id=1, first_name="test_first_name1", last_name="test_last_name1", email="test_email1",
                            phone="test_phone1", user=self.user),
                    Contact(id=2, first_name="test_first_name2", last_name="test_last_name2", email="test_email2",
                            phone="test_phone2", user=self.user), ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts_first_name(first_name=first_name, offset=offset, limit=limit,
                                               db=self.session, user=self.user)
        self.assertEqual(result, contacts)

    async def test_get_contacts_by_last_name(self):
        limit = 10
        offset = 0
        last_name = "test_last_name"
        contacts = [Contact(id=1, first_name="test_first_name1", last_name="test_last_name1", email="test_email1",
                            phone="test_phone1", user=self.user),
                    Contact(id=2, first_name="test_first_name2", last_name="test_last_name2", email="test_email2",
                            phone="test_phone2", user=self.user), ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts_last_name(last_name=last_name, offset=offset, limit=limit,
                                              db=self.session, user=self.user)
        self.assertEqual(result, contacts)

    async def test_get_contact_by_email(self):
        email = "test_email1"
        contact = Contact(id=1, first_name="test_first_name1", last_name="test_last_name1", email="test_email1",
                          phone="test_phone1", user=self.user)
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await get_contact_email(email=email, db=self.session, user=self.user)
        self.assertEqual(result, contact)

    async def test_get_contact(self):
        contact_id = 1
        contact = Contact(id=contact_id, first_name="test_first_name1", last_name="test_last_name1",
                          email="test_email1",
                          phone="test_phone1", user=self.user)

        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await get_contact(contact_id=contact_id, db=self.session, user=self.user)
        self.assertEqual(result, contact)

    async def test_create_contact(self):
        body = ContactSchema(id=1, first_name="test_first_name", last_name="test_last_name",
                             email="example@example.com",
                             phone="380673293127", birth_date=date(1998, 1, 11), friend_status=False)
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mocked_contact

        result = await create_contact(body=body, user=self.user, db=self.session)

        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birth_date, body.birth_date)
        self.assertEqual(result.friend_status, body.friend_status)

    async def test_update_contact_email_not_changed(self):
        contact_id = 1
        body = ContactUpdateSchema(first_name="test_first_name", last_name="test_last_name",
                                   email="example@example.com",
                                   phone="380673293127", birth_date=date.today(), friend_status=False)
        contact = Contact(id=contact_id, first_name="test_first_name",
                          last_name="test_last_name",
                          email="example@example.com",
                          phone="380673293127",
                          birth_date=date(2000, 1, 11),
                          friend_status=False)
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        if self.session.return_value.email == body.email:
            result = await update_contact(contact_id=contact_id, body=body, user=self.user, db=self.session)
            self.assertEqual(result, contact)
            self.assertEqual(result.first_name, body.first_name)
            self.assertEqual(result.last_name, body.last_name)
            self.assertEqual(result.email, body.email)
            self.assertEqual(result.phone, body.phone)
            self.assertEqual(result.birth_date, body.birth_date)
            self.assertEqual(result.friend_status, body.friend_status)

    async def test_update_contact_mail_changed_mail_exist(self):
        contact_id = 1
        body = ContactUpdateSchema(first_name="test_first_name", last_name="test_last_name",
                                   email="example2@example.com",
                                   phone="380673293127", birth_date=date.today(), friend_status=False)
        contact = Contact(id=contact_id, first_name="test_first_name",
                          last_name="test_last_name",
                          email="example@example.com",
                          phone="380673293127",
                          birth_date=date(2000, 1, 11),
                          friend_status=False)
        contact_with_same_email = Contact(id=2, first_name="test_first_name2",
                                          last_name="test_last_name2",
                                          email="example2@example.com",
                                          phone="380673293127",
                                          birth_date=date(1998, 1, 11),
                                          friend_status=False)

        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        if self.session.return_value.email != body.email:
            mocked_contact_ = MagicMock()
            mocked_contact_.scalar_one_or_none.return_value = contact_with_same_email
            result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
            self.assertFalse(result)
            self.session.commit.assert_not_called()

    async def test_update_contact_mail_changed_mail_not_exist(self):
        contact_id = 1
        body = ContactUpdateSchema(first_name="test_first_name", last_name="test_last_name",
                                   email="example2@example.com",
                                   phone="380673293127", birth_date=date.today(), friend_status=False)
        contact = Contact(id=contact_id, first_name="test_first_name",
                          last_name="test_last_name",
                          email="example@example.com",
                          phone="380673293127",
                          birth_date=date(2000, 1, 11),
                          friend_status=False)
        contact_with_same_email = Contact(id=2, first_name="test_first_name2",
                                          last_name="test_last_name2",
                                          email="example2@example.com",
                                          phone="380673293127",
                                          birth_date=date(1998, 1, 11),
                                          friend_status=False)

        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = contact
        if self.session.return_value.email != body.email:

            mocked_contact.scalar_one_or_none.return_value = None
            self.session.execute.return_value = mocked_contact

            if not self.session.return_value:
                mocked_contact.scalar_one_or_none.return_value = contact
                self.session.execute.return_value = mocked_contact

                result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
                self.assertEqual(result, contact)
                self.assertEqual(result.first_name, body.first_name)
                self.assertEqual(result.last_name, body.last_name)
                self.assertEqual(result.email, body.email)
                self.assertEqual(result.phone, body.phone)
                self.assertEqual(result.birth_date, body.birth_date)
                self.assertEqual(result.friend_status, body.friend_status)

    async def test_delete_contact_exist(self):
        contact_id = 1
        contact = Contact(id=contact_id, first_name="test_first_name",
                          last_name="test_last_name",
                          email="example@example.com",
                          phone="380673293127",
                          birth_date=date(2000, 1, 11),
                          friend_status=False)
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_delete_contact_not_exist(self):
        contact_id = 1
        contact = Contact(id=contact_id, first_name="test_first_name",
                          last_name="test_last_name",
                          email="example@example.com",
                          phone="380673293127",
                          birth_date=date(2000, 1, 11),
                          friend_status=False)
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(contact_id=contact_id, user=self.user, db=self.session)
        assert not result
        self.session.commit.assert_not_called()


if __name__ == '__main__':
    unittest.main()
