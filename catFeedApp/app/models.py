from app import db
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///catFeed.db')

class Owner(db.Model):
    """
    Model representing owners in the database.
    
    Attributes:
        id (int): Unique ID of the owner record.
        username (str): The username of the owner record.
        email (str): The email of the owner record.
        password (str): The password of the owner record.
    """
    __tablename__ = 'owners'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    
    def __repr__(self):
        return '<Owner %r>' % self.username
    
class FeedTime(db.Model):
    """
    Model representing scheduled feeding times currently in the database.
    
    Attributes:
        id (int): Unique ID of the feed time record.
        time (str): The time of the feed time record.
        size (int): The size of the feed time record.
        type (int): The type of the feed time record.
    """
    __tablename__ = 'feedtimes'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(80), unique=False, nullable=False)
    size = db.Column(db.Integer, unique=False, nullable=False)
    type = db.Column(db.Integer, unique=False, nullable=False)
    
    def __repr__(self):
        return '<FeedTime %r>' % self.time
    
class Feeding(db.Model):
    """
    Model representing past feedings
    
    Attributes:
        id (int): Unique ID of the feed time record.
        time (str): The time of the feed time record.
        size (int): The size of the feed time record.
        type (int): The type of the feed time record.
        date (str): The date of the feed time record.
    """
    __tablename__ = 'feedings'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(80), unique=False, nullable=False)
    size = db.Column(db.Integer, unique=False, nullable=False)
    type = db.Column(db.Integer, unique=False, nullable=False)
    date = db.Column(db.String(80), unique=False, nullable=False)
    
    def __repr__(self):
        return '<Feeding %r>' % self.time