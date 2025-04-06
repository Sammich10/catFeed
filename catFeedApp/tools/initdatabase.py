import os
import sys

# Add the parent directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, get_db

# Create the Flask app
app = create_app()

# Initialize the database
db = get_db()

# Define the path to the database file
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'catFeed.db')

# Check if the database file exists
if os.path.exists(db_path):
    print("Removing catFeed.db")
    os.remove(db_path)

# Create the database and all tables
with app.app_context():
    print("Creating catFeed.db")
    db.create_all()
    print("Tables created:")
    print(db.engine.table_names())