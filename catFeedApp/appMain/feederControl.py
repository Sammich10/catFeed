from classes.charLCD import CharLCD
from classes.DCMotor import DCMotor
from classes.distanceSensor import DistanceSensor

# Define feeder control objects
lcd = CharLCD()
motor = DCMotor(2)
dsens = DistanceSensor(16, 20)

# Initialize the LCD screen
lcd.initialize()
