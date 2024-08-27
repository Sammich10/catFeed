from classes.charLCD import CharLCD
from classes.DCMotor import DCMotor
from classes.distanceSensor import DistanceSensor

# Define feeder control objects
lcd = CharLCD()
motor = DCMotor(2)
# Define distance sensor object and its GPIOs
DSENS_TRIG_GPIO = 16
DSENS_ECHO_GPIO = 20
dsens = DistanceSensor(DSENS_TRIG_GPIO, DSENS_ECHO_GPIO)

# Initialize the LCD screen
lcd.initialize()
# Setup the distance sensor GPIOs
dsens.setup()
