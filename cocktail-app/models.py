from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    """User Model. Contains a username and an encrypted password"""
    __tablename__ = "users"

    username = db.Column(db.String(15), primary_key=True)
    password = db.Column(db.Text, nullable=False)

    lists = db.relationship('List', backref="user")

    def __repr__(self):
        return f"<Username: {self.username}>"

    @classmethod
    def signup(cls, username, password):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class List(db.Model):
    """List model. Contains an id, a user id to identify which user the list belongs to, a name, and a description."""
    __tablename__ = "lists"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(15), db.ForeignKey('users.username', ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(15), nullable=False)
    description = db.Column(db.String(100))

    drinks = db.relationship("Drink", secondary="lists_drinks", backref="lists")

class List_Drink(db.Model):
    """A join table which shows which drinks are in which lists"""
    __tablename__ = "lists_drinks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id', ondelete="CASCADE"), nullable=False)
    drink_id = db.Column(db.Integer, db.ForeignKey('drinks.drink_id', ondelete="CASCADE"), nullable=False)

class Drink(db.Model):
    """Drink Model. Contains the id for the drink found in TheCocktailDB"""
    __tablename__ = "drinks"

    drink_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, nullable=False)

    def serialize(self):
        return {
            'drink_id': self.drink_id,
            'name': self.name,
            'image_url': self.image_url
        }


def connect_db(app):
    """Connect the db to the Flask app"""

    db.app = app
    db.init_app(app)