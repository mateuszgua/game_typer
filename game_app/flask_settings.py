import os
from os import environ
from os import path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", default=None)
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    HOST = 'localhost'
    PORT = 9000
    DEBUG = True
    TESTING = True
