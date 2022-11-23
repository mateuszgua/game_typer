from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, TimeField
from wtforms.validators import DataRequired, Email, EqualTo


class RegistrationForm(FlaskForm):
    firstname = StringField('Firstname', validators=[DataRequired()])
    lastname = StringField('Lastname', validators=[DataRequired()])
    password1 = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[
                              DataRequired(), EqualTo('password1')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    nick = StringField('Nick', validators=[DataRequired()])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password1 = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class EditUserForm(FlaskForm):
    firstname = StringField('Firstname', validators=[DataRequired()])
    lastname = StringField('Lastname', validators=[DataRequired()])
    password1 = PasswordField('Password')
    password2 = PasswordField('Confirm Password', validators=[
                              DataRequired(), EqualTo('password1')])
    nick = StringField('Nick', validators=[DataRequired()])
    submit = SubmitField('Change')


class AddGameForm(FlaskForm):
    game_teams = StringField('Team')
    team_1 = StringField('Team 1')
    team_2 = StringField('Team 2')
    game_day = DateField('Date')
    game_time = TimeField('Time')
    submit = SubmitField('Add')