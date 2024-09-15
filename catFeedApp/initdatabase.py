from appMain.app import app, db
import os

if os.path.exists('appMain/catFeed.db'):
    print("Removing catFeed.db")
    os.remove('appMain/catFeed.db')

with app.app_context():
    print("Creating catFeed.db")
    db.create_all()