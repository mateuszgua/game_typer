from database import Base

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, DateTime, Column, Integer, String, ForeignKey, UnicodeText
from flask_security import UserMixin, RoleMixin
from werkzeug.security import generate_password_hash, check_password_hash


class RolesUsers(Base):
    __tablename__ = 'roles_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    role_id = Column('role_id', Integer(), ForeignKey('role.id'))


class Role(Base, RoleMixin):
    __tablename__ = 'role'
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))
    permissions = Column(UnicodeText)


class User(Base, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    firstname = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    password_hash = Column(String(100), nullable=False)
    nick = Column(String(100), unique=True)
    email = Column(String(100), nullable=False, unique=True)
    active = Column(Boolean())
    fs_uniquifier = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    roles = relationship('Role', secondary='roles_users',
                         backref=backref('users', lazy='dynamic'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)