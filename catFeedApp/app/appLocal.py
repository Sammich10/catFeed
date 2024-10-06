from app import app, db, feeder
import time
import datetime
import threading

feedMonitor_cv = threading.Condition()
feed_flag = False
FEED_TIMEOUT_SECONDS = 60
LCD_UPDATE_RATE_SECONDS = 10
FEED_TIME_UPDATE_RATE_SECONDS = 15
stop_threads = False

def setFeedFlag():
    global feed_flag
    print("Setting feed flag")
    feedMonitor_cv.acquire()
    feed_flag = True

def resetFeedFlag():
    global feed_flag
    print("Resetting feed flag")
    feedMonitor_cv.notify()
    feedMonitor_cv.release()
    feed_flag = False

def triggerFeed(ftype, fsize):
    from app.models import Feeding, FeedTime
    global feed_flag
    print("Triggering feed")
    feed_flag = True
    #trigger the feed
    feeder.motor.forward(fsize * 3)
    # create a timeout thread to reset the feed flag after the timeout period
    threading.Timer(FEED_TIMEOUT_SECONDS, resetFeedFlag).start()
    # If type is 1, it is a 1 time feed
    if ftype == 1:
        # Remove the feed time from the database
        FeedTime.query.filter_by(time = time.strftime("%H:%M")).delete()
    # Add the feed record to the database
    new_feeding = Feeding(time = time.strftime("%H:%M:%S"), type = type, date = time.strftime("%Y-%m-%d"), size = size)
    db.session.add(new_feeding)
    db.session.commit()

def feedTimeMonitor_thread():
    from app.models import FeedTime
    with app.app_context():
        while True:
            # Check the feed time database
            feed_times = FeedTime.query.all()
            timeNow = datetime.datetime.now().strftime("%H:%M")
            for feed_time in feed_times:
                # Check if the time matches
                if feed_time.time == timeNow:
                    # Trigger the feed
                    size = feed_time.size
                    type = feed_time.type
                    triggerFeed(type, size)
                    # Wait for the feed flag to be reset to enter the next loop
                    feedMonitor_cv.wait()
            time.sleep(FEED_TIME_UPDATE_RATE_SECONDS)

def lcdMonitor_thread():
    from app.models import FeedTime
    with app.app_context():
        while True:
            # Get the current time
            timeNow = datetime.datetime.now().strftime("%H:%M")
            # Get upcoming feed times, max of 3
            feed_times = FeedTime.query.order_by(FeedTime.time).all()
            # Get the feeding times that precede the current time
            feed_times_past = [ft for ft in feed_times if ft.time < timeNow]
            # Get the feeding times that follow the current time
            feed_times_future = [ft for ft in feed_times if ft.time > timeNow]
            # Show up to 3 feeding times, displaying the feed times after the current time first, then the feed times before the current time
            feed_times_display = feed_times_past[:min(3, len(feed_times_past))] + feed_times_future[:min(3, len(feed_times_future))]
            # Display the feed times
            array = [[' ' for i in range(feeder.display.LCD_WIDTH)] for j in range(feeder.display.LCD_HEIGHT)]
            array[0] = "Upcoming Feeds:"
            for i in range(len(feed_times_display)):
                # Display the time converted from 24 hour format to 12 hour format with AM/PM
                timeString = time.strftime("%I:%M %p", time.strptime(feed_times_display[i].time, "%H:%M"))
                array[i+1] = timeString
            
            for i in range(len(array)):
                feeder.display.writeRow(i, array[i])
            
            time.sleep(LCD_UPDATE_RATE_SECONDS)

# Initialize the local application process
def catFeedLocalProc():
    global stop_threads
    feedMonitor = threading.Thread(target=feedTimeMonitor_thread)
    feedMonitor.start()
    screenMonitor = threading.Thread(target=lcdMonitor_thread)
    screenMonitor.start()
    while True:
        if stop_threads:
            feedMonitor.join()
            screenMonitor.join()
            break
        time.sleep(15)