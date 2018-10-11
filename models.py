"""SQLAlchemy models for Warbler."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class FollowersFollowee(db.Model):
    """Connection of a follower <-> followee."""

    __tablename__ = 'follows'

    followee_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    follower_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    image_url = db.Column(
        db.Text,
        default="https://t3.ftcdn.net/jpg/00/64/67/52/240_F_64675209_7ve2XQANuzuHjMZXP3aIYIpsDKEbF5dD.jpg",
    )

    header_image_url = db.Column(
        db.Text,
        default="/static/images/warbler-hero.jpg"
    )

    bio = db.Column(
        db.Text,
        default='A Warblista!'
    )

    location = db.Column(
        db.Text,
        default="The Nest!"

    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    messages = db.relationship('Message', backref='user', lazy='dynamic')

    favorites = db.relationship('Favorite', backref='user', lazy='dynamic')


    followers = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(FollowersFollowee.follower_id == id),
        secondaryjoin=(FollowersFollowee.followee_id == id),
        backref=db.backref('following', lazy='dynamic'),lazy='dynamic'
        )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    def is_followed_by(self, other_user):
        """Is this user followed by `other_user`?"""

        return bool(self.followers.filter_by(id=other_user.id).first())

    def is_following(self, other_user):
        """Is this user following `other_use`?"""

        return bool(self.following.filter_by(id=other_user.id).first())

    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            # import pdb; pdb.set_trace()   

            if is_auth:
                return user

        return False

    def num_of_likes(self):
        """Get num of likes for specific user"""

        num_of_likes = self.favorites.count()
        
        return num_of_likes


class Message(db.Model):
    """An individual message ("warble")."""

    __tablename__ = 'messages'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    text = db.Column(
        db.String(140),
        nullable=False,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

class Favorite(db.Model):
    """Maps a users id to their favorite message (id) """

    __tablename__ = 'favorites'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    msg_id = db.Column(
        db.Integer,
        db.ForeignKey('messages.id', ondelete='CASCADE'),
        nullable=False,
    )

    messages = db.relationship('Message', backref='favorites')


# might need to change name below to do conflict from table name
    # favorites = db.relationship(
    # "User",
    # secondary="follows",
    # primaryjoin=(FollowersFollowee.follower_id == id),
    # secondaryjoin=(FollowersFollowee.followee_id == id),
    # backref=db.backref('following', lazy='dynamic'),lazy='dynamic'
    # )

#    followers = db.relationship(
#         "User",
#         secondary="follows",
#         primaryjoin=(FollowersFollowee.follower_id == id),
#         secondaryjoin=(FollowersFollowee.followee_id == id),
#         backref=db.backref('following', lazy='dynamic'),lazy='dynamic'
#         )


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
