from forms import RegistrationForm, LoginForm, EditUserForm
from models import User, Role, UserAdminView, RoleAdminView, HomeAdminView
from database import db_session, init_db

import uuid
from flask import Flask, render_template, url_for, redirect, request, flash, session

from flask_settings import Config
from flask_security import Security, hash_password, SQLAlchemySessionUserDatastore
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_admin import Admin

from flask_bootstrap import Bootstrap5


app = Flask(__name__, instance_relative_config=False)
app.config.from_object('flask_settings.Config')

admin = Admin(app, 'FlaskApp', url='/home',
              index_view=HomeAdminView(name='Home'))


admin.add_view(UserAdminView(User, db_session))
admin.add_view(RoleAdminView(Role, db_session))

user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
app.security = Security(app, user_datastore)

bootstrap = Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/home')
def home():
    users = User.query.all()
    return render_template('home.html', users=users, current_user=current_user)


@app.route('/user/<int:user_id>')
def user(user_id):
    user = User.query.filter_by(id=user_id).first()
    # delete
    user_id1 = User.query.get(int(user_id))
    print(user_id1)
    print(f"To jest user: %s", current_user.is_authenticated)
    print(f"To jest user: %s", session.get('id'))
    print(user_id)
    print(current_user.get_id())

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
        return redirect(url_for('user', user_id=user.id))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if user.check_password(password=form.password1.data):
                login_user(user, remember=form.remember.data)
                next = request.args.get('next')
                return redirect(next or (url_for('user', user_id=user.id)))
            flash("Wrong Password - Try Again!")
        else:
            flash("That User Doesn't Exist! Try Again...")
    return render_template('login.html', form=form)


@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to view that page.')
    return redirect(url_for('login'))


@app.route('/logout', methods=('GET', 'POST'))
@login_required
def logout():
    session.clear()
    logout_user()
    flash("You have been logged out!")
    return redirect(url_for('login', next=request.url))


@app.route('/edit/<int:user_id>', methods=('GET', 'POST'))
def edit(user_id):
    form = EditUserForm()
    user = User.query.filter_by(id=user_id).first()

    # To delete
    print(f"To jest user: %s", current_user.is_authenticated)
    print(f"To jest user: %s", session.get('id'))
    print(user_id)
    print(current_user.get_id())

    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        password = request.form['password']
        email = request.form['email']
        nick = request.form['nick']

        try:
            user.firstname = firstname
            user.lastname = lastname
            user.password = password
            user.email = email
            user.nick = nick

            db_session.commit()
            flash("User updated successfully!")
            return render_template('edit.html', form=form, user=user, id=user_id)
        except:
            flash("Error! There was a problem edit user... try again.")
            return render_template('edit.html', form=form, user=user, id=user_id)
    else:
        return render_template('edit.html', form=form, user=user, id=user_id)


@app.post('/delete/<int:user_id>')
def delete(user_id):
    # delete
    print(user_id)
    print(current_user.get_id())

    if user_id == current_user.get_id():
        user = User.query.filter_by(id=user_id).first()
        form = RegistrationForm()

        try:
            db_session.delete(user)
            db_session.commit()
            flash("User deleted successfully!")
            return render_template('register.html', form=form)

        except:
            flash("Whoops! There was a problem deleting user, try again...")

    else:
        flash("Sorry, you can't delete that user!")
        return redirect(url_for('home'))


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
