from game_app import views, forms
from game_app import models, database, config

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemySessionUserDatastore
from flask_login import LoginManager
from flask_admin import Admin

from flask_bootstrap import Bootstrap5

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, instance_relative_config=False)
app.config.from_object('game_app.config.Config')

admin = Admin(app, 'FlaskApp', url='/home',
              index_view=models.HomeAdminView(name='Home'))

db = SQLAlchemy(app)

user_datastore = SQLAlchemySessionUserDatastore(
    database.db_session, models.User, models.Role)
app.security = Security(app, user_datastore)

bootstrap = Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
