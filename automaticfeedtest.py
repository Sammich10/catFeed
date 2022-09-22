
import sqlite3 as sql
from charLCD import charLCD
import sys
import os
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
from datetime import datetime
from update import checkFeedTime
testarray = []
testarray.append(datetime.now().strftime("%H:%M"))

print(testarray)
checkFeedTime(testarray)
print(done)
