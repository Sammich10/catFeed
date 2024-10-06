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
# Decorator function to check if user is logged in by the presence of the 'logged-in' key in the session
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        # If the 'logged-in' key is present in the session, allow the decorated function to proceed
        if 'logged-in' in session:
            return f(*args,**kwargs)
        else:
            # If the 'logged-in' key is not present in the session, redirect the user to the login page
            return redirect(url_for('login'), Response=302)
    return wrap

# Route for the home page
@app.route("/",methods=['GET'])
def root():
    if 'logged-in' in session:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'), Response=302)

@app.route("/login", methods=['GET','POST'])
def login():
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
    passwordHash = hash_password(password)
    if Owner.query.filter(Owner.username==username, Owner.password==passwordHash).first():
        return True
    return False
    
# Handles the registration of a new user. If the request method is 'POST',
# it will add the new user to the database and log them in. If the request
# method is 'GET', it will render the registration page.

# Parameters:
# None

# Returns:
# The rendered registration page or a redirect to the home page if the
# user is logged in.
# errors = None
@app.route("/register", methods=['GET','POST'])
def register():
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

# Checks if an email already exists in the database.

# Parameters:
# email (str): The email to check.

# Returns:
# True if the email already exists, False otherwise.
def verify_unique_email(email):
    # Check if email already exists in the database
    existingOwener = Owner.query.filter(Owner.email==email).first()
    if existingOwener is not None:
        print(existingOwener)
        return True
    return False

# Adds a new owner to the database.

# Parameters:
# username (str): The new owner's username.
# email (str): The new owner's email.
# password (str): The new owner's password.

# Returns:
# None
def add_owner(username, email, password):
    new_owner = Owner(username = username, email = email, password = password)
    db.session.add(new_owner)
    db.session.commit()

# Hashes a password with a randomly generated salt.

# :param password: The password to hash
# :type password: str
# :return: The hashed password
# :rtype: bytes
def hash_password(password):
    salt = os.urandom(16)
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt + hashed_password

def verify_password(stored_hash, provided_password):
    salt = stored_hash[:16]
    hashed_password = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
    return hashed_password == stored_hash[16:]
    
# Route for logging out
@app.route("/logout")
@login_required
def logout():
    session.pop('logged-in',None)
    return redirect(url_for('login'))

@app.route("/home", methods=['GET'])
@login_required
def home():
    return render_template('index.html', title="Feed my cat", username=session['username'], version="v2.2.1" )

@app.route("/api/getDistance", methods=['GET'])
@login_required
def getDistance():
    if feeder.foodsens is None:
        # Return an error message
        return Response("food distance sensor not found", status=500)
    distance_percent = feeder.foodsens.getReading_percent()
    # Round to the nearest 5%
    distance_percent = round(distance_percent/20)*20
    print(distance_percent)
    return jsonify({'distance': distance_percent})

@app.route("/api/getLastFeed", methods=['GET'])
@login_required
def getLastFeed():
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
    # Get all recorded feeds, order by date first then time. Sort by newest to oldest
    feeding_times = Feeding.query.order_by(Feeding.date, Feeding.time).all()
    feeding_times_list = []
    for feeding_time in feeding_times:
        feeding_times_list.append((feeding_time.date, feeding_time.time, feeding_time.type, feeding_time.size)) 
    print(feeding_times_list)
    return jsonify({'feeding_times': feeding_times_list})

@app.route("/api/getFeedTimes", methods=['GET'])
@login_required
def getFeedTimes():
    feed_times = FeedTime.query.all()
    feed_times_list = []
    for feed_time in feed_times:
        feed_times_list.append((feed_time.time, feed_time.type, feed_time.size))
    print(feed_times_list)
    return jsonify({'feed_times': feed_times_list})

@app.route("/api/videoFeed")
@login_required
def videoFeed():
    print("Starting live video feed")
    if feeder.picam is None:
        # Return an error message
        return Response("camera not found", status=500)
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Initialize camera using libcamera (OpenCV interface)

def gen_frames():
    try:
        while True:
            frame = feeder.picam.camera.capture_array()
            # TODO: Configurable rotation
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            # Convert the rotated frame to a JPEG image
            _, jpeg = cv2.imencode('.jpg', frame)
            frame = jpeg.tobytes()

            # Yield the frame in MJPEG format
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except Exception as e:
        print(e)

@app.route("/api/manualFeed", methods=['POST'])
@login_required
def manualFeed():
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
        new_feeding = Feeding(time = time.strftime("%H:%M:%S"), type = 0, date = time.strftime("%Y-%m-%d"), size = sizeInt)
        db.session.add(new_feeding)
        db.session.commit()
        return Response("success", status=200)
    else:
        return Response("error", status=500)
    
@app.route("/api/addFeedTime", methods=['POST'])
@login_required
def addFeedTime():
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
        return Response("success", status=200)
    
@app.route("/api/deleteFeedTime", methods=['POST'])
@login_required
def deleteFeedTime():
    if request.method == 'POST':
        # Parse the JSON response
        data = request.get_json()
        print(data)
        # Get the time and type from the JSON response
        timeStr = data['time']
        if time is None:
            return Response("error", status=500)
        # Delete the feed time record from the database
        feedtime = FeedTime.query.filter_by(time = timeStr).first()
        db.session.delete(feedtime)
        db.session.commit()
        return Response("success", status=200)
    

