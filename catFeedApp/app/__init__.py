# Flask application imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from flask_login import LoginManager
# Import the CatFeeder class
from app.hwCtrl.feeder import CatFeeder
from app.configs.hwCfg import HardwareConfig as hwConfig
# Import other modules
import os
import multiprocessing
import atexit

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('app.configs.appCfg.BaseConfig')
app.secret_key = "\xbe\xa0\x9a\xda\xe3\xbdv]'?\xd7S]4uA\x80\xb1v3\xab\xf4s?"

db = SQLAlchemy(app)

migrate = Migrate(app, db)

# lm = LoginManager()
# lm.setup_app(app)
# lm.login_view = 'login'

feeder = CatFeeder(hwConfig)

from app import models

# Check if this is the main process. This is used to initialize the feeder and start the camera only 
# once when the application is run or reloaded.
if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    # initialize the feeder and start the camera
    feeder.initialize()
    print("Feeder initialized")
    feeder.startCamera()
    print("Camera started")
    from app.appLocal import manager
    manager.start()
    def shutdown():
        manager.stop()
        feeder.stopCamera()
    atexit.register(shutdown)

from app import routes

