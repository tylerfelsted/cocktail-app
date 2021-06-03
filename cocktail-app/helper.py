from flask import session, g
from models import db, connect_db, User, List, List_Drink, Drink
from sqlalchemy import and_

CURR_USER_KEY = "curr_user"

def do_login(user):
    session[CURR_USER_KEY] = user.username

def do_logout():
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

def extract_ingredients(drink):
    ingredients = []
    for i in range(15):
        ingredient = drink[f'strIngredient{i+1}']
        measure = drink[f'strMeasure{i+1}']
        if ingredient:
            if measure:
                ingredients.append(f"{measure} {ingredient}")
            else:
                ingredients.append(ingredient)
    return ingredients

def extract_drinks(drink_list):
    drinks = []
    for drink in drink_list.drinks:
        drinks.append({
            "idDrink": drink.drink_id,
            "strDrink": drink.name,
            "strDrinkThumb": drink.image_url
        });
    return drinks

def process_drink(json, action):
    data = {
        'drink': json['drink'],
        'list_id': json['list']
    }
    if action == 'add':
        add_drink(data)
    elif action == 'remove':
        remove_drink(data)


def add_drink(data):
    drink = data['drink']
    if not Drink.query.get(drink['id']):
        new_drink = Drink(drink_id=drink['id'], name=drink['name'], image_url=drink['image'])
        db.session.add(new_drink)
        db.session.commit()
    

    # Get list of drinks in specified list
    # Check if the drink is already in the list
    # If drink is not in list, add it to the list, otherwise, do nothing
    drinks = List.query.get(data['list_id']).drinks
    if not int(drink['id']) in [drink.drink_id for drink in drinks]:
        list_drink = List_Drink(list_id=data['list_id'], drink_id=drink['id'])
        db.session.add(list_drink)
        db.session.commit()

def remove_drink(data):
    drink = data['drink']
    drinks = List.query.get(data['list_id']).drinks
    if int(drink['id']) in [drink.drink_id for drink in drinks]:
        List_Drink.query.filter(and_(List_Drink.drink_id == drink['id'], List_Drink.list_id == data['list_id'])).delete()
        db.session.commit()
