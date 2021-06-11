import os
import requests

from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, List, List_Drink, Drink
from forms import UserForm, ListForm
from helper import CURR_USER_KEY, do_login, do_logout, extract_ingredients, extract_drinks, process_drink


API_BASE_URL = "https://www.thecocktaildb.com/api/json/v1/1"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
uri = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5433/cocktail_db')
if uri.startswith('postgres://'):
    uri = uri.replace("://", "ql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")

connect_db(app)

@app.before_request
def add_user_to_g():
    """Adds the current logged in user to the flask global to allow for authorization"""
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None


@app.route('/')
def show_home_page():
    """Displays the home page. Displays links to register or login if no user is currently logged in.
    Otherwise it displays a random assortment of cocktails"""
    if g.user:
        drinks = []
        for i in range(10):
            res = requests.get(f'{API_BASE_URL}/random.php')
            drinks.append(res.json()['drinks'][0])
        return render_template("home.html", drinks=drinks)
    return render_template("home-anon.html")

@app.route('/register', methods=["GET", "POST"])
def register_user():
    """Add a new user"""

    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        try:
            user = User.signup(username, password)
            db.session.commit()
        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/register.html', form=form)
        do_login(user)
        flash(f"Registered {user.username}", "success")
        return redirect('/')

    return render_template('users/register.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login_user():
    """Logs in a user"""
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
    """Logs out a user"""
    do_logout()
    flash("Logged out!", "info")
    return redirect('/')

@app.route('/users/<username>')
def show_user_details(username):
    """Displays a users username and all of the drinks lists they have created"""
    if g.user.username == username:
        user = User.query.get_or_404(username)
        return render_template('users/details.html', user=user)

@app.route('/drinks/search')
def search_drinks():
    """Allows a user to search TheCocktailDB for any cocktail"""
    search = request.args.get('search')
    res = requests.get(f'{API_BASE_URL}/search.php?s={search}')
    drinks = res.json()['drinks']

    return render_template('drinks/search_drinks.html', drinks=drinks, search=search)

@app.route('/drinks/<int:drink_id>')
def show_drink_details(drink_id):
    """Displays details on any cocktail, including its name, an image, ingredients and directions for making it."""
    res = requests.get(f'{API_BASE_URL}/lookup.php?i={drink_id}')
    drink = res.json()['drinks'][0]
    ingredients = extract_ingredients(drink, True)
    return render_template('drinks/details.html', drink=drink, ingredients=ingredients)

@app.route('/lists/new', methods=["GET", "POST"])
def show_list_form():
    """Displays a form for creating a new list"""
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
    """Shows a lists name and description, as well as any drinks a user had added to it"""
    drink_list = List.query.get_or_404(list_id)
    if g.user.username != drink_list.user.username:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    drinks = extract_drinks(drink_list)
    return render_template('list_details.html', drink_list=drink_list, drinks=drinks)

@app.route('/lists/<int:list_id>/ingredients')
def show_list_ingredients(list_id):
    """Shows a list of ingredients required to make all the drinks in a given list"""
    drink_list = List.query.get_or_404(list_id)
    if g.user.username != drink_list.user.username:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    all_ingredients = []
    for drink in drink_list.drinks:
        print(drink.drink_id)
        res = requests.get(f'{API_BASE_URL}/lookup.php?i={drink.drink_id}')
        drink = res.json()['drinks'][0]
        ingredients = extract_ingredients(drink, False)
        for ingredient in ingredients:
            all_ingredients.append(ingredient)
    return render_template("list_ingredients.html", ingredients=set(all_ingredients), drink_list=drink_list)
    


#-----------------API ROUTES------------------------
@app.route('/api/lists/add-drink', methods=["POST"])
def add_drink_to_list():
    """Adds a specified drink, to a specified list"""
    res = process_drink(request.json, 'add')
    return jsonify(res)

@app.route('/api/lists/remove-drink', methods=["POST"])
def remove_drink_from_list():
    """Removes a specified drink from a specified list"""
    res = process_drink(request.json, 'remove')
    return jsonify(res)

@app.route('/api/drinks/<int:drink_id>')
def get_drink_info(drink_id):
    """Returns the lists that a drink belongs to"""
    drink = Drink.query.get(drink_id)
    drink_lists={
        "lists": []
    }
    if drink:
        drink_lists["lists"] = [list_element.id for list_element in drink.lists]
    return jsonify(drink_lists)
    