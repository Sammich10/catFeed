from objects.charLCD import CharLCD
from objects.DCMotor import DCMotor
from objects.distanceSensor import DistanceSensor
from objects.camera import Camera

class HardwareConfig:
    GPIOS = {
        "DSENS_TRIG" : 16,
        "DSENS_ECHO" : 20,
        "DC_MOTOR_EN1" : 19,
        "DC_MOTOR_EN2" : 26
    }
    LCD = {
        "LCD_I2C_ADDR" : 0x27,
        "ROWS" : 4,
        "COLS" : 20
    }
    CAMERA = {
        "RESOLUTION" : (720, 720),     # Default resolution 720p
        "MAX_RESOLUTION" : (1920, 1080)
    }
