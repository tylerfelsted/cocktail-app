import os
from unittest import TestCase

from models import db, connect_db, User, List, List_Drink, Drink


os.environ['DATABASE_URL'] = "postgresql://postgres:postgres@localhost:5433/cocktail_test"

from app import app, CURR_USER_KEY


db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class ListViewsTestCase(TestCase):
    """Test list view functions"""

    def setUp(self):
        """Create test client and add test data"""
        User.query.delete()
        List.query.delete()
        db.session.commit()
        self.client = app.test_client()

        self.testuser1 = User.signup(username='testuser1', password='password1')
        self.list1 = List(user_id='testuser1', name='list1', description='This is a test list')
        db.session.add(self.list1)
        db.session.commit()
        db.session.refresh(self.list1)
        db.session.expunge(self.list1)

    def test_show_list_form(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.username
            resp = c.get('/lists/new')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<button class="btn btn-primary">Create List</button>', html)

    def test_list_form(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.username
            
            self.assertEqual(len(List.query.all()), 1)

            data = {
                'name': 'New List',
                'description': 'This is a brand new list!'
            }
            resp = c.post('/lists/new', data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            new_list_id = List.query.filter_by(name='New List').one().id

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<li><a href="/lists/{new_list_id}">New List</a></li>', html)
            self.assertEqual(len(List.query.all()), 2)

    def test_show_list(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.username
            resp = c.get(f'/lists/{self.list1.id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<h1>{self.list1.name}</h1>', html)
            self.assertIn(f'<p>{self.list1.description}</p>', html)