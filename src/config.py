import os

class BaseConfig(object):
    DEBUG=False
    SECRET_KEY="\xbe\xa0\x9a\xda\xe3\xbdv]'?\xd7S]4uA\x80\xb1v3\xab\xf4s?"
    
# Use if install is in /home/pi/catFeed
PROJECT_DIR = os.path.expanduser('~/catFeed')
# Use if install in is /var/www/html/catFeed
# PROJECT_DIR = '/var/www/html/catFeed'
