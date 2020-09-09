import os
import requests
import json
from flask import Flask, render_template, request, flash, redirect, session, g, abort, jsonify, Blueprint, url_for
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from keys import key
from flask_paginate import Pagination, get_page_parameter
from urllib.parse import quote

from forms import UserAddForm, LoginForm
from models import db, connect_db, User, GovMembers, Likes

BASE_URL = 'https://api.propublica.org/congress/v1/'
MEMBERS_API_URL = 'https://api.propublica.org/congress/v1/116/senate/members.json'
ALL_MEMBERS = 'https://api.propublica.org/congress/v1/116/senate/members.json'
MEMBER_VOTE_POSITION_API = 'https://api.propublica.org/congress/v1/members/'
BILL_API = 'https://api.propublica.org/congress/v1/bills/search.json'

# SPECIFIC_BILL_API = 'https://api.propublica.org/congress/v1/{congress}/bills'

CURR_USER_KEY = 'curr_user'

# mod = Blueprint()

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


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Welcome back {user.username}!", 'success')
            return redirect('/')

        flash('Invalid credentials', 'danger')

    return render_template('users/login.html', form=form)


@app.route('/users/like', methods=['GET', 'POST'])
def add_like():
    """Toggle a liked item for currently logged in user"""

    if not g.user:
        flash('Access unauthorized', 'danger')
        return redirect('/')

    member_id = request.args.get('member_id')
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')

    new_govmember_like = GovMembers(id=member_id,
                                    first_name=first_name,
                                    last_name=last_name)

    new_like = Likes(user_id=g.user.id, item_id=member_id)

    db.session.add(new_like)
    db.session.add(new_govmember_like)
    db.session.commit()

    # liked_msg_ids = [msg.id for msg in g.user.likes]

    return redirect('/')


@app.route('/users/like/<like_id>/delete', methods=['GET', 'POST'])
def remove_like(like_id):
    """Remove govmember from favorites"""

    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect('/')

    liked_member = GovMembers.query.get_or_404(like_id)

    user_likes = g.user.likes

    if liked_member in user_likes:
        g.user.likes = [
            like for like in user_likes if like != liked_member
        ]
    else:
        g.user.likes.append(liked_member)

    db.session.commit()
    return redirect('/')

    # user_likes = g.user_likes

    # if liked_item in user_likes:
    #     g.user.likes = [
    #         like for like in user_likes if like != liked_item]
    # else:
    #     g.user.likes.append(liked_item)

    # db.session.commit()
    # return redirect('/')


@app.route('/users/delete', methods=['POST'])
def delete_user():
    """Delete user"""

    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect('/')

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect('/signup')


@app.route('/logout')
def logout():
    """Handle user logout"""

    do_logout()

    flash("You have successfully logged out", 'success')
    return redirect('/login')


# *****************************************************
# General User routes and search routes


# *****************************************************
# Homepage and error pages


@app.route('/')
def show_homepage():
    """Return Homepage

    - anon: no feed, history or likes
    - logged in: show last 10 history searches and favorites
    """
    if g.user:
        username = g.user.username

        govmembers = GovMembers.query.all()

        liked_member_ids = [govmember.id for govmember in g.user.likes]

        liked_member_name = [
            member.first_name for member in govmembers if member in g.user.likes]

        liked_member_last_name = [
            member.last_name for member in govmembers if member in g.user.likes]

        print(liked_member_ids)
        print(liked_member_name)
        print(liked_member_last_name)

        return render_template('home.html', username=username, liked_member_ids=liked_member_ids,
                               liked_member_name=liked_member_name, liked_member_last_name=liked_member_last_name)

    else:
        return render_template('homepage.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/search/member')
def do_search():
    """Handle search data and send request to API"""

    response = requests.get(f"{BASE_URL}/members/B001267.json",
                            headers={'X-API-Key': key})
    data = response.json()
    first_name = data['results'][0]['first_name']
    last_name = data['results'][0]['last_name']

    return data


@app.route('/search')
def get_gov_official():
    """Gather list of government officials"""

    res = requests.get(ALL_MEMBERS,
                       headers={'X-API-Key': key})

    data = res.json()

    id = [member['id'] for member in data['results'][0]['members']]
    first_name = [member['first_name']
                  for member in data['results'][0]['members']]
    last_name = [member['last_name']
                 for member in data['results'][0]['members']]

    members = data['results'][0]['members']

    return render_template('search/gov-officials.html', id=id, first_name=first_name, last_name=last_name, members=members)


@app.route('/search/congress')
def get_congress_member():
    """Gather list of congress members"""

    res = requests.get(f"{BASE_URL}116/house/members.json",
                       headers={'X-API-Key': key})

    data = res.json()

    id = [member['id'] for member in data['results'][0]['members']]
    first_name = [member['first_name']
                  for member in data['results'][0]['members']]
    last_name = [member['last_name']
                 for member in data['results'][0]['members']]

    members = data['results'][0]['members']

    # liked_members_ids = [likes.id for govmembers in g.user.likes]

    return render_template('search/congress.html',
                           members=members,
                           )


@app.route('/search/member/<member_id>')
def get_member_info(member_id):
    """Retrieve government official individual data on link click"""

    params = {
        'limit': 20,
        'offset': 100
    }

    res = requests.get(
        f"{MEMBER_VOTE_POSITION_API}{member_id}/votes.json", headers={'X-API-Key': key}, params=params)

    response = requests.get(f"{BASE_URL}/members/{member_id}.json",
                            headers={'X-API-Key': key})

    response_data = response.json()
    member_contact_data = response_data['results'][0]

    data = res.json()
    # return data
    members_data = data['results'][0]['votes']

    return render_template('search/officials_voting.html', members_data=members_data, member_id=member_id, member_contact_data=member_contact_data)


@app.route('/search/bill')
def get_bill_info():
    """Retrieve all bill information"""

    params = {
        'offset': 300
    }

    search_term = request.args['search-form-input']
    parsed_search_term = quote(search_term)
    res = requests.get(f"{BILL_API}?query=\"{parsed_search_term}\"", headers={
                       'X-API-key': key}, params=params)
    data = res.json()
    # return data
    # print(parsed_search_term)
    search_results = data['results']
    bill_data = data['results'][0]['bills']

    return render_template('search/bill-voting.html', bill_data=bill_data, search_results=search_results)


@app.route('/search/bill/<bill_id>')
def get_bill_by_id(bill_id):
    """Retrieve individually selected bill"""

    id_no = bill_id.split('-')[0]
    congress_no = bill_id.split('-')[1]

    if bill_id[0] == "p":
        id_no = bill_id.split('-')[0].upper()

        res = requests.get(
            f"{BASE_URL}{congress_no}/nominees/{id_no}.json", headers={'X-API-Key': key})

        data = res.json()
        nomination_data = data['results'][0]

        return render_template("search/nomination.html", nomination_data=nomination_data)

    else:
        res = requests.get(
            f"{BASE_URL}{congress_no}/bills/{id_no}.json", headers={'X-API-Key': key})

        data = res.json()
        bill_data = data['results'][0]

        return render_template('search/individual-bill.html', bill_data=bill_data)
