from classes.charLCD import CharLCD
from classes.DCMotor import DCMotor
from classes.distanceSensor import DistanceSensor
from classes.camera import Camera

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
        "RESOLUTION" : (1280, 720),     # Default resolution 720p
        "MAX_RESOLUTION" : (1920, 1080)
    }
    def __init__(self):
        try:
            self.display = CharLCD(address = self.LCD["LCD_I2C_ADDR"], height = self.LCD["ROWS"], width = self.LCD["COLS"])
            self.motor = DCMotor(en_1_pin=self.GPIOS["DC_MOTOR_EN1"], en_2_pin=self.GPIOS["DC_MOTOR_EN2"])
            self.picam = Camera(resolution=self.CAMERA["RESOLUTION"])
            self.foodsens = DistanceSensor(trig_pin=self.GPIOS["DSENS_TRIG"], echo_pin=self.GPIOS["DSENS_ECHO"])
            print("Hardware configured successfully")
        except Exception as e:
            self.display = None
            self.motor = None
            self.picam = None
            self.foodsens = None
            raise Exception("Error initializing hardware. Verify hardware configuration.")

try:
    hardwareAccess = HardwareConfig()
except Exception as e:
    print(e)
    raise e