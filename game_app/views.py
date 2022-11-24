from game_app import app, login_manager, admin
from game_app.forms import RegistrationForm, LoginForm, EditUserForm, AddGameForm
from game_app.models import User, Role, Team, UserAdminView, RoleAdminView, UploadFile, Game, UserType
from game_app.database import db_session
from game_app.config import Config

import os
import uuid
from flask import render_template, url_for, redirect, request, flash, session, json
from flask_login import login_user, current_user, logout_user, login_required

from werkzeug.utils import secure_filename


config = Config()

admin.add_view(UserAdminView(User, db_session))
admin.add_view(RoleAdminView(Role, db_session))
admin.add_view(RoleAdminView(Game, db_session))
admin.add_view(RoleAdminView(UserType, db_session))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to view that page.')
    return redirect(url_for('login'))


@app.route('/home')
def home():
    teams = Team.query.all()
    IMG_LIST = os.listdir('game_app/static/files')
    IMG_LIST = ['files/' + i for i in IMG_LIST]
    print(IMG_LIST)
    return render_template('index.html', teams=teams, current_user=current_user, image_list=IMG_LIST)


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

    return render_template('accounts/user.html', user=user)


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
    return render_template('accounts/register.html', form=form)


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
    return render_template('accounts/login.html', form=form)


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
            return render_template('accounts/edit.html', form=form, user=user, id=user_id)
        except:
            flash("Error! There was a problem edit user... try again.")
            return render_template('accounts/edit.html', form=form, user=user, id=user_id)
    else:
        return render_template('accounts/edit.html', form=form, user=user, id=user_id)


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
            return render_template('accounts/register.html', form=form)

        except:
            flash("Whoops! There was a problem deleting user, try again...")

    else:
        flash("Sorry, you can't delete that user!")
        return redirect(url_for('home'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


@app.route('/admin/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            flash("No selected file")
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(config.UPLOAD_FOLDER, filename))
            upload = UploadFile(filename=file.filename, data=file.read())
            db_session.add(upload)
            db_session.commit()
            flash(f"Uploaded: {file.filename}")
    return render_template('loadfile.html')


@app.route('/admin/select_file', methods=['GET', 'POST'])
def select_file():
    files = UploadFile.query.all()
    if request.method == 'POST':
        if request.form.get('mycheckbox') != None:
            file_idx = request.form.get('mycheckbox')
            processjson(file_idx)
            flash(f"Load successfully!")
        else:
            flash(f"Please chose one.")
    return render_template('selectfile.html', files=files)


def processjson(file_idx):
    file = UploadFile.query.filter_by(id=file_idx).first()
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static/files", file.filename)
    data = json.load(open(json_url))
    
    i = 0
    while i < 32 : 
        team = Team(name=data['team'][i]['name'],
                       games_played=0,
                       wins=0,
                       draws=0,
                       lost=0,
                       goal_scored=0,
                       goal_lost=0,
                       goal_balance=0,
                       points=0,
                       group=data['team'][i]['group'],
                       play_off=0,
                       image_name=f"files/{data['team'][i]['name']}_48x48.png"
                       )
        db_session.add(team)
        db_session.commit()
        i += 1


@app.route('/admin/games', methods=['GET', 'POST'])
def games():
    games = Game.query.all()
    teams = Team.query.all()
    form = AddGameForm()
    if form.validate_on_submit():
        existing_game = Game.query.filter_by(game_teams=form.game_teams.data).first()
        if existing_game is not None:
            game = Game(game_teams=form.game_teams.data,
                        team_1=form.team_1.data,
                        team_2=form.team_2.data,
                        game_day=form.game_day.data,
                        game_time=form.game_time.data,
                        )
            db_session.add(game)
            db_session.commit()
            flash('Add game successfully.')
        flash('Whoops! There was a problem!')
    return render_template('gameslist.html', teams=teams, games=games, form=form)

    
@app.route('/admin/game_edit', methods=['GET', 'POST'])
def game_edit():
    games = Game.query.all()
    
    if request.method == 'POST':
        game = Game.query.filter_by(id=request.form['action']).first()
        team1 = request.form.get('team1')
        team2 = request.form.get('team2')
        
        try:
            game.goals_team_1 = team1
            game.goals_team_2 = team2

            db_session.commit()
            flash("Game updated successfully!")
            return render_template('gamesedit.html', games=games)
        except:
            flash("Error! There was a problem edit game... try again.")
    return render_template('gamesedit.html', games=games)


@app.post('/delete_game/<int:game_id>')    
def delete_game(game_id):
    game_id = request.form['delete']
    game = Game.query.filter_by(id=game_id).first()
    
    try:
        db_session.delete(game)
        db_session.commit()
        games = Game.query.all()
        flash("Game deleted successfully!")
        return render_template('gamesedit.html', games=games)
    except:
        flash("Whoops! There was a problem deleting game, try again...")


# Errors
@ app.errorhandler(404)
def page_not_found(error_description):
    return render_template('404.html', error_description=error_description)