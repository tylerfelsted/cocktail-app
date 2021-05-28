from flask import session, g


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
            "idDrink": drink.id,
            "strDrink": drink.name,
            "strDrinkThumb": drink.image_url
        });
    return drinks