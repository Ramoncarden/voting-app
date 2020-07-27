"""SQLAlchemy models for Informed Voter"""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class User(db.Model):
    """User in the system"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    username = db.Column(db.Text, nullable=False, unique=True)


def connect_db(app):
    """
    Connect this database to provided Flask app
    Call this in Flask app 
    """

    db.app = app
    db.init_app(app)
