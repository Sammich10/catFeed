#!/bin/bash

sudo apt update;
sudo apt upgrade -y;

sudo apt install python3 -y;
sudo apt install python3-pip -y;
sudo apt install python3-venv -y;
sudo apt intsall python3-pigpio -y;

sudo apt install python3-RPi.GPIO -y;
sudo apt install python3-smbus2 -y;
sudo apt install python3-rpi.gpio -y;
sudo apt install python3-smbus python3-rpi.gpio i2c-tools -y;
sudo apt install python3-flask-sqlalchemy -y;
sudo apy install python3-flask-migrate -y;
pip install RPLCD --break-system-packages -y;
apt-get install libffi-dev

sudo apt install apache2 -y;
sudo apt install sqlite3 -y;
sudo apt install git -y;

# Start pigpiod
sudo pigpiod;
