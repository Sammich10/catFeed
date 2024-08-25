from appMain import app, db
from flask import Flask, render_template, Response, request, jsonify, redirect, url_for, session
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
import sqlite3 as sql
import time
import threading
import os
import sys
from crypt import methods
import atexit
from classes.models import Owner

# Decorator function to check if user is logged in by the presence of the 'logged-in' key in the session
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        # If the 'logged-in' key is present in the session, allow the decorated function to proceed
        if 'logged-in' in session:
            return f(*args,**kwargs)
        else:
            # If the 'logged-in' key is not present in the session, redirect the user to the login page
            return redirect(url_for('login'))
    return wrap

# Route for the home page
@app.route("/",methods=['GET'])
def root():
    if 'logged-in' in session:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))
    return('',404)

@app.route("/registerNewOwner", methods=['GET','POST'])
def registerOwner():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
    return render_template('registerOwner.html', error=error)

def add_owner(username, password):
    new_owner = Owner(username = username, password = password)
    db.session.add(new_owner)
    db.session.commit()

# Route for the login page
@app.route("/login", methods=['GET','POST'])
def login():
    error=None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged-in'] = True
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route("/register")
def register():
    return render_template('register.html')
# Route for logging out
@app.route("/logout")
@login_required
def logout():
    session.pop('logged-in',None)
    return redirect(url_for('login'))



@app.route("/home", methods=['GET'])
@login_required
def home():
    return render_template('index.html', title="Feed my cat")

