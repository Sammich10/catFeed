# Include flask app and database
from appMain import app, db
# Import the flask app and associated libraries 
from flask import Flask, render_template, Response, request, jsonify, redirect, url_for, session
from functools import wraps
# Import database libraries
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sqlite3 as sql
# Import system libraries
import os
import sys
import hashlib
import time
import threading
import atexit
# Database models
from classes.models import Owner
# Cat feeder control classes
from appMain.feederControl import lcd
from appMain.feederControl import motor
from appMain.feederControl import dsens

# Decorator function to check if user is logged in by the presence of the 'logged-in' key in the session
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        # If the 'logged-in' key is present in the session, allow the decorated function to proceed
        if 'logged-in' in session:
            return f(*args,**kwargs)
        else:
            # If the 'logged-in' key is not present in the session, redirect the user to the login page
            return redirect(url_for('login'), Response=302, message="You need to login first")
    return wrap

# Route for the home page
@app.route("/",methods=['GET'])
def root():
    if 'logged-in' in session:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'), Response=302, message="Please login")

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
            return render_template('register.html', error="Email already exists")
        password = hash_password(request.form['password'])
        add_owner(username, email, password)
        return redirect(url_for('login'))
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
    return render_template('index.html', title="Feed my cat", username=session['username'], last_feed="Unknown", food_remaining_percennt="0%", version="v2.2.1" )

@app.route("/api/getDistance", methods=['GET'])
def getDistance():
    distance_percent = dsens.getReading_percent()
    return jsonify({'distance': distance_percent})

