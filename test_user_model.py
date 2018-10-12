"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, FollowersFollowee, Favorite, Bcrypt

bcrypt = Bcrypt()

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


# FLASK_ENV=production python -m unittest test_user_model.py


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        
        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()
        Favorite.query.delete()

        db.session.commit()

        self.client = app.test_client()

        

    def tearDown(self):
        """After each test function, delete every table."""

        # :)

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password=bcrypt.generate_password_hash("HASHED_PASSWORD").decode('UTF-8')
        )

        v = User(
            email="vest@vest.com",
            username="vestuser",
            password=bcrypt.generate_password_hash("HASHED_PASSWORD").decode('UTF-8')
        )

        db.session.add(u)
        db.session.add(v)

        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(u.messages.count(), 0)
        self.assertEqual(u.followers.count(), 0)
        self.assertEqual(u.is_followed_by(v), False)
        self.assertEqual(u.is_following(v), False)

    def test_user_signup(self):

        u = User.signup(username='username',
            email='email@gmail.com',
            password='hashed_pwd',
            image_url='image_url',
        )

        db.session.commit()

        query = User.query.all()

        # Tests that user was added to DB

        self.assertEqual(len(query),1)

        # test that the user instance is equal to the query

        queried_user = User.query.first()

        self.assertEqual(u,queried_user)

        


    def test_user_auth(self):

        u = User.signup(username='username',
            email='email@gmail.com',
            password='hashed_pwd',
            image_url='image_url',
        )

        db.session.commit()

        auth_user = User.authenticate(u.username,'hashed_pwd')

        self.assertEqual(auth_user,u)

        # get full test coverage! :) for likes and follows... ask joel for clarification





