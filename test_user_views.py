"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_views.py


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


# FLASK_ENV=production python -m unittest test_user_views.py


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

    def test_user_view(self):
        """Does basic model views work?"""

        # not authenticated tests
        response = self.client.get('/')

        ideal_response = b'<h4>New to Warbler?</h4>'
        
        self.assertEqual(response.status_code,200)

        self.assertIn(ideal_response,response.data)

        # authenticated tests]

        u = User(
            email="test@test.com",
            username="testuser",
            password=bcrypt.generate_password_hash("HASHED_PASSWORD").decode('UTF-8')
        )

        self.session[CURR_USER_KEY] = u.id

        self.assertEqual(response.status_code,200)


# test login/logout with view session  


        # v = User(
        #     email="vest@vest.com",
        #     username="vestuser",
        #     password=bcrypt.generate_password_hash("HASHED_PASSWORD").decode('UTF-8')
        # )

        # db.session.add(u)
        # db.session.add(v)

        # db.session.commit()

        # # User should have no messages & no followers
        # self.assertEqual(u.messages.count(), 0)
        # self.assertEqual(u.followers.count(), 0)
        # self.assertEqual(u.is_followed_by(v), False)
        # self.assertEqual(u.is_following(v), False)
        # # self.assertIn('testuser', u.authenticate('testuser','HASHED_PASSWORD'))


