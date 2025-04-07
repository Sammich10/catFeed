import os

class BaseConfig(object):
    """
    Flask app base configuration
    """
    DEBUG=False
    # SECRET_KEY="\xbe\xa0\x9a\xda\xe3\xbdv]'?\xd7S]4uA\x80\xb1v3\xab\xf4s?"
    SECRET_KEY = 'dev'
    # Get the path to the database file
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'catFeed.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DB_PATH

class HardwareConfig:
    """
    Hardware configuration class
    """
    # Define GPIOs
    GPIOS = {
        "DSENS_TRIG" : 16,
        "DSENS_ECHO" : 20,
        "DC_MOTOR_EN1" : 19,
        "DC_MOTOR_EN2" : 26
    }
    # Define LCD parameters
    LCD = {
        "LCD_I2C_ADDR" : 0x27,
        "ROWS" : 4,
        "COLS" : 20
    }
    # Define camera parameters
    CAMERA = {
        "RESOLUTION" : (1080, 1080),     # Default resolution 720p
        "MAX_RESOLUTION" : (1920, 1080),
        "V_FLIP" : True,
        "H_FLIP" : False,
        "ROTATION" : 0
    }
    # Define hardware enablement
    HW_ENABLE = {
        "DISPLAY" : True,
        "CAMERA" : True,
        "MOTOR" : True,
        "DSENS" : False
    }

class DatabaseConfig:
    """
    Database configuration class
    """
    # Define database parameters
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'catFeed.db')
    DB_NAME = 'catFeed.db'
    
class TaskConfig:
    """
    Task configuration class
    """
    FEED_TIMEOUT_SECONDS = 60
    LCD_UPDATE_RATE_SECONDS = 10
    LCD_ITERATE_PANES_RATE_SECONDS = 20
    FEED_TIME_UPDATE_RATE_SECONDS = 15