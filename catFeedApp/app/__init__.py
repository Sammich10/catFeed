from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from flask_login import LoginManager
from app.hwCtrl.feeder import CatFeeder
import os
import multiprocessing
import time
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('app.configs.appCfg.BaseConfig')
app.secret_key = "\xbe\xa0\x9a\xda\xe3\xbdv]'?\xd7S]4uA\x80\xb1v3\xab\xf4s?"

db = SQLAlchemy(app)

migrate = Migrate(app, db)

# lm = LoginManager()
# lm.setup_app(app)
# lm.login_view = 'login'

feeder = CatFeeder()

if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    feeder.initialize()
    feeder.startCamera()
    print("Feeder initialized")

from app import routes, models
