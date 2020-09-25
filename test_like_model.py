"""Like model tests"""

# run these tests like:
#    python -m unittest test_like_model.py

from app import app, CURR_USER_KEY  # nopep8
import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Likes, GovMembers

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///voter-test"
app.config["SQLALCHEMY_ECHO"] = False

# import app

# Create tables and delete data in each test

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Test views for Likes"""

    def setup(self):
        """Create test client, add sample data"""
        db.drop_all()
        db.create_all()

        self.id = 90210
        u = User.signup("tester@test.com", "tester123", "rolltide")
        u.id = self.id

        self.u = User.query.get(self.id)

        self.client = app.test_client()

        self.testuser = User.signup(email="test@test.com",
                                    username="testuser",
                                    password="testuser"
                                    )
        self.testuser_id = 8989
        self.testuser.id = self.testuser_id

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_member_likes(self):
        """Does basic model work?"""
        m1 = GovMembers(
            id="3000",
            first_name="Bill",
            last_name="Testman"
        )

        u = User.signup("newtester@testit.com", "newtester", "qwerty")
        uid = 6666
        u.id = uid
        db.session.add_all([m1, u])
        db.session.commit()

        u.likes.append(m1)

        db.session.commit()

        l = Likes.query.filter(Likes.user_id == uid).all()
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].item_id, m1.id)
