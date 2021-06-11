from flask import session, g
from models import db, connect_db, User, List, List_Drink, Drink
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

CURR_USER_KEY = "curr_user"

def do_login(user):
    """Adds the current user to the session"""
    session[CURR_USER_KEY] = user.username

def do_logout():
    """Removes the current user from the session"""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

def extract_ingredients(drink, with_measures):
    """Creates a list of ingredients required to make a drink.
    Unless measure is not present, or specifically excluded, it will prepend the ingredient with a measure"""
    ingredients = []
    for i in range(15):
        ingredient = drink[f'strIngredient{i+1}']
        measure = drink[f'strMeasure{i+1}']
        if ingredient:
            if with_measures and measure:
                ingredients.append(f"{measure} {ingredient}")
            else:
                ingredients.append(ingredient)
    return ingredients

def extract_drinks(drink_list):
    """Returns the id, name, and image for each drink in a list"""
    drinks = []
    for drink in drink_list.drinks:
        drinks.append({
            "idDrink": drink.drink_id,
            "strDrink": drink.name,
            "strDrinkThumb": drink.image_url
        });
    return drinks

def process_drink(json, action):
    """Either adds or removes a drink from a list, depending on the action specified"""
    data = {
        'drink': json['drink'],
        'list_id': json['list']
    }
    if action == 'add':
        return add_drink(data)
    elif action == 'remove':
        return remove_drink(data)


def add_drink(data):
    """Adds a drink to a list. Will add the drink to the local db if it is not already present"""
    drink = data['drink']
    if not Drink.query.get(drink['drink_id']):
        try:
            new_drink = Drink(drink_id=drink['drink_id'], name=drink['name'], image_url=drink['image_url'])
            db.session.add(new_drink)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

    # Get list of drinks in specified list
    # Check if the drink is already in the list
    # If drink is not in list, add it to the list, otherwise, do nothing
    drinks = List.query.get(data['list_id']).drinks
    if not int(drink['drink_id']) in [drink.drink_id for drink in drinks]:
        list_drink = List_Drink(list_id=data['list_id'], drink_id=drink['drink_id'])
        db.session.add(list_drink)
        db.session.commit()
        
    return {
        "method": "add_drink",
        "drink": drink,
        "list": data['list_id']
    }

def remove_drink(data):
    """Removes a drink from a list"""
    drink = data['drink']
    drinks = List.query.get(data['list_id']).drinks
    if int(drink['drink_id']) in [drink.drink_id for drink in drinks]:
        List_Drink.query.filter(and_(List_Drink.drink_id == drink['drink_id'], List_Drink.list_id == data['list_id'])).delete()
        db.session.commit()
    return {
        "method": "remove_drink",
        "drink": drink,
        "list": data['list_id']
    }