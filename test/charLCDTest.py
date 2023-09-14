from charLCD import charLCDScreen
import time
import random
screen = charLCDScreen()

screen.clear()
screen.startScreenUpdater()
screen.writeRow(3,"TESTING")

time.sleep(2)
screen.writeRow(2,"TEST 2!!!")

time.sleep(3)
screen.clear()

time.sleep(2)
screen.writeRow(1,"HELLO!")

print(screen.getlinesfull())
screen.pop_row(4)
screen.stopScreenUpdater()
