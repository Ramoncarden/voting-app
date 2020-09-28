"""User model tests"""

# run these tests like:
#    python -m unittest test_user_model.py
from app import app  # nopep8

import os
from unittest import TestCase
from sqlalchemy import exc


from models import db, User, Likes

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///voter-test"
app.config["SQLALCHEMY_ECHO"] = False

# Create tables and delete data in each test

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for users"""

    def setUp(self):
        """Create test clien and sample data"""
        db.drop_all()
        db.create_all()

        test_user1 = User.signup('tester@test.com', 'tester987', 'password1')
        test_user1id = 99999
        test_user1.id = test_user1id

        test_user2 = User.signup('mcnair@test.com', 'McNair', 'qwerty')
        test_user2id = 1001
        test_user2.id = test_user2id

        db.session.commit()

        test_user1 = User.query.get(test_user1id)
        test_user2 = User.query.get(test_user2id)

        self.test_user1 = test_user1
        self.test_user1id = test_user1id

        self.test_user2 = test_user2
        self.test_user2id = test_user2id

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work"""

        u = User(
            email="testuser@testing.com",
            username="testuser",
            password="Ahashedpassword"
        )

        db.session.add(u)
        db.session.commit()

        # User should have 0 liked items
        self.assertEqual(len(u.likes), 0)

    # signup tests

    def test_valid_signup(self):
        user_signup = User.signup(
            "testy",
            "testing@tester.com",
            "asdfg"
        )
        userid = 2000
        user_signup.id = userid
        db.session.commit()

        user_signup = User.query.get(user_signup.id)
        self.assertIsNotNone(user_signup)
        self.assertEqual(user_signup.email, 'testing@tester.com')
        self.assertEqual(user_signup.username, 'testy')
        self.assertNotEqual(user_signup.password, 'asdfg')

    def test_invalid_username_signup(self):
        invalid_user = User.signup(
            'rolltide@test.com', None, 'funfunfun'
        )
        userid = 12345
        invalid_user.id = userid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        invalid_email = User.signup(None, 'user1', 'yuiop')
        userid = 54321
        invalid_email.id = userid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup('newuser@test.com', 'blaze', None)

        with self.assertRaises(ValueError) as context:
            User.signup('newuser@test.com', 'blaze', '')

    # Test authentication

    def test_valid_authentication(self):
        test_user = User.authenticate(self.test_user1.username, 'password1')
        self.assertIsNotNone(test_user)
        self.assertEqual(test_user.id, self.test_user1id)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate('randomusername', 'password1'))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(
            self.test_user1.username, 'notrightpassword'
        ))
