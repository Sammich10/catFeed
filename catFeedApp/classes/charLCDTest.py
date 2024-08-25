from charLCD import charLCD
import sys

screen = charLCD()

screen.initialize()
screen.clear()
# Check for input arguments
if(len(sys.argv) > 1):
    print(sys.argv[1])
    screen.writeRow(0, sys.argv[1])