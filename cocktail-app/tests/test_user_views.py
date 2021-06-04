import os
from unittest import TestCase

from models import db, connect_db, User, List, List_Drink, Drink


os.environ['DATABASE_URL'] = "postgresql://postgres:postgres@localhost:5433/cocktail_test"

from app import app, CURR_USER_KEY


db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewsTestCase(TestCase):
    """Test user view functions"""

    def setUp(self):
        """Create test client, add sample data"""
        User.query.delete()
        db.session.commit()
        self.client = app.test_client()

        self.testuser1 = User.signup(username='testuser1', password='password1')
        db.session.commit()

    def test_show_user_details(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.username
            
            resp = c.get(f'/users/{self.testuser1.username}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<h3>{self.testuser1.username}</h3>', html)

    def test_