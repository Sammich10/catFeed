import os

class BaseConfig(object):
    DEBUG=False
    SECRET_KEY="\xbe\xa0\x9a\xda\xe3\xbdv]'?\xd7S]4uA\x80\xb1v3\xab\xf4s?"
    # Get the path to the database file
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'catFeed.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DB_PATH

