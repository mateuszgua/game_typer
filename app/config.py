import os
from os import path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))

load_dotenv(path.join(basedir, '.env'))

USERNAME = os.getenv('MYSQL_USERNAME')
PASSWORD = os.getenv('MYSQL_PASSWORD')
HOST = os.getenv('MYSQL_HOST')
DB_NAME = os.getenv('MYSQL_DB_NAME')
TABLE_NAME = os.getenv('MYSQL_TABLE_NAME')
url = f"mysql+mysqlconnector://{USERNAME}:{PASSWORD}@{HOST}/{DB_NAME}"

print(url)

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", default=None)
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT")
    SECURITY_PASSWORD_HASH = 'sha512_crypt'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = url

    STATIC_FOLDER = 'static'
    UPLOAD_FOLDER = 'app/static/files'
    IMG_FOLDER = os.path.join('static', 'files')
    ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'json'}
    TEMPLATES_FOLDER = 'templates'

    ENV = os.getenv('ENV')
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = False
    TESTING = False

    SESSION_COOKIE_SECURE = True


class ProductionConfig(Config):
    pass


class TestingConfig(Config):
    DEBUG = True
    TESTING = True

    SESSION_COOKIE_SECURE = False


class DevelopmentConfig(Config):
    DEBUG = True

    SESSION_COOKIE_SECURE = False
