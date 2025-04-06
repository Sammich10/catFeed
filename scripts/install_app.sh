#!/bin/bash

# Check if the script is being run as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script as root or with sudo privileges."
    exit 1
fi

# Check if the installation directory is provided
if [ -z "$1" ]; then
    echo "Please provide the installation directory as an argument."
    exit 1
fi

# Get the installation directory
APP_INSTALL_DIR=$1

# Create the installation directory if it doesn't exist
mkdir -p $APP_INSTALL_DIR

# Verify that python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "python3 is not installed. Please install python3 and try again."
    exit 1
fi

# Verify that pip3 is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install pip3 and try again."
    exit 1
fi

# Verify that python venv is installed
if ! command -v python3-venv &> /dev/null; then
    echo "python3-venv is not installed. Please install python3-venv and try again."
    exit 1
fi

echo "Application will be installed in $APP_INSTALL_DIR"
# Create the python virtual environment and activate it
python3 -m venv ${APP_INSTALL_DIR}/.venv;
source ${APP_INSTALL_DIR}/.venv/bin/activate;
cd $APP_INSTALL_DIR;

# Install system dependencies
echo "Installing system dependencies"
sudo apt install libcamera-dev libffi-dev libcap-dev libkms++-dev libfmt-dev libdrm-dev -y;

# Install network dependencies
echo "Installing network dependencies"
# Install apache
sudo apt install apache2 sqlite3 -y;

# Install python dependencies
echo "Installing python dependencies"
pip3 install -r modules.toml;

# Start pigpiod
sudo pigpiod;
