import atexit
from crypt import methods
import string
from turtle import delay
from flask import Flask, render_template, Response, request, jsonify, redirect, url_for, session
from functools import wraps
from time import time,sleep
import time
import threading
import os
import sqlite3 as sql
from datetime import datetime, timedelta
from classes.distanceSensor import read_distance
from classes.DCMotor import DCMotor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "catFeed.sqlite3")
dispenser_motor = DCMotor()


def dispenseFood(t):
    dispenser_motor.dispense(t)
    return

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.secret_key = "\xbe\xa0\x9a\xda\xe3\xbdv]'?\xd7S]4uA\x80\xb1v3\xab\xf4s?"

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged-in' in session:
            return f(*args,**kwargs)
        else:
            return redirect(url_for('login'))
    return wrap

@app.route("/",methods=['GET'])
def root():
    if 'logged-in' in session:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))
    return('',404)

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

@app.route("/logout")
@login_required
def logout():
    session.pop('logged-in',None)
    return redirect(url_for('login'))

@app.route("/home", methods=['GET'])
@login_required
def home():
    return render_template('index.html', title="Feed my cat")

@app.route("/viewLog",methods=['GET'])
@login_required
def viewLog():
    try:
        conn=sql.connect(db_path)
        cur=conn.cursor()
        logData = conn.execute('SELECT * FROM feedlog').fetchall()
        conn.close()
        print(logData)
        return render_template('viewLog.html', title="Log View", logData = logData)
    except sql.Error as error:
        print("sqlite error fetching logs")
        print(error)
    return render_template('viewLog.html', title="Log View", logData = None)

@app.route("/manualFeed", methods=['GET','POST'])
def manualFeed():
    if request.method  == 'POST':
        rightnow=datetime.now().strftime("%H:%M")
        date = datetime.now().strftime("%m/%d/%Y")
        temp = request.form.get('timeconst')
        temp = float(temp)
        dispenseFood(temp)
        try:
            conn=sql.connect(db_path)
            cur=conn.cursor()
            cur.execute("INSERT INTO feedlog (time,date,size,type) VALUES (?,?,?,?)",(rightnow,date,'custom','manual'))
            conn.commit()
            conn.close()
            return('',204)
        except sql.Error as error:
            print("sqlite error while updating log")
            print(error)
    return "not a post"

@app.route("/readDistance", methods=['GET'])
def get_dist():
    distance=read_distance()*100
    s = ""
    if(distance<=6 or distance > 1000):
        s="Full"
    elif(distance>6 and distance <=9):
        s="~Half"
    elif(distance>9 and distance<11):
        s="Low"
    elif(distance >=11):
        s="Critical"
    jsonResp={0:s}
    return jsonify(jsonResp)

@app.route("/setTime", methods=['POST'])
def setTime():
    if request.method == 'POST':
        sql_insert_query="""UPDATE feedtimes SET time=?, size=? WHERE id = ?"""
        try:
            conn = sql.connect(db_path)
            cur = conn.cursor()
            data = open(BASE_DIR + "/feedtimes.txt","r").readlines()
            if request.form.get('slot') == '1':
                data[0] = request.form.get('time') + "\n"
                cur.execute(sql_insert_query,(request.form.get('time'), 'r',1))
            elif request.form.get('slot') == '2':
                data[1] = request.form.get('time') + "\n"
                cur.execute(sql_insert_query,(request.form.get('time'), 'r',1))
            conn.commit()
            conn.close()
            with open(BASE_DIR + "/feedtimes.txt","w") as file:
                file.writelines(data)
        except sqlite3.Error as error:
            print("sqlite error updating feed time")
            print(error)
        return('',204)
    return"not a post"
    
@app.route("/getTimes", methods=['GET'])
def getTimes():
    if request.method=='GET':
        feedtimes = []
        feedsfile = open(BASE_DIR + "/feedtimes.txt", "r")
        jsonResp = {}
        i = 1
        for x in feedsfile:
            if x != '\n':
                feedtimes.append(x)
        for y in feedtimes:
            #print(y)
            y = datetime.strptime(y.strip(),"%H:%M").strftime("%I:%M %p")
            jsonResp[i] = y
            i = i + 1
        return jsonify(jsonResp)
    return "not a get"
@app.route("/getLogs", methods=['GET'])

def getLogs():
    return('',204)
    

if __name__ == "__main__":

    app.run(host="0.0.0.0", port = "5000", debug=True)
