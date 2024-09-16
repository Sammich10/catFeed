from appMain.app import db
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///catFeed.db')

class Owner(db.Model):
    __tablename__ = 'owners'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    
    def __repr__(self):
        return '<Owner %r>' % self.username
    
class FeedTime(db.Model):
    __tablename__ = 'feedtimes'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(80), unique=False, nullable=False)
    size = db.Column(db.Integer, unique=False, nullable=False)
    type = db.Column(db.Integer, unique=False, nullable=False)
    
    def __repr__(self):
        return '<FeedTime %r>' % self.time
    
class Feeding(db.Model):
    __tablename__ = 'feedings'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(80), unique=False, nullable=False)
    size = db.Column(db.Integer, unique=False, nullable=False)
    type = db.Column(db.Integer, unique=False, nullable=False)
    date = db.Column(db.String(80), unique=False, nullable=False)
    
    def __repr__(self):
        return '<Feeding %r>' % self.time