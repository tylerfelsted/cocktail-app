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

    def test_show_register_form(self):
        """Register form is displayed"""

        with self.client as c:
            resp = c.get('/register')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<button class="btn btn-primary">Sign me up!</button>', html)

    def test_sign_up(self):
        """A new user can register for the site"""

        with self.client as c:
            form_data = {'username': 'testuser2', 'password': 'password2'}
            resp = c.post('/register', data=form_data)

            self.assertEqual(resp.status_code, 302)
            with c.session_transaction() as sess:
                self.assertTrue(sess.get(CURR_USER_KEY))

    def test_sign_up_existing_username(self):
        """A new user cannot use an existing username"""

        with self.client as c:
            form_data = {'username': 'testuser1', 'password': 'password3'}
            resp = c.post('/register', data=form_data)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<button class="btn btn-primary">Sign me up!</button>', html)
            self.assertIn('<div class="alert alert-danger">Username already taken</div>', html)

    def test_show_login_form(self):
        """Login form is displayed"""

        with self.client as c:
            resp = c.get('/login')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<button class="btn btn-primary">Login</button>', html)

    def test_login(self):
        """A user can log in"""

        with self.client as c:
            form_data = {'username': 'testuser1', 'password': 'password1'}
            resp = c.post('/login', data=form_data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<a class="nav-link" href="/users/testuser1">testuser1</a>', html)
            self.assertIn('<div class="alert alert-success">Welcome, testuser1!</div>', html)
            with c.session_transaction() as sess:
                self.assertEqual(sess.get(CURR_USER_KEY), self.testuser1.username)

    def test_login_wrong_password(self):
        """A user cannot login with invalid credentials, and a warning message is displayed."""

        with self.client as c:
            form_data = {'username': 'testuser1', 'password': 'wrongpassword'}
            resp = c.post('/login', data=form_data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<div class="alert alert-danger">Incorrect username/password</div>', html)
            with c.session_transaction() as sess:
                self.assertFalse(sess.get(CURR_USER_KEY))

    def test_logout(self):
        """A user can log out"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.username
            
            resp = c.get('/logout')
            self.assertEqual(resp.status_code, 302)

            with c.session_transaction() as sess:

                self.assertEqual(sess.get(CURR_USER_KEY), None)

    def test_show_user_details(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.username
            
            resp = c.get(f'/users/{self.testuser1.username}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<h3>{self.testuser1.username}</h3>', html)