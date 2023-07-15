#This python script runs when the system starts up and
#continupusly checks the feeds file and is responsible for 
#automatically triggering feeds
from datetime import datetime
import time, traceback
import threading
from classes.DCMotor import DCMotor
from classes.distanceSensor import read_distance
from classes.charLCD import charLCD
import os
import sys
import sqlite3 as sql

screen = charLCD()
motor = DCMotor()
FEED_SIZE = 10

feedsarray = []

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

db_path = os.path.join(BASE_DIR,"catFeed.sqlite3")

def updateScreen(feedsarray):
    distance = read_distance() * 100
    percentfull = round((100-(distance * 100 / 12)),0)
    status = ""
    if(distance<=8 or distance > 1000):
        status="Full"
    elif(distance>8 and distance <=12):
        status="~Half"
    elif(distance>12 and distance<14):
        status="low"
    elif(distance >=14):
        status="critical"
    i = 0
    now = datetime.now() #current date and time
    screen.clear()
    screen.setCursor(0,0)
    w=now.strftime("%I:%M %p") + " | " + status
    screen.write(w)
    for c,y in enumerate(feedsarray):
        screen.setCursor(c+1,0)
        y = y.strip()
        try:
            t = datetime.strptime(y,"%H:%M")
            t = t.strftime("%I:%M %p")
            s = "Feed " + str(c+1) + ": " + str(t)
            screen.write(s)
        except:
            continue
            #print("error writing time to screen")

def feed(time):
    print("Feed time!")
    date = datetime.now().strftime("%m/%d/%Y")
    try:
        conn = sql.connect(db_path)
        cur = conn.cursor()
    except sqlite3.Error as error:
        print("sqlite error while updating log")
        print(error)
    cur.execute("INSERT INTO feedlog (time,date,size,type) VALUES (?,?,?,?)",(time,date,'regular','automatic'))
    conn.commit()
    conn.close()
    motor.dispense(FEED_SIZE)
    screen.clear()
    screen.setCursor(1,0)
    screen.write("   Feeding time!")
    screen.setCursor(2,0)
    screen.write("        >x<")
    return

def checkFeedTime(feedsarray):
    rightnow = datetime.now().strftime("%H:%M")
    for y in feedsarray:
        y=y.strip()
        if(y == rightnow):
            feed(rightnow)
            return True
    return False

def thread_checkFeedTimes(event):
    #print("Feed time checking thread started")
    event.set()
    while(1):
        print("checking feed time") 
        if(checkFeedTime(feedsarray)):
            event.clear()
            time.sleep(60)
            event.set()
        
        time.sleep(15)
    print("thread 1 exited while loop")

def updateArray():
    feedsarray.clear()
    i = 0
    feedsfile = open(BASE_DIR + "/feedtimes.txt","r")
    for i,x in enumerate(feedsfile):
        try:
            feedsarray[i] = x
        except:
            feedsarray.append(x)

def thread_updateFeedsArray(event):
    #print("screen update thread started")
    while(1):
        print("updating screen")
        print(feedsarray)
        event.wait()
        updateArray()
        updateScreen(feedsarray)
        time.sleep(5)
    print("thread 2 exited while loop")

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

if __name__ == '__main__':
    event = threading.Event()
    try:
        feedsfile = open(BASE_DIR + "/feedtimes.txt","r")
        i=0 
        for x in feedsfile:
            if(i>3):
                break
            i = i + 1
            if x != "\n":
                feedsarray.append(x)

 
        t1=threading.Thread(target=thread_updateFeedsArray,args=(event,))
        t2=threading.Thread(target=thread_checkFeedTimes,args=(event,))
        t1.start()
        t2.start()

    except KeyboardInterrupt:
        t1.stop()
        t2.stop()
        exit(0)
