#!/bin/bash

# Update & upgrade the system
sudo apt update;
sudo apt upgrade -y;
# Install python packages
sudo apt install python3 -y;
sudo apt install python3-pip -y;
sudo apt install python3-venv -y;
sudo apt intsall python3-pigpio -y;
sudo apt install python3-smbus2 -y;
sudo apt install python3-rpi.gpio -y;
sudo apt install python3-smbus python3-rpi.gpio i2c-tools -y;
sudo apt install python3-flask -y;
sudo apt install python3-flask-sqlalchemy -y;
sudo apy install python3-flask-migrate -y;
sudo apy install python3-picamera2 -y;
apt-get install libffi-dev
# Install apache
sudo apt install apache2 -y;
# Install sqlite
sudo apt install sqlite3 -y;
# Install git
sudo apt install git -y;

# Start pigpiod
sudo pigpiod;
