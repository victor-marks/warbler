import os

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, EditAddForm, LoginForm, MessageForm
from models import db, connect_db, User, Message, Favorite

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///warbler'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""
    print('\n\n\n\n', 'boop')

    print('\n\n\n\n', session)

    # import pdb; pdb.set_trace()

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.data['username'],
                password=form.data['password'],
                email=form.data['email'],
                image_url=form.data['image_url'] or 'https://t3.ftcdn.net/jpg/00/64/67/52/240_F_64675209_7ve2XQANuzuHjMZXP3aIYIpsDKEbF5dD.jpg',
            )
            db.session.commit()

        except IntegrityError as e:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(username=form.data['username'],
                                 password=form.data['password'])

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""
    
    do_logout()

    # No flash message 

    return redirect("/login")

##############################################################################
# General user routes:

@app.route('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)

    num_of_likes = user.num_of_likes()

    return render_template('users/show.html', user=user, num_of_likes=num_of_likes)


@app.route('/users/<int:user_id>/favorites')
def show_users_favorites(user_id):
    """Show favorites from user."""

    user = User.query.get_or_404(user_id)
    favorite_list = user.favorites.all()

    num_of_likes = user.num_of_likes()

    return render_template('users/favorites.html', user=user, favorite_list=favorite_list, num_of_likes=num_of_likes)



@app.route('/users/<int:user_id>/following')
def show_following(user_id):
    """Show list of people this user is following."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/following.html', user=user)


@app.route('/users/<int:user_id>/followers')
def users_followers(user_id):
    """Show list of followers of this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/followers.html', user=user)


@app.route('/users/follow/<int:follow_id>', methods=['POST'])
def add_follow(follow_id):
    """Add a follow for the currently-logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followee = User.query.get_or_404(follow_id)
    g.user.following.append(followee)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followee = User.query.get(follow_id)
    g.user.following.remove(followee)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """Update profile for current user."""

    user = User.query.get(session[CURR_USER_KEY])

    form = EditAddForm(obj=user)

    if form.validate_on_submit():

        # FIX THIS!
        user_auth = User.authenticate(username=g.user.username, password=form.data['password'])   

        if user_auth:

            user.username = request.form.get('username')
            user.email = request.form.get('email')
            user.image_url = request.form.get('image_url')
            user.header_image_url = request.form.get('header_image_url')
            user.bio = request.form.get('bio')

            db.session.commit()

            return redirect(f"/users/{user.id}")

    return render_template('users/edit.html',user=user, form=form)

@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


##############################################################################
# Messages routes:

@app.route('/messages/new', methods=["GET", "POST"])
def messages_add():
    """Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.data['text'])
        g.user.messages.append(msg)
        db.session.commit()

        return redirect(f"/users/{g.user.id}")

    return render_template('messages/new.html', form=form)


@app.route('/messages/<int:message_id>', methods=["GET"])
def messages_show(message_id):
    """Show a message."""

    msg = Message.query.get(message_id)
    return render_template('messages/show.html', message=msg)


@app.route('/messages/<int:message_id>/delete', methods=["POST"])
def messages_destroy(message_id):
    """Delete a message."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    msg = Message.query.get(message_id)
    db.session.delete(msg)
    db.session.commit()

    return redirect(f"/users/{g.user.id}")


@app.route('/messages/<int:message_id>/favorite', methods=["POST"])
def add_favorite_message(message_id):
    """add favorite message to database."""

    if not g.user:
        flash("Please login.")
        return redirect("/login")

    user_id = g.user.id
    favorite = Favorite(user_id=user_id,msg_id=message_id)
    db.session.add(favorite)
    db.session.commit()

    return redirect(f"/users/{g.user.id}")


@app.route('/messages/<int:message_id>/unfavorite', methods=["POST"])
def remove_favorite_message(message_id):
    """remove favorite message to database."""

    if not g.user:
        flash("Please login.")
        return redirect("/login")

    user_id = g.user.id
    unfavorite = Favorite.query.filter(Favorite.msg_id==message_id).first()
    # import pdb; pdb.set_trace()
    db.session.delete(unfavorite)
    db.session.commit()

    return redirect("/")


##############################################################################
# Homepage and error pages


@app.route('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followees
    """

    if g.user:

        user = User.query.get(session[CURR_USER_KEY])

        following_ids = [f.id for f in user.following] + [g.user.id]

        messages = (Message
                    .query
                    .order_by(Message.timestamp.desc())
                    .filter(Message.user_id.in_(following_ids))
                    .limit(100))

        favorites = Favorite.query.all()
        list_of_favorites = [fav.msg_id for fav in favorites if fav.user_id == g.user.id]

        return render_template('home.html', messages=messages, favorites=list_of_favorites)

    else:
        return render_template('home-anon.html')


@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html'), 404


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
