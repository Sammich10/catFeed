# Import database libraries
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sqlite3 as sql
# Import system libraries
import os
import sys
import time as ti
import threading
import atexit
import cv2
import io
# Database models
from classes.models import engine, Owner, Feeding, FeedTime
from appMain.feederControl import hardwareAccess
# Threads
lcdControl = None
timeChecker = None
# Thread control
stop_threads = False
running_threads = []
# Thread flags / shared variables
TimeToFeed = False
feed = None


# Check if the current time matches any of the feedtimes in the database
def checkFeedtimes():
    # Get the current time
    now = ti.time()

    # Get the feedtimes from the database
    connection = engine.connect()
    feedtimes = connection.execute(text("SELECT * FROM feedtimes")).fetchall()
    
    # Loop through the feedtimes
    for feedtime in feedtimes:
        # Convert the time string to a time object
        time = ti.strptime(feedtime.time, "%H:%M")
        # Convert the time object to a time in seconds
        time = ti.mktime(time)
        # Check if the time is equal to the current time in hours and minutes
        if time == now:
            print("It is time to feed the cat")
            # Return true
            return feedtime

    # Return false
    return None

def checkFeedTimes_thread(stop_threads):
    # This thread will continuously poll the database and check if the current time matches any of the feedtimes in the database
    # If it does, set the flag to True to trigger a feeding from the control thread
    global feed
    global TimeToFeed
    while not stop_threads:
        feed = checkFeedtimes()
        if feed is not None:
            TimeToFeed = True
            ti.sleep(100)
        ti.sleep(5)
        
def getUpcomingFeedtimes(num = 3):
    # Get the current time
    now = ti.time()

    # Get the feedtimes from the database
    connection = engine.connect()
    feedtimes = connection.execute(text("SELECT * FROM feedtimes")).fetchall()
    
    upcomingFeedtimes = []
    # Check for up to 2 upcoming feeds in the future (today's earliest feedtimes)
    for feedtime in feedtimes:
        # Check if the time is in the future
        if feedtime.time > now:
            upcomingFeedtimes.append(feedtime)
    
    # No feed times later today
    if len(upcomingFeedtimes) == 0:
        # Get the earliest 3 feedtimes from the database (tomorrows earliest feedtimes)
        for i in range(0, len(feedtimes)):
            if i > num:
                break
            if feedtimes[i].time < now:
                upcomingFeedtimes.append(feedtimes[i])
    
    return upcomingFeedtimes

def updateDisplay(charArray):
    if hardwareAccess.display is not None:
        if len(charArray) > 4:
            charArray = charArray[0:4]
        for row in charArray:
            hardwareAccess.display.writeRow(row)
    else:
        print("No display connected")
            
def displayUpcomingFeeds(upcomingFeedtimes):
    numFeeds = len(upcomingFeedtimes)
    display = [["Upcoming Feeds:"]]
    for i in range(numFeeds):
        if i > hardwareAccess.display.LCD_HEIGHT-1:
            break
        time = str(upcomingFeedtimes[i].time)
        # Convert the time as HH:MM AM/PM
        display.append(time)
    updateDisplay(display)
    
def getLastFeedtime():
    connection = engine.connect()
    lastFeedtime = connection.execute(text("SELECT * FROM Feeding ORDER BY time DESC LIMIT 1")).fetchone()
    return lastFeedtime
    
def lcd_thread(stop_threads):
    print("Starting appMain.lcd_thread")
    while not stop_threads():
        upcomingFeedtimes = getUpcomingFeedtimes()
        if len(upcomingFeedtimes) > 0:
            displayUpcomingFeeds(upcomingFeedtimes)
        else:
            updateDisplay([["No upcoming feeds"]])
        ti.sleep(10)
        lastFeedtime = getLastFeedtime()
        if lastFeedtime is not None:
            updateDisplay([["Last Fed: " + str(lastFeedtime.time)]])
        ti.sleep(10)
        
        

def start():
    print("Starting appMain.update background threads")
    global lcdControl
    global timeChecker
    global stop_threads    
   
    stop_threads = False
    threads_to_start = []
    lcdControl = threading.Thread(target=lcd_thread, args=(lambda: stop_threads,))
    threads_to_start.append(lcdControl)
    timeChecker = threading.Thread(target=checkFeedTimes_thread, args=(lambda: stop_threads,))
    threads_to_start.append(timeChecker)
    
    for thread in threads_to_start:
        print("Starting thread: " + str(thread))
        thread.start()
        running_threads.append(thread)
    
    atexit.register(stop)
    
def stop():
    print("Stopping appMain.update background threads")
    global stop_threads
    global lcdControl
    global timeChecker
    stop_threads = True
    for(thread) in running_threads:
        print("Joining thread: " + str(thread))
        thread.join()
start()