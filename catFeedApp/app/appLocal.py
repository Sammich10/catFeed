from app import app, db, feeder
import time
import datetime
import threading
import weakref

feedMonitor = None
screenMonitor = None

feedMonitor_cv = threading.Condition()
feed_flag = False
FEED_TIMEOUT_SECONDS = 60
LCD_UPDATE_RATE_SECONDS = 10
LCD_ITERATE_PANES_RATE_SECONDS = 20
FEED_TIME_UPDATE_RATE_SECONDS = 15
stop_threads = False

mainProcess_cv = threading.Condition()
upcomingFeedsString = ""
pastFeedsString = ""

class TaskManager:
    """
    The TaskManager class is responsible for scheduling tasks (functions) to run at regular intervals (using threads) 
    and starting, stopping and managing their execution.
    
    Attributes:
        tasks (dict): A dictionary to store the tasks and their associated information.
        lock (threading.Lock): A lock to ensure thread safety when accessing the tasks dictionary.
        tickrate (int): The rate at which the tasks are executed (in seconds).
        last_tick (float): The time at which the last tick occurred.
        run_tasks (bool): A flag indicating whether the tasks should be run.
        stop_tasks (bool): A flag indicating whether the tasks should be stopped.
        queue (list): A list to store tasks that need to be scheduled.

    Methods:
        __init__(): Initializes the TaskManager instance.
        register_task(name, func, interval): Registers a new task with a given name, function, and interval.
        _schedule_task(name, func, interval): Schedules a task to run immediately if it's the first time, and then starts a new thread to run the task at the specified interval.
        _start_task(name): Starts a new thread to run the task at the specified interval.
        _run_task(name): The main function that runs the task at the specified interval, updating the last_run and next_run times as needed.
    """
    
    def __init__(self):
        """
        Initializes the TaskManager instance.
        
        Args:
            None
        
        Returns:
            None
        """
        self.tasks = {}
        self.lock = threading.Lock()
        self.tickrate = 1
        self.last_tick = time.time()
        self.run_tasks = False
        self.stop_tasks = False
        self.queue = []
    
    def _schedule_task(self, name, func, interval):
        """
        Schedules a task to run immediately if it's the first time, and then starts a new thread to run the task at the specified interval.
        
        Args:
            name (str): The name of the task.
            func (function): The function to be executed by the task.
            interval (float): The interval at which the task should be executed (in seconds).
        
        Returns:
            None
            
        Raises:
            ValueError: If the task is already registered.
        """
        if name in self.tasks:
            raise ValueError(f"Task '{name}' already registered")
        print(f"Registered task: {name}")
        self.tasks[name] = {
            'func': func,
            'interval': interval,
            'thread': None,
            'last_run': None,
            'next_run': None,
            'fStopped': False
        }
        self._start_task(name)
    
    def _start_task(self, name):
        """
        Starts a new thread to run the task at the specified interval.
        
        Args:
            name (str): The name of the task.
        
        Returns:
            None
            
        Raises:
            ValueError: If the task is not registered.
        """
        with self.lock:
            if self.tasks[name]['thread'] is None:
                raise ValueError(f"Attempted to start task '{str(name)}' that is not registered")
            # Run the task once to initialize the last_run and next_run times
            task = self.tasks[name]
            task['func']()
            task['last_run'] = time.time()
            task['next_run'] = time.time() + task['interval']
            task['fStopped'] = False
            # Start a new thread to run the task at the specified interval
            thread = threading.Thread(target=self._run_task, args=(name,), daemon=True)
            thread.start()
            self.tasks[name]['thread'] = weakref.ref(thread)
            print(f"Started task: {name}")
    def _run_task(self, name):
        """
        Runs a task in an infinite loop, sleeping until the next scheduled run time, and then executing the task function.
        
        Args:
            name (str): The name of the task.
        
        Returns:
            None
        """
        task = self.tasks[name]
        while True and not self.stop_tasks and not task['fStopped']:
            with self.lock:
                # If the next scheduled run of the task is in the past, it is time to run the task
                if task['next_run'] < time.time():
                    # Run the task
                    task['func']()
                    # Update the next scheduled run time
                    task['last_run'] = time.time()
                    # Update the next scheduled run time
                    task['next_run'] = time.time() + task['interval']
            # Update the tasks last tick time
            self.last_tick = time.time()
            # Sleep the thread for the tickrate duration
            time.sleep(self.tickrate)
    # Returns the status of a task, including its last run time, next run time, and thread status
    def get_task_status(self, name):
        with self.lock:
            task = self.tasks.get(name)
            if task is None:
                return None
            return {
                'last_run': task['last_run'],
                'next_run': task['next_run'],
                'thread': task['thread']() if task['thread'] else None
            }

    def register_task(self, name, func, interval):
        """
        Registers a new task with a given name, function, and interval.
        
        Args:
            name (str): The name of the task.
            func (function): The function to be executed by the task.
            interval (float): The interval at which the task should be executed (in seconds).
        
        Returns:
            None
        """
        with self.lock:
            if self.run_tasks:
                try:
                    self._schedule_task(name, func, interval)
                    print(f"Registered task: {name} to run every {interval} seconds")
                except ValueError:
                    print(f"Task '{name}' already registered")
            else:
                self.queue.append((name, func, interval))
                print(f"Queued task: {name}")
    
    def unregister_task(self, name):
        """
        Unregisters a task, stopping its thread and removing it from the task dictionary.
        
        Args:
            name (str): The name of the task to be unregistered.
        
        Returns:
            None
        """
        with self.lock:
            task = self.tasks.pop(name, None)
            if task is None:
                return
            print("Unregistered task: " + name)
            task['fStopped'] = True
            thread = task['thread']()
            if thread is not None:
                print("Stopping task thread: " + name, "thread id: " + str(thread.ident))
                thread.join()
    
    def start(self):
        """
        Starts the task manager, scheduling all queued tasks and enabling task scheduling.
        
        Args:
            None
        
        Returns:    
            None
        """
        self.run_tasks = True
        while self.queue:
            name, func, interval = self.queue.pop(0)
            self._schedule_task(name, func, interval)
    
    def stop(self):
        """
        Stops the task manager, stopping all task threads and disabling task scheduling.
        
        Args:
            None
        
        Returns:
            None
        """
        self.queue.clear()
        self.run_tasks = False
        self.stop_tasks = True
        for name, task in self.tasks.items():
            print(f"Stopping task: {name}")
            thread = task['thread']()
            if thread is not None:
                thread.join()
            self.queue.append((name, task['func'], task['interval']))

def triggerFeed(fsize):
    print("Triggering feed")
    if feeder.display is not None: 
        threading.Thread(target=feeder.display.feedTimeDisplayRoutine, args=(fsize*3,)).start()
    if feeder.motor is not None:
        threading.Thread(target=feeder.motor.forward, args=(fsize*3,)).start()

def checkFeedTime():
    print("Checking feed times")
    from app.models import FeedTime
    from app.models import Feeding
    with app.app_context():
        # Check the feed time database
        feed_times = FeedTime.query.order_by(FeedTime.time).all()
        # Get the current time
        timeNow = datetime.datetime.now().strftime("%H:%M")
        updateUpcomingFeeds(feed_times, timeNow)
        # Check if the current time matches any of the feed times
        for feed_time in feed_times:
            if feed_time.time == timeNow:
                size = feed_time.size
                type = feed_time.type
                # Trigger the feed
                triggerFeed(size)
                # Add the feed record to the database
                new_feeding = Feeding(time = time.strftime("%H:%M"), type = type, date = time.strftime("%Y-%m-%d"), size = size)
                db.session.add(new_feeding)
                if type == 1:
                    # Remove the feed time from the database if it is a 1 time feed
                    FeedTime.query.filter_by(time = feed_time.time).delete()
                db.session.commit()
        past_feeds = Feeding.query.order_by(Feeding.time.desc()).all()
        if len(past_feeds) > 0:
            # update the feed times global variable
            updatePastFeeds(past_feeds)
        
def updatePastFeeds(feed_times, maxNumDisplay=3):
    # Get the three most recent feeding times
    """
    Updates the global variable pastFeedsString with the maxNumDisplay most recent feed times in 12 hour 
    format with AM/PM, and the month and day of the week in 3 character format.

    Args:
        feed_times (list): A list of FeedTime objects
        maxNumDisplay (int): The maximum number of feed times to display
        
    Returns:
        None
    """
    feed_times_display = feed_times[:maxNumDisplay]
    timesString = []
    for i in range(min(maxNumDisplay, len(feed_times_display))):
        print("Time: " + feed_times_display[i].time + " Date: " + feed_times_display[i].date)
        # Display the time converted from 24 hour format to 12 hour format with AM/PM, but remove leading zero for times before 10. Add the month and day of the week in 3 character format
        timesString.append(time.strftime("%l:%M %p", time.strptime(feed_times_display[i].time, "%H:%M")) + " " + time.strftime("%b %d", time.strptime(feed_times_display[i].date, "%Y-%m-%d")))
    # update the past feed times global variable
    global pastFeedsString
    pastFeedsString = timesString

def updateUpcomingFeeds(feed_times, timeNow, maxNumDisplay=3):
    # Get the feeding times that precede the current time
    feed_times_past = [ft for ft in feed_times if ft.time < timeNow]
    # Get the feeding times that follow the current time
    feed_times_future = [ft for ft in feed_times if ft.time > timeNow]
    # Show up to 3 feeding times, displaying the feed times after the current time first, then the feed times before the current time
    feed_times_display = feed_times_future[:len(feed_times_future)] + feed_times_past[:len(feed_times_past)]
    timesString = []
    for i in range(min(maxNumDisplay, len(feed_times_display))):
        # Display the time converted from 24 hour format to 12 hour format with AM/PM, but remove leading zero for times before 10
        timesString.append(time.strftime("%l:%M %p", time.strptime(feed_times_display[i].time, "%H:%M")))
    # update the upcoming feed times global variable
    global upcomingFeedsString
    upcomingFeedsString = timesString

def updateUpcomingFeedsPane():
    print("Updating LCD feed times pane")
    global upcomingFeedsString
    paneTextArray = [[' ' for i in range(feeder.display.LCD_WIDTH)] for j in range(feeder.display.LCD_HEIGHT)]
    paneTextArray[0] = "Upcoming Feeds:"
    if len(upcomingFeedsString) > 0:
        for i in range(min(feeder.display.LCD_HEIGHT - 1, len(upcomingFeedsString))):   
            paneTextArray[i + 1] = upcomingFeedsString[i]
    else:
        paneTextArray[1] = "No upcoming feeds"
    feeder.display.updatePane('upcomingFeeds', paneTextArray)
            
def updatePastFeedsPane():
    print("Updating LCD past feeds pane")
    global pastFeedsString
    paneTextArray = [[' ' for i in range(feeder.display.LCD_WIDTH)] for j in range(feeder.display.LCD_HEIGHT)]
    paneTextArray[0] = "Past Feeds:"
    if len(pastFeedsString) > 0:
        for i in range(min(feeder.display.LCD_HEIGHT - 1, len(pastFeedsString))):   
            paneTextArray[i + 1] = pastFeedsString[i]
    else:
        paneTextArray[1] = "No past feeds"
    feeder.display.updatePane('pastFeeds', paneTextArray)
        
def iterateLcdPane():
    print("Iterating LCD pane")
    feeder.display.iteratePanes()
    
manager = TaskManager()
manager.register_task('checkFeedTime', checkFeedTime, FEED_TIME_UPDATE_RATE_SECONDS)
if feeder.hardwareEnabled['display']:
    feeder.display.registerPane('upcomingFeeds', [[' ' for i in range(feeder.display.LCD_WIDTH)] for j in range(feeder.display.LCD_HEIGHT)])
    manager.register_task('updateUpcomingFeedsPane', updateUpcomingFeedsPane, LCD_UPDATE_RATE_SECONDS)
    feeder.display.registerPane('pastFeeds', [[' ' for i in range(feeder.display.LCD_WIDTH)] for j in range(feeder.display.LCD_HEIGHT)])
    manager.register_task('updatePastFeedsPane', updatePastFeedsPane, LCD_UPDATE_RATE_SECONDS)
    manager.register_task('iterateLcdPane', iterateLcdPane, LCD_ITERATE_PANES_RATE_SECONDS)
