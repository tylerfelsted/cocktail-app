import os
from unittest import TestCase

from models import db, connect_db, User, List, List_Drink, Drink


os.environ['DATABASE_URL'] = "postgresql://postgres:postgres@localhost:5433/cocktail_test"

from app import app, CURR_USER_KEY


db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class DrinkViewsTestCase(TestCase):
    """Test drink view functions"""

    def setUp(self):
        """Create test client and add test data"""
        self.client = app.test_client()

    def test_search_drinks(self):
        with self.client as c:
            resp = c.get('/drinks/search?search=margarita')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h5 class="card-title">Margarita</h5>', html)
    
    def test_show_drink_details(self):
        with self.client as c:
            resp = c.get('/drinks/11007')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Margarita</h1>', html)
            self.assertIn('<li>1 1/2 oz  Tequila</li>', html)