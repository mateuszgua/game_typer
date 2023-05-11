from app import models, database, config

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemySessionUserDatastore
from flask_login import LoginManager
from flask_admin import Admin

from flask_bootstrap import Bootstrap5

basedir = os.path.abspath(os.path.dirname(__file__))

application = Flask(__name__, instance_relative_config=False)

if application.config["ENV"] == "production":
    application.config.from_object('app.config.ProductionConfig')
elif application.config["ENV"] == "testing":
    application.config.from_object('app.config.TestingConfig')
else:
    application.config.from_object('app.config.DevelopmentConfig')

admin = Admin(application, 'FlaskApp', url='/home',
              index_view=models.HomeAdminView(name='Home'))

db = SQLAlchemy(application)

user_datastore = SQLAlchemySessionUserDatastore(
    database.db_session, models.User, models.Role)
# app.security = Security(app, user_datastore)

bootstrap = Bootstrap5(application)

login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'login'

from app import views, forms