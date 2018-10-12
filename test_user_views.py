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

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


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

        self.u = User(
            email="test@test.com",
            username="testuser",
            password=bcrypt.generate_password_hash("HASHED_PASSWORD").decode('UTF-8'),
            image_url= None,     
        )

        db.session.add(self.u)
        db.session.commit()


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

        

    def test_login(self):
        """Test that login function works"""

        CURR_USER_KEY = "curr_user"
        client = app.test_client()
        # result = client.post('/login', data={'username': 'testuser', 'password': 'HASHED_PASSWORD'})
        
        # import pdb; pdb.set_trace()
        with self.client as c:
            with c.session_transaction() as session:
                result = client.post('/login', data={'username': 'testuser', 'password': 'HASHED_PASSWORD'})
            # If it redirects, the login function worked correctly, otherwise it renders template
            self.assertEqual(result.status_code,302)
          
        with self.client as c:
            with c.session_transaction() as session:
                result = client.post('/login', data={'username': 'testuser', 'password': 'NOTTHEPASSWORD'})
            # If it redirects, the login function worked correctly, otherwise it renders template
            self.assertEqual(result.status_code,200)
        

    def test_logout(self):
        """Test that logout function works"""

        client = app.test_client()

        CURR_USER_KEY = "curr_user"

        with self.client as c:
            with c.session_transaction() as session:
                result = client.post('/login', data={'username': 'testuser', 'password': 'HASHED_PASSWORD'})
            # print(session)
            # self.assertEqual(CURR_USER_KEY in session, True)
            self.assertEqual(result.status_code,302)


            result = client.get('/logout')
    

            self.assertEqual(CURR_USER_KEY in session,False)


        





# class MessageViewTestCase(TestCase):
#     """Test views for messages."""

#     def setUp(self):
#         """Create test client, add sample data."""

#         User.query.delete()
#         Message.query.delete()

#         self.client = app.test_client()

#         self.testuser = User.signup(username="testuser",
#                                     email="test@test.com",
#                                     password="testuser",
#                                     image_url=None)

#         db.session.commit()

#     def test_add_message(self):
#         """Can user add a message?"""

#         # Since we need to change the session to mimic logging in,
#         # we need to use the changing-session trick:

#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess[CURR_USER_KEY] = self.testuser.id

#             # Now, that session setting is saved, so we can have
#             # the rest of ours test

#             resp = c.post("/messages/new", data={"text": "Hello"})

#             # Make sure it redirects
#             self.assertEqual(resp.status_code, 302)

#             msg = Message.query.one()
#             self.assertEqual(msg.text, "Hello")
