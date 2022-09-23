# Automated Cat Feeder Using Raspberry Pi and Flask
> Automatically feed your cat, schedule up to 3 daily feeds, and track feedings over time!
> Live demo [_here_](https://www.sammichelsen.tech).

## Table of Contents
* [General Info](#general-information)
* [Technologies Used](#technologies-used)
* [Features](#features)
* [Setup/Usage](#setup)
* [Project Status](#project-status)
* [Improvements](#room-for-improvement)


## General Information
This project was originally born as a group project for an embedded systems class, and after the semester ended I decided to try and build a new one that I could keep and actually use to feed my two cats. 


## Technologies Used
- Flask web application framework
- Apache HTTP server
- SQLite3 Database
- Raspberry Pi GPIO


## Features
- Simple, user friendly web application UI to program the feeder and check its status
- Schedule up to 3 daily feeds
- Trigger a manual feed
- Track feeds 
- View scheduled feeds and the status of the food hopper on LCD screen


## Setup/Usage
The files for this project are located in the /var/www/html/catFeed folder on the raspberry pi.
In order to get the project up and running, you must first clone the repository onto a Raspberry Pi. You will need to make sure 
you have installed Python, Flask, Apache, SQLite3, and pigpio. Configure Apache2 to work with Flask, and go into your Pi's /etc/rc.local file
and add a line that runs the update.py file on boot.


## Project Status
The project as it stands is fully functional, and I would consider it to be in a decent 1.0 state. I do plan to add more features in time
_in progress_



## Room for Improvement
- Add a way to set the size of automated feeds. As of now their all "regular" size feeds by default.