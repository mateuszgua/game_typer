from game_app import database

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, DateTime, Column, Integer, String, ForeignKey, UnicodeText, LargeBinary, Date, Time
from flask import redirect, url_for, request
from flask_security import UserMixin, RoleMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user

from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView


class RolesUsers(database.Base):
    __tablename__ = 'roles_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    role_id = Column('role_id', Integer(), ForeignKey('role.id'))


class Role(database.Base, RoleMixin):
    __tablename__ = 'role'
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))
    permissions = Column(UnicodeText)


class User(UserMixin, database.Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    firstname = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    password_hash = Column(String(200), nullable=False)
    nick = Column(String(100), unique=True)
    email = Column(String(100), nullable=False, unique=True)
    active = Column(Boolean())
    fs_uniquifier = Column(String(255), unique=True, nullable=False)
    authenticated = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    roles = relationship('Role', secondary='roles_users',
                         backref=backref('users', lazy='dynamic'))
    # types = relationship('Type', secondary='user_type',
    #  backref=backref('users', lazy='dynamic'))
    types = relationship('Type', backref='user')
    points = Column(Integer)

    def __repr__(self) -> str:
        return str(self.id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='sha512')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_active(self):
        return True

    def get_id(self):
        return self.email

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False


class AdminMixin:
    def is_accessible(self):
        return current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('login', next=request.url))


class AdminView(AdminMixin, ModelView):
    pass


class HomeAdminView(AdminMixin, AdminIndexView):
    pass


class BaseModelView(ModelView):
    def on_model_change(self, form, model, is_created):
        if is_created:
            model.generate_slug()
        return super().on_model_change(form, model, is_created)


class RoleAdminView(AdminMixin, BaseModelView):
    pass


class UserAdminView(AdminMixin, BaseModelView):
    pass


class Team(database.Base):
    __tablename__ = 'team'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    games_played = Column(Integer, nullable=False)
    wins = Column(Integer, nullable=False)
    draws = Column(Integer, nullable=False)
    lost = Column(Integer, nullable=False)
    goal_scored = Column(Integer, nullable=False)
    goal_lost = Column(Integer, nullable=False)
    goal_balance = Column(Integer, nullable=False)
    points = Column(Integer, nullable=False)
    group = Column(String(100), nullable=False)
    play_off = Column(Integer, nullable=False)
    image_name = Column(String(100), nullable=False)

    def __repr__(self) -> str:
        return self.name


class UploadFile(database.Base):
    __tablename__ = 'file'
    id = Column(Integer, primary_key=True)
    filename = Column(String(100))
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    data = Column(LargeBinary)


# class UserType(database.Base):
    # __tablename__ = 'user_type'
    # id = Column(Integer(), primary_key=True)
    # user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    # type_id = Column('type_id', Integer(), ForeignKey('type.id'))


class Type(database.Base):
    __tablename__ = 'type'
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer)
    tournament = Column(String(20))
    type_goals_team_1 = Column(Integer)
    type_goals_team_2 = Column(Integer)
    type_points = Column(Integer)
    user_id = Column(Integer, ForeignKey('user.id'))


class Game(database.Base):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True)
    game_discipline = Column(String(20))
    tournament = Column(String(20))
    team_1 = Column(String(20))
    team_2 = Column(String(20))
    game_day = Column(Date(), nullable=False)
    game_time = Column(Time(), nullable=False)
    goals_team_1 = Column(Integer)
    goals_team_2 = Column(Integer)
    game_phase = Column(String(30))
    result = Column(String(10))
