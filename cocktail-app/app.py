import os
import requests

from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from models import db, connect_db, User, List, List_Drink, Drink
from forms import UserForm, ListForm
from helper import CURR_USER_KEY, do_login, do_logout, extract_ingredients, extract_drinks, process_drink


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
        flash(f"Registered {user.username}", "success")
        return redirect('/')

    return render_template('users/register.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login_user():

    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            do_login(user)
            flash(f"Welcome, {user.username}!", "success")
            return redirect('/')
        else:
            flash('Incorrect username/password', "danger")

    return render_template('users/login.html', form=form)

@app.route('/logout')
def logout_user():
    do_logout()
    flash("Logged out!", "info")
    return redirect('/')

@app.route('/users/<username>')
def show_user_details(username):
    if g.user.username == username:
        user = User.query.get_or_404(username)
        return render_template('users/details.html', user=user)

@app.route('/drinks/search')
def search_drinks():
    search = request.args.get('search')
    res = requests.get(f'{API_BASE_URL}/search.php?s={search}')
    drinks = res.json()['drinks']

    return render_template('drinks/drinks.html', drinks=drinks)

@app.route('/drinks/<int:drink_id>')
def show_drink_details(drink_id):
    res = requests.get(f'{API_BASE_URL}/lookup.php?i={drink_id}')
    drink = res.json()['drinks'][0]
    ingredients = extract_ingredients(drink)
    return render_template('drinks/details.html', drink=drink, ingredients=ingredients)

@app.route('/lists/new', methods=["GET", "POST"])
def show_list_form():
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    form = ListForm()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        new_list = List(user_id=g.user.username, name=name, description=description)
        db.session.add(new_list)
        db.session.commit()
        return redirect(f'/users/{g.user.username}')

    return render_template('list_form.html', form=form)

@app.route('/lists/<int:list_id>')
def show_list(list_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    drink_list = List.query.get_or_404(list_id)
    drinks = extract_drinks(drink_list)
    return render_template('list_details.html', drink_list=drink_list, drinks=drinks)


@app.route('/api/lists/add-drink', methods=["POST"])
def add_drink_to_list():
    process_drink(request.json, 'add')
    return 'success'

@app.route('/api/lists/remove-drink', methods=["POST"])
def remove_drink_from_list():
    process_drink(request.json, 'remove')
    return 'success'

@app.route('/api/drinks/<int:drink_id>')
def get_drink_info(drink_id):
    drink = Drink.query.get(drink_id)
    if drink:
        drink_lists = {
            "lists": [list_element.id for list_element in drink.lists]
        }
        return jsonify(drink_lists)
    return "Nothing"