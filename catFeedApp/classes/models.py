from appMain import db

class Owner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    
    def __repr__(self):
        return '<Owner %r>' % self.username
    
class FeedTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(80), unique=False, nullable=False)
    type = db.Column(db.Integer, unique=False, nullable=False)
    
    def __repr__(self):
        return '<FeedTime %r>' % self.time
    
class Feeding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(80), unique=False, nullable=False)
    type = db.Column(db.Integer, unique=False, nullable=False)
    date = db.Column(db.String(80), unique=False, nullable=False)
    
    def __repr__(self):
        return '<Feeding %r>' % self.time