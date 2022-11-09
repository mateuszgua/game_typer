import os
from flask import Flask, render_template, url_for, redirect, request, flash

from flask_settings import Config
from flask_security import Security, hash_password, SQLAlchemySessionUserDatastore
from flask_login import LoginManager, login_user, current_user, logout_user

from database import db_session, init_db
from models import User, Role
from forms import RegistrationForm, LoginForm

app = Flask(__name__, instance_relative_config=False)
app.config.from_object('flask_settings.Config')
#app.config['SQLALCHEMY_DATABASE_URI'] = url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get(
    "SECURITY_PASSWORD_SALT", '146585145368132386173505678016728509634')
#db = SQLAlchemy(app)

user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
app.security = Security(app, user_datastore)


@app.route('/home/')
# @auth_required()
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


@app.route('/<int:user_id>/')
def user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user.html', user=user)


@app.route('/register/', methods=('GET', 'POST'))
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(firstname=form.firstname.data,
                    lastname=form.lastname.data,
                    email=form.email.data,
                    nick=form.nick.data,
                    )
        user.set_password(form.password1.data)
        db_session.add(user)
        db_session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login/', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password1.data):
            login_user(user)

            flash('Loged in successfully.')

            next = request.args.get('next')
            return redirect(next or url_for('index'))
        flash('Invalid login or password!')
    return render_template('login.html', form=form)


@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        password = request.form['password']
        email = request.form['email']
        nick = request.form['nick']
        user = User(firstname=firstname,
                    lastname=lastname,
                    password=password,
                    email=email,
                    nick=nick)
        db_session.add(user)
        db_session.commit()

    return render_template('create.html')


@app.route('/<int:user_id>/edit/', methods=('GET', 'POST'))
def edit(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        password = request.form['password']
        email = request.form['email']
        nick = request.form['nick']

        user.firstname = firstname
        user.lastname = lastname
        user.password = password
        user.email = email
        user.nick = nick

        db_session.add(user)
        db_session.commit()

        return redirect(url_for('index'))

    return render_template('edit.html', user=user)


@app.post('/<int:user_id>/delete/')
def delete(user_id):
    user = User.query.get_or_404(user_id)
    db_session.delete(user)
    db_session.commit()

    return redirect(url_for('index'))


if __name__ == '__main__':
    config = Config()
    with app.app_context():
        init_db()
        if not app.security.datastore.find_user(email="test@me.com"):
            app.security.datastore.create_user(
                firstname='Jan',
                lastname='Kowalski',
                email="test@me.com",
                password_hash=hash_password("password_hash"))
        db_session.commit()
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
