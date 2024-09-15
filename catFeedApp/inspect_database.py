from appMain.app import app, db
from sqlalchemy import text
import os

if os.path.exists('appMain/catFeed.db'):
    with app.app_context():
        # List all the tables in the database
        tables = db.engine.table_names()
        print(tables)
        for table in tables:
            print(table)
            print(db.session.execute(text("SELECT * FROM " + table)).all())
        
    
