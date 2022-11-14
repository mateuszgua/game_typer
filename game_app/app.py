from forms import RegistrationForm, LoginForm
from models import User, Role
from database import db_session, init_db
import os
import uuid
from flask import Flask, render_template, url_for, redirect, request, flash

from flask_settings import Config
from flask_security import Security, hash_password, SQLAlchemySessionUserDatastore, auth_required
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

from flask_bootstrap import Bootstrap5


app = Flask(__name__, instance_relative_config=False)
app.config.from_object('flask_settings.Config')

user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
app.security = Security(app, user_datastore)

bootstrap = Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.route('/home')
def index():
    users = User.query.all()
    return render_template('index.html', users=users, current_user=current_user)


@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 2:
        return render_template('admin.html')
    else:
        flash("Sorry you must be the Admin access the Admin Page.")
        return redirect(url_for('index'))


@app.route('/user/<int:user_id>')
@auth_required
def user(user_id):
    user = User.query.filter_by(id=user_id).first()
    return render_template('user.html', user=user)


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user is None:
            user = User(firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        email=form.email.data,
                        nick=form.nick.data,
                        )
            user.set_password(form.password1.data)
            if user.fs_uniquifier is None:
                user.fs_uniquifier = uuid.uuid4().hex
            db_session.add(user)
            db_session.commit()
            return redirect(url_for('login'))
        flash('A user already exist with that email address.')
    return render_template('register.html', form=form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user', user_id=2))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if user.check_password(password=form.password1.data):
                login_user(user, remember=form.remember.data)

                flash("Login Succesfull!!")

                next = request.args.get('next')
                return redirect(next or (url_for('user', user_id=2)))
            flash("Wrong Password - Try Again!")
        else:
            flash("That User Doesn't Exist! Try Again...")
    return render_template('login.html', form=form)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to view that page.')
    return render_template(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/create', methods=('GET', 'POST'))
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


@app.route('/<int:user_id>/edit', methods=('GET', 'POST'))
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


@app.post('/<int:user_id>/delete')
def delete(user_id):
    user = User.query.get_or_404(user_id)
    db_session.delete(user)
    db_session.commit()

    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(error_description):
    return render_template('404.html', error_description=error_description)


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
