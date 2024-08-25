from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.secret_key = "\xbe\xa0\x9a\xda\xe3\xbdv]'?\xd7S]4uA\x80\xb1v3\xab\xf4s?"
# Hard coded for now
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'catFeed.db')

db = SQLAlchemy(app)

# Import routes after app and db are initialized
from appMain import routes