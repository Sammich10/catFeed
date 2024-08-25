#!/bin/bash

CATFEED_APP_DIR=$(pwd)

chmod 755 $CATFEED_APP_DIR
chmod 755 $CATFEED_APP_DIR/../
chmod 644 $CATFEED_APP_DIR/*
if [ -d $CATFEED_APP_DIR/venv ]; then
    chmod -R 755 $CATFEED_APP_DIR/venv
fi

sudo apt update
sudo apt install apache2 libapache2-mod-wsgi-py3 python3-pip
sudo apt-get install python3-flask -y