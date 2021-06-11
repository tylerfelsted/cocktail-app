Welcome to my Cocktail App: https://tyler-cocktail-app.herokuapp.com/

This is an application in which a user can search a database of mixed drinks, add any of those drinks to custom lists, and generate a list of ingredients required to make the drinks in a given list.

Upon first entering the site, a user is presented with a homepage that tells them they can search for drinks, or they can register or login. Without logging in, a user can search for any drink found in TheCocktailDB database. A list of drinks will appear with a title and thumbnail for each drink. There is a button to view more details about the drink, including ingredients, and directions for making the drink.
If a user chooses to register or login, they then gain the ability to create custom lists. Clicking on their username in the upper right corner will take them to a page which will show them any existing lists they have created. There is a button that will take them to a form to create a new list.
A new list can be created by entering a name and an optional description of the list.
Once at least one list has been created for that user, they can add any drink to it, by selecting the 'Add to list' button found next to any drink. A modal will pop up with all of this lists that the drink can be added to. Checking or unchecking any of theses lists, will add or remove that drink from those lists.
After adding a drinks to a list, a user can view a specific list by selecting it on their user details page. Any drinks added to that list will appear here. There is also a button to generate a list of ingredients. This will show all of the ingredients required to make all of the drinks in the selected list.

API used: https://www.thecocktaildb.com/api.php
I am using the free version of this api, which means that there is some functionality that is limited. It is not possible to browse all of the drinks without a subscription, so users can only find drinks by directly searching for them.

This application is built using Python, Flask, PostgreSQL, SQLAlchemy, HTML, Bootstrap, JavaScript, and JQuery.