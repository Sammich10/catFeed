# Cat feeder control classes
from classes.charLCD import CharLCD
from classes.DCMotor import DCMotor
from classes.distanceSensor import DistanceSensor
from classes.camera import Camera
import os

initialized = False
# Define feeder control objects
lcd = CharLCD(address=0x27)
motor = DCMotor(19,26)
camera = Camera(resolution=(720, 1080))
# Define distance sensor object and its GPIOs
DSENS_TRIG_GPIO = 16
DSENS_ECHO_GPIO = 20
dsens = DistanceSensor(DSENS_TRIG_GPIO, DSENS_ECHO_GPIO)

def initializeClasses():
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        print("Initializing feeder control classes")
        # Initialize the LCD screen
        try:
            lcd.initialize()
        except Exception as e:
            print(e)
        # Initialize the camera
        try:
            camera.initialize()
            camera.start()
        except Exception as e:
            print(e)
        # Setup the distance sensor GPIOs
        dsens.setup()
        # Setup the motor GPIOs
        motor.setup()
    
def cleanupClasses():
    global initialized
    if not initialized:
        return
    print("Closing feeder control classes")
    # Close the camera
    camera.cleanup()
    initialized = False