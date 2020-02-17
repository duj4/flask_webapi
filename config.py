import os
import sys

DEBUG = True
HOST = '0.0.0.0'
PORT = '5000'

# SQLite URI
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

dev_db = prefix + os.path.join(os.path.dirname(os.path.abspath('app3.py')), 'data.db')
SECRET_KEY = 'the quick brown fox jumps over the lazy dog'
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', dev_db)
SQLALCHEMY_TRACK_MODIFICATIONS = False
