#This python script runs when the system starts up
import time, traceback, threading, os, sys, schedule
import sqlite3 as sql
from datetime import datetime
from classes.catFeeder import catFeeder
import config


# get the base dir of the catFeeder project
PROJECT_BASE_DIR = os.path.dirname(os.path.abspath(config.PROJECT_DIR))

db_path = os.path.join(PROJECT_BASE_DIR,"db/catFeed.sqlite3")
sys.path.append(PROJECT_BASE_DIR)

def feedTimesUpdate():
    SQL_QUERY = "SELECT * FROM FEED_TIMES ORDER BY id DESC"
    try:
        conn = sql.connect(db_path)
        feedTimes = conn.execute(SQL_QUERY).fetchall()
        print(feedTimes)
    except sql.Error as error:
        print("sqlite3 error fetching feed times:")
        print(error)
    return

# Function to schedule feed times and store job objects
def schedule_feed_times():
    feed_times = fetch_feed_times_from_db()

    for feed_time in feed_times:
        # ... (Same as before)

        # Schedule the feeding action at the specified feed time and store the job object
        job = schedule.every().day.at(feed_time_str).do(feed_action)
        scheduled_jobs[feed_time_str] = job

# Function to delete a scheduled job based on the feed time
def delete_job(feed_time_str):
    if feed_time_str in scheduled_jobs:
        job = scheduled_jobs[feed_time_str]
        schedule.cancel_job(job)
        del scheduled_jobs[feed_time_str]

if __name__ == '__main__':
    feedTimesUpdate()
