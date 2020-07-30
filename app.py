import os
from flask import Flask, render_template, request, flash, redirect, session, g, abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm
from models import db, connect_db, User

CURR_USER_KEY = 'curr_user'

app = Flask(__name__)

# Get DB_URI from environ variable. If not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///informed_voter_db')
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secert_voter2020')

connect_db(app)
db.create_all()

# *************************************************
# User signup, login, and logout


@app.before_request
def add_user_to_g():
    """If user logged in, add curr user to Flask global"""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None


def do_login(user):
    """Log in user"""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/')
def show_homepage():
    """Return Homepage"""

    return render_template('home-anon.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user signup.

    Create new user and add to db. Redirect to home page.

    If form not valid, present form.

    If user already exists with submitted username: flash error message and
    re-present form
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                email=form.email.data,
                username=form.username.data,
                password=form.password.data,
            )
            db.session.commit()

        except IntegrityError:
            flash('Username already exists', 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)
        return redirect('/')

    else:
        return render_template('users/signup.html', form=form)

# @app.route('login', methods=['GET', 'POST'])
# def login():
#     """Handle user login"""
