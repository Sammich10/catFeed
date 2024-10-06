from sqlalchemy import text
import os
import sys

# Add the parent directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db

if os.path.exists('app/catFeed.db'):
    with app.app_context():
        # List all the tables in the database
        tables = db.engine.table_names()
        print(tables)
        for table in tables:
            print(table)
            print(db.session.execute(text("SELECT * FROM " + table)).all())
        
    
