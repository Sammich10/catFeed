from charLCD import charLCD
from datetime import datetime
import time, traceback
import threading
from DCMotor import DCMotor
from distanceSensor import read_distance
import os
import sys
import sqlite3 as sql
screen = charLCD()
motor = DCMotor()
feedsarray = []
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR,"catFeed.sqlite3")

def updateScreen(feedsarray):
    distance = read_distance() * 100
    percentfull = round((100-(distance * 100 / 12)),0)
    status = ""
    if(distance<=6 or distance > 1000):
        status="Full"
    elif(distance>6 and distance <=9):
        status="~Half"
    elif(distance>9 and distance<11):
        status="low"
    elif(distance >=11):
        status="critical"
    i = 0
    now = datetime.now() #current date and time
    screen.clear()
    screen.setCursor(0,0)
    w=now.strftime("%I:%M %p") + " | " + status
    screen.write(w)
    c = 1
    for y in feedsarray:
        screen.setCursor(c,0)
        y = y.strip()
        t = datetime.strptime(y,"%H:%M")
        t = t.strftime("%I:%M %p")
        s = "Feed " + str(c) + ": " + str(t)
        screen.write(s)
        c = c+1
    return

def checkFeedTime(feedsarray):
    rightnow = datetime.now().strftime("%H:%M")
    date = datetime.now().strftime("%m/%d/%Y")
    for y in feedsarray:
        y=y.strip()
        if(y == rightnow):
            print("Feed time!")
            try:
                conn = sql.connect(db_path)
                cur = conn.cursor()
            except sqlite3.Error as error:
                print("sqlite error while updating log")
                print(error)
            cur.execute("INSERT INTO feedlog (time,date,size,type) VALUES (?,?,?,?)",(rightnow,date,'regular','automatic'))
            conn.commit()
            conn.close()
            motor.dispense(1.25)
            screen.clear()
            screen.setCursor(1,0)
            screen.write("   Feeding time!")
            screen.setCursor(2,0)
            screen.write("        >x<")
            time.sleep(60)
    return

def updateArray():
    i = 0
    feedsfile = open(BASE_DIR + "/feedtimes.txt","r")
    for x in feedsfile:
        if(i>2):
            break
        i = i + 1
        if x != "\n":
            feedsarray.append(x)
starttime = time.time()
#test automatic feeding
if(len(sys.argv)>1):
    if(sys.argv[1]=="test"):
       testarray=[]
       testarray.append(datetime.now().strftime("%H:%M"))
       print(testarray)
       print("testing...")
       checkFeedTime(testarray)
       print("test complete")
       exit(0)

while(1):
    try:
        updateArray()
        updateScreen(feedsarray)
        checkFeedTime(feedsarray)
        feedsarray.clear()
        time.sleep(60.0 - ((time.time()-starttime)%60))
    except KeyboardInterrupt:
        exit(0)
