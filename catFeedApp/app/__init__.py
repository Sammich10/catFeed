"""
Initialization of the Flask application
"""

# Flask application imports
from flask import Flask, Blueprint, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from flask_login import LoginManager
# Import the CatFeeder class
from hardware import charLCD, DCMotor, distanceSensor, PiCam
from app.configuration import HardwareConfig as hwConfig
from app.configuration import BaseConfig as appConfig

import atexit

# Import some system modules
import os

# Global app runtime variable(s)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db = SQLAlchemy()
cam = None
motor = None
distSensor = None
disp = None

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
    
    # If this is the first time the app is being run, initialize the hardware
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        initialize_hardware() 
    
    from .routes import auth, catfeedapp, api
    app.register_blueprint(auth.bp)
    app.register_blueprint(catfeedapp.bp)
    app.register_blueprint(api.bp)
    
    @app.route('/')
    def root():
        return redirect(url_for('auth.root'))
    
    return app

def get_db():
    """
    Returns the database object.

    Returns:
        SQLAlchemy: The database object.
    """
    return db

def get_camera():
    """
    Returns the camera object

    Returns:
        PiCam.PiCam: The camera object
    """
    return cam

def get_motor():
    """
    Returns the motor object
    
    Returns:
        DCMotor.DCMotor: The motor object
    """
    return motor

def get_distance_sensor():
    """
    Returns the distance sensor object
    
    Returns:
        distanceSensor.DistanceSensor: The distance sensor object
    """
    return distSensor

def get_display():
    """
    Returns the display object
    
    Returns:
        charLCD.CharLCD: The display object
    """
    return disp

def initialize_hardware():
    """
    Initializes the hardware objects with the proper configuration parameters
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        RuntimeError if the hardware objects are not initialized properly
    """
    global cam, motor, distSensor, disp
    if hwConfig.HW_ENABLE["CAMERA"]:
        cam = PiCam.Camera(resolution=hwConfig.CAMERA["RESOLUTION"])
        if cam.initialize():
            cam.start()
            print("Camera hardware initialized.")
        else:
            print("Camera hardware initialization failed.")
    else:
        cam = None
        print("Camera hardware not enabled.")
    if hwConfig.HW_ENABLE["MOTOR"]:
        motor = DCMotor.DCMotor(en_1_pin=hwConfig.GPIOS["DC_MOTOR_EN1"], en_2_pin=hwConfig.GPIOS["DC_MOTOR_EN2"])
        motor.initialize()
    else:
        motor = None
        print("Motor hardware not enabled.")
    if hwConfig.HW_ENABLE["DSENS"]:
        distSensor = distanceSensor.DistanceSensor(trig_pin=hwConfig.GPIOS["DSENS_TRIG"], echo_pin=hwConfig.GPIOS["DSENS_ECHO"])
        distSensor.initialize()
    else:
        distSensor = None
        print("Distance sensor hardware not enabled.")
    if hwConfig.HW_ENABLE["DISPLAY"]:
        disp = charLCD.CharLCD(address = hwConfig.LCD["LCD_I2C_ADDR"], height = hwConfig.LCD["ROWS"], width = hwConfig.LCD["COLS"])
        disp.initialize()
    else:
        disp = None
        print("Display hardware not enabled.")

def shutdown_hardware():
    """
    Cleanup method for the hardware objects.  This method is called
    automatically when the application is shut down.

    Args:
        None

    Returns:
        None
    """
    
    if cam is not None:
        cam.cleanup()

atexit.register(shutdown_hardware)