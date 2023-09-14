
from classes.charLCD import charLCDScreen
from classes.DCMotor import DCMotor
import datetime

class catFeeder():

    def __init__(self):
        self.dispenser = DCMotor()
        self.screen = charLCDScreen()
        return
    
    def dispense(self, seconds):
        self.dispenser.dispense(seconds)
        return
    
    def updateTime(self):
        # Set cursor to top left corner
        self.screen.set_cursor(0,0)
        now = datetime.datetime.now()
        # write the time to the screen formatted in HH:MM AM/PM
        self.screen.write("Time: " + now.strftime("%I:%M %p"))
    
    
    
    
    
