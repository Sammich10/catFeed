# Include flask app and database
from app import app, db

# Import the flask app and associated libraries 
from flask import Flask, render_template, Response, request, jsonify, redirect, url_for, session
from functools import wraps

# Import database libraries
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sqlite3 as sql

# Import system libraries
import os
import hashlib
import time
import threading
import cv2
from PIL import Image

# Database models
from app.models import Owner, Feeding, FeedTime
from app import feeder

# Global app runtime variable(s)
camera_mode = 0

def login_required(f):
    """
    Decorator function to check if user is logged in

    Args: 
        f (function): The function to be decorated

    Returns: The decorated function if the user is logged in, otherwise 
    redirects the user to the login page
    """
    @wraps(f)
    def wrap(*args, **kwargs):
        # If the 'logged-in' key is present in the session, allow the decorated function to proceed
        if 'logged-in' in session:
            return f(*args,**kwargs)
        else:
            # If the 'logged-in' key is not present in the session, redirect the user to the login page
            return redirect(url_for('login'), Response=302)
    return wrap


@app.route("/",methods=['GET'])
def root():
    """
    Handles the root route of the application. If the user is logged in,
    redirects them to the home page. Otherwise, redirects them to the login page

    Parameters:
        None

    Returns:
        None

    """
    if 'logged-in' in session:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'), Response=302)

@app.route("/login", methods=['GET','POST'])
def login():
    """
    Handles the login route of the application. If the request method is 'POST',
    it will check the username and password and log the user in. If the request
    method is 'GET', it will render the login page.

    Parameters:
        None

    Returns:
        The rendered login page or a redirect to the home page if the user is
        logged in.

    """
    error=None
    if request.method == 'POST':
        validUser = checkUser(request.form['username'], request.form['password'])
        if validUser:
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged-in'] = True
            session['username'] = request.form['username']
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

def checkUser(username, password):
    """
    Checks if a user with the given username and password exists in the database.

    Parameters:
        username (str): The username of the user to check.
        password (str): The password of the user to check.

    Returns:
        True if the user exists in the database, False otherwise.
    """
    passwordHash = hash_password(password)
    if Owner.query.filter(Owner.username==username, Owner.password==passwordHash).first():
        return True
    return False

@app.route("/register", methods=['GET','POST'])
def register():
    """    
    Handles the registration of a new user. If the request method is 'POST',
    it will add the new user to the database and log them in. If the request
    method is 'GET', it will render the registration page.
    
    Parameters:
        None
    
    Returns:
        The rendered registration page or a redirect to the home page if the
        user is logged in.
    
    errors: 
        None
    """
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        if verify_unique_email(email):
            # Get the username associated with the email 
            username = Owner.query.filter(Owner.email==email).first().username
            resp = {'success': False, 'errors': 'Email already exists.', 'info': {'username': username, 'email': email}}
            return jsonify(resp)
        password = hash_password(request.form['password'])
        add_owner(username, email, password)
        resp = {'success': True, 'errors': None, 'info': None}
        return jsonify(resp)
    return render_template('register.html')

def verify_unique_email(email):
    """
    Checks if an email address already exists in the database
    
    parameters:
        email (str): the email to check
    
    returns:
        True if the email already exists, False otherwise.
    """
    existingOwener = Owner.query.filter(Owner.email==email).first()
    if existingOwener is not None:
        print(existingOwener)
        return True
    return False

def add_owner(username, email, password):
    """
    Adds a new owner entry to the database.

    Parameters:
        username (str): The new owner's username.
        email (str): The new owner's email.
        password (str): The new owner's password.

    Returns:
        None
    """
    new_owner = Owner(username = username, email = email, password = password)
    db.session.add(new_owner)
    db.session.commit()
def hash_password(password):
    """
    Hashes a password with a randomly generated salt.
    Parameters:
        password (str): The password to hash
    
    Returns: 
        The hashed password (bytes)
    """
    salt = os.urandom(16)
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt + hashed_password

def verify_password(stored_hash, provided_password):
    """
    Verifies that the provided password matches the stored hash.
    Parameters:
        stored_hash (bytes): The stored hash of the password.
        provided_password (str): The password to verify.
    
    Returns:
        True if the password matches, False otherwise.
    """
    salt = stored_hash[:16]
    hashed_password = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
    return hashed_password == stored_hash[16:]
    
# Route for logging out
@app.route("/logout")
@login_required
def logout():
    """
    Logs out the user and redirects them to the login page.
    
    Parameters:
        None
    
    Returns:
        A redirect to the login page
    """
    session.pop('logged-in',None)
    return redirect(url_for('login'))

@app.route("/home", methods=['GET'])
@login_required
def home():
    """
    Renders the home page for the user.
    
    Parameters:
        None
    
    Returns:
        The rendered home page
    """
    return render_template('index.html', title="Feed my cat", username=session['username'], version="v2.2.1" )

@app.route("/api/getDistance", methods=['GET'])
@login_required
def getDistance():
    """
    Returns the distance reading from the food distance sensor. If the sensor is not
    initialized or enabled, an error message is returned.
    
    Parameters:
        None
    
    Returns:
        A JSON object containing the distance reading.
    """
    if feeder.foodsens is None or feeder.hardwareEnabled['foodsens'] == False:
        # Return an error message if the food distance sensor is not initialized or not enabled
        return Response("food distance sensor not found", status=500)
    distance_percent = feeder.foodsens.getReading_percent()
    # Round to the nearest 5%
    distance_percent = round(distance_percent/20)*20
    print(distance_percent)
    return jsonify({'distance': distance_percent})

@app.route("/api/getLastFeed", methods=['GET'])
@login_required
def getLastFeed():
    """
    API endpoint to get the last feed recorded in the database.
    
    Parameters:
        None
    
    Returns:
        A JSON object containing the last feed recorded in the database.
    """
    last_feed = Feeding.query.order_by(Feeding.time.desc()).first()
    if last_feed == None:
        last_feed = ""
    else:
        last_feed = (last_feed.time, last_feed.date)
    print(last_feed)
    return jsonify({'last_feed': last_feed})


@app.route("/api/getFeedingTimes", methods=['GET'])
@login_required
def getFeedingTimes():
    """
    API endpoint to get all feeding times recorded in the database.
    
    Parameters:
        None
    
    Returns:
        A JSON object containing all feeding times recorded in the database.
    """
    # Get all recorded  from the database, order by date first then time.
    feeding_times = Feeding.query.order_by(Feeding.date, Feeding.time).all()
    feeding_times_list = []
    # Convert the feeding times to a list of tuples
    for feeding_time in feeding_times:
        feeding_times_list.append((feeding_time.date, feeding_time.time, feeding_time.type, feeding_time.size)) 
    # Return a JSON object containing the list of feeding times
    return jsonify({'feeding_times': feeding_times_list})

@app.route("/api/getFeedTimes", methods=['GET'])
@login_required
def getFeedTimes():
    """
    API endpoint to get all scheduled feed times that currently exist in the database.
    
    Parameters:
        None
        
    Returns:
        A JSON object containing all scheduled feed times that currently exist in the database
    """
    feed_times = FeedTime.query.all()
    feed_times_list = []
    for feed_time in feed_times:
        feed_times_list.append((feed_time.time, feed_time.type, feed_time.size))
    print(feed_times_list)
    return jsonify({'feed_times': feed_times_list})

@app.route("/api/videoFeed")
@login_required
def videoFeed():
    """
    API endpoint to start the live video feed.
    
    Parameters:
        None
    
    Returns:
        A response object containing the live video feed.
    """
    print("Starting live video feed")
    if feeder.picam is None:
        # Return an error message
        return Response("camera not found", status=500)
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Initialize camera using libcamera (OpenCV interface)

def processFrame(frame_raw, setting):
    """
    Processes the raw frame and returns the processed frame.
    
    Parameters:
        frame_raw: the raw frame
        setting: the processing setting
        
    Returns:
        the processed frame
    """
    if setting == 0:
        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame_raw, cv2.COLOR_BGR2GRAY)
        return gray 
    if setting == 1:
        # Convert the frame to YUV
        frame_yuv = cv2.cvtColor(frame_raw, cv2.COLOR_BGR2YUV)
        frame_y = frame_yuv[:, :, 0]
        frame_y_bilateral = cv2.bilateralFilter(frame_y, 5, 150, 150)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        frame_processed = clahe.apply(frame_y_bilateral)
        return frame_processed
    if setting == 2:
        # Convert the frame to RGB
        rgb = cv2.cvtColor(frame_raw, cv2.COLOR_BGR2RGB)
        return rgb

def gen_frames():
    """
    Generates frames for the live video feed.
    
    Parameters:
        None
    
    Returns:
        A response object containing the live video feed.
    """
    global camera_mode
    try:
        # Start the camera feed
        while True:
            # Capture the raw frame from the Pi Camera
            frame_raw = feeder.picam.camera.capture_array()
            # TODO: Configurable rotation
            frame_raw = cv2.flip(frame_raw, 0)
            # Perform processing
            frame_processed = processFrame(frame_raw, camera_mode)
            # Convert the processed and rotated frame to a JPEG image
            _, jpeg = cv2.imencode('.jpg', frame_processed)
            # Convert the JPEG image to bytes
            frame = jpeg.tobytes()
            # Yield the frame in MJPEG format
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except Exception as e:
        print(e)

@app.route("/api/manualFeed", methods=['POST'])
@login_required
def manualFeed():
    """
    API endpoint to manually trigger a feeding.
    
    Parameters:
        None
    
    Returns:
        A response object containing the result of the manual feed.
    """
    if request.method == 'POST':
        if feeder.motor is None:
            # Return an error message
            return Response("motor not found", status=500)
        # Parse the JSON response
        data = request.get_json()
        print(data)
        # Get the time and type from the JSON response
        size = data['size']
        if size is None:
            return Response("error, no size parameter for manual feed", status=500)
        sizeInt = int(size)
        # If the display is not found, still run the motor
        if feeder.display is not None:
            # Run the display routine in a separate thread
            t2 = threading.Thread(target=feeder.display.feedTimeDisplayRoutine, args=(sizeInt*3,)).start()
        # Run the motor in a separate thread and return a success response immediately
        t1 = threading.Thread(target=feeder.motor.forward, args=(sizeInt*3,)).start()
        # Add the feed record to the database
        new_feeding = Feeding(time = time.strftime("%H:%M"), type = 0, date = time.strftime("%Y-%m-%d"), size = sizeInt)
        db.session.add(new_feeding)
        db.session.commit()
        return Response("Success", status=200)
    else:
        return Response("Error", status=500)
    
@app.route("/api/toggleCamera", methods=['POST'])
@login_required
def toggleCamera():
    """
    API endpoint to toggle the camera mode.
    
    Parameters:
        None
    
    Returns:
        A response object containing the result of the camera toggle.
    """
    if request.method == 'POST':
        if feeder.picam is None:
            # Return an error message
            return Response("camera not found", status=500)
        global camera_mode
        if camera_mode + 1 > 2:
            camera_mode = 0
        else:
            camera_mode += 1
        print(camera_mode)
        return Response("Success", status=200)
    else:
        return Response("Error", status=500)

@app.route("/api/addFeedTime", methods=['POST'])
@login_required
def addFeedTime():
    """
    API endpoint to add a feed time to the database.
    
    Parameters:
        None
    
    Returns:
        A response object containing the result of the feed time addition.
    """
    if request.method == 'POST':
        # Parse the JSON response
        data = request.get_json()
        print(data)
        # Get the time and type from the JSON response
        timeStr = data['time']
        if time is None:
            return Response("error, no time parameter", status=500)
        type = data['type']
        if type is None:
            return Response("error, no type parameter", status=500)
        typeInt = int(type)
        size = data['size']
        if size is None:
            return Response("error, no size parameter", status=500)
        sizeInt = int(size)
        # Add the feed time record to the database
        new_feedtime = FeedTime(time = timeStr, type = typeInt, size = sizeInt)
        db.session.add(new_feedtime)
        db.session.commit()
        return Response("Success", status=200)
    
@app.route("/api/deleteFeedTime", methods=['POST'])
@login_required
def deleteFeedTime():
    """
    API endpoint to delete a feed time from the database.
    
    Parameters:
        None
    
    Returns:
        A response object containing the result of the feed time deletion.
    """
    if request.method == 'POST':
        # Parse the JSON response
        data = request.get_json()
        print(data)
        # Get the time and type from the JSON response
        timeStr = data['time']
        if time is None:
            return Response("Error", status=500)
        # Delete the feed time record from the database
        feedtime = FeedTime.query.filter_by(time = timeStr).first()
        db.session.delete(feedtime)
        db.session.commit()
        return Response("Success", status=200)
    

