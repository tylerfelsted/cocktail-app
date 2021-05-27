import os
import requests

from flask import Flask, render_template, request, flash, redirect, session, g
from models import db, connect_db, User, List, List_Drink
from forms import UserForm, ListForm

CURR_USER_KEY = "curr_user"
API_BASE_URL = "https://www.thecocktaildb.com/api/json/v1/1"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5433/cocktail_db'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")

connect_db(app)

@app.before_request
def add_user_to_g():
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def do_login(user):
    session[CURR_USER_KEY] = user.username

def do_logout():
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/')
def show_home_page():
    return render_template("index.html")

@app.route('/register', methods=["GET", "POST"])
def register_user():
    """Add a new user"""

    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.signup(username, password)
        db.session.commit()
        do_login(user)
        return redirect('/')


    return render_template('new_user.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login_user():

    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            do_login(user)
            print('logged in!', user)
        else:
            print('login failed!')
        return redirect('/')

    return render_template('login.html', form=form)

@app.route('/drinks/search')
def search_drinks():
    search = request.args.get('search')
    res = requests.get(f'{API_BASE_URL}/search.php?s={search}')

    drinks = res.json()['drinks']


    return render_template('drinks.html', drinks=drinks)
