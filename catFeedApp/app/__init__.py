# Import Flask application modules
from flask import Flask, Blueprint, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Import the Cat Feeder hardware and configuration
from hardware import charLCD, DCMotor, distanceSensor, PiCam
from app.configuration import HardwareConfig as hwConfig
from app.configuration import BaseConfig as appConfig

# Import some system modules
import os

# Global app runtime variable(s)
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
db          = SQLAlchemy()

def create_app():
    """
    Creates the Flask app and initializes all the relevant components.

    Initializes the SQLAlchemy database, and sets up the application
    configuration. If this is the first time the app is being run, it also
    initializes the hardware components.

    Returns the Flask app object.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(appConfig)
    
    db.init_app(app)
    migrate = Migrate(app, db)
    
    from .routes import auth, catfeedapp, api
    app.register_blueprint(auth.bp)
    app.register_blueprint(catfeedapp.bp)
    app.register_blueprint(api.bp)
    
    @app.route('/')
    def root():
        """
        Redirects the user to the login page if they are not logged in, or the home
        page if they are.

        Returns:
            Response: The response object from the redirect.
        """
        return redirect(url_for('auth.root'))
    
    return app

def get_db():
    """
    Returns the database object.

    Returns:
        SQLAlchemy: The database object.
    """
    return db
