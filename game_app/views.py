from game_app import app, login_manager, admin
from game_app.forms import RegistrationForm, LoginForm, EditUserForm, AddGameForm
from game_app.models import User, Role, Team, UserAdminView, RoleAdminView, UploadFile, Game, Tip, UserTournaments, GamesPlayed
from game_app.database import db_session
from game_app.config import Config

import os
import uuid
from flask import render_template, url_for, redirect, request, flash, json
from flask_login import login_user, current_user, logout_user, login_required

from werkzeug.utils import secure_filename
from datetime import datetime

config = Config()

admin.add_view(UserAdminView(User, db_session))
admin.add_view(RoleAdminView(Role, db_session))
admin.add_view(RoleAdminView(Game, db_session))


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(user_id)
    except:
        return None
    # return User.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to view that page.')
    return redirect(url_for('login'))


@app.route('/home')
def home():
    teams = Team.query.all()
    IMG_LIST = os.listdir('game_app/static/files')
    IMG_LIST = ['files/' + i for i in IMG_LIST]
    return render_template('index.html', teams=teams, current_user=current_user, image_list=IMG_LIST)


@app.route('/user/<int:user_id>')
# @login_required
def user(user_id):
    user = User.query.filter_by(id=user_id).first()

    user_id = current_user.get_id()
    print("___________________")
    print(user_id)
    user_auth = current_user.is_authenticated
    print("___________________")
    print(user_auth)

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
                user.authenticated = True
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
    user = current_user
    user.authenticated = False
    logout_user()
    flash("You have been logged out!")
    return redirect(url_for('login'))


@app.route('/edit/<int:user_id>', methods=('GET', 'POST'))
@login_required
def edit(user_id):
    form = EditUserForm()
    user = User.query.filter_by(id=user_id).first()

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
@login_required
def delete(user_id):

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
@login_required
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
@login_required
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
    while i < 32:
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

    #
    user_id = 1
    user = User.query.filter_by(id=user_id).first()
    if form.validate_on_submit():
        existing_game = Game.query.filter_by(id=form.id.data).first()
        if existing_game is None:
            game = Game(id=form.id.data,
                        discipline=form.discipline.data,
                        game_name=form.tournament.data,
                        game_phase=form.game_phase.data,
                        team_1=form.team_1.data,
                        team_2=form.team_2.data,
                        game_day=form.game_day.data,
                        game_time=form.game_time.data,
                        )
            db_session.add(game)
            db_session.commit()
            flash('Add game successfully.')
            return redirect(url_for('games'))
        flash('Whoops! There was a problem!')
    return render_template('gameslist.html', teams=teams, games=games, form=form, user=user)


@app.route('/admin/game_edit', methods=['GET', 'POST'])
def game_edit():
    games = Game.query.all()
    return render_template('gamesedit.html', games=games)


@app.post('/admin/edit_one_game/<int:game_id>')
def edit_one_game(game_id):

    edit_game = Game.query.filter_by(id=game_id).first()
    discipline = request.form.get('discipline')
    tournament = request.form.get('tournament')
    phase = request.form.get('phase')
    name_team_1 = request.form.get('name_team_1')
    name_team_2 = request.form.get('name_team_2')
    game_date = request.form.get('game_day')
    game_time = request.form.get('game_time')
    team1 = request.form.get('team1')
    team2 = request.form.get('team2')
    finished = request.form.get('game_completed') != None

    try:
        edit_game.game_discipline = discipline
        edit_game.tournament = tournament
        edit_game.game_phase = phase
        edit_game.team_1 = name_team_1
        edit_game.team_2 = name_team_2
        edit_game.game_day = game_date
        edit_game.game_time = game_time
        edit_game.goals_team_1 = team1
        edit_game.goals_team_2 = team2
        edit_game.finished = finished
        db_session.commit()

        if finished == True:
            set_winner(edit_game)
            update_tip_points(game_id)
            update_team_points(edit_game)

        flash("Game updated successfully!")
        return redirect(url_for('game_edit'))
    except:
        flash("Error! There was a problem edit game... try again.")
    return redirect(url_for('game_edit'))


def set_winner(edit_game):
    if edit_game.goals_team_1 > edit_game.goals_team_2:
        edit_game.winner = 1
    elif edit_game.goals_team_1 < edit_game.goals_team_2:
        edit_game.winner = 2
    else:
        edit_game.winner = 0
    db_session.commit()


def update_tip_points(game_id):
    game = Game.query.filter_by(id=game_id).first()
    tips = Tip.query.all()

    for tip in tips:
        if tip.game_id == game_id:
            if tip.tip_goals_team_1 != None and tip.tip_goals_team_2 != None:
                game_difference = game.goals_team_1 - game.goals_team_2
                tip_difference = tip.tip_goals_team_1 - tip.tip_goals_team_2

                if tip.tip_goals_team_1 == game.goals_team_1 and tip.tip_goals_team_2 == game.goals_team_2:
                    tip.tip_points = 5
                elif tip.winner == game.winner and game_difference == tip_difference:
                    tip.tip_points = 3
                elif tip.winner == game.winner:
                    tip.tip_points = 2
                else:
                    tip.tip_points = 0
            else:
                tip.tip_points = 0
            db_session.commit()


def update_team_points(edit_game):
    team_name_1 = edit_game.team_1
    team_name_2 = edit_game.team_2

    team_1 = Team.query.filter_by(name=team_name_1.lower()).first()
    team_2 = Team.query.filter_by(name=team_name_2.lower()).first()

    games_played = GamesPlayed.query.all()

    if is_game_played_exist(edit_game, games_played):
        pass
    else:
        fill_teams_table(edit_game, team_1, team_2)
        game_played_team_1 = GamesPlayed(
            game_id=edit_game.id,
            team_id=team_1.id)
        db_session.add(game_played_team_1)
        game_played_team_2 = GamesPlayed(
            game_id=edit_game.id,
            team_id=team_2.id)
        db_session.add(game_played_team_2)
        db_session.commit()


def is_game_played_exist(edit_game, games_played):
    for game_played in games_played:
        if edit_game.id == game_played.game_id:
            return True


def fill_teams_table(edit_game, team_1, team_2):
    if int(edit_game.winner) == 1:
        team_1.games_played += 1
        team_1.wins += 1
        team_1.draws += 0
        team_1.lost += 0
        team_1.goal_scored += edit_game.goals_team_1
        team_1.goal_lost += edit_game.goals_team_2
        team_1.goal_balance = team_1.goal_scored - team_1.goal_lost
        team_1.points += 3

        team_2.games_played += 1
        team_2.wins += 0
        team_2.draws += 0
        team_2.lost += 1
        team_2.goal_scored += edit_game.goals_team_2
        team_2.goal_lost += edit_game.goals_team_1
        team_2.goal_balance = team_2.goal_scored - team_2.goal_lost
        team_2.points += 0

    elif int(edit_game.winner) == 2:
        team_1.games_played += 1
        team_1.wins += 0
        team_1.draws += 0
        team_1.lost += 1
        team_1.goal_scored += edit_game.goals_team_1
        team_1.goal_lost += edit_game.goals_team_2
        team_1.goal_balance = team_1.goal_scored - team_1.goal_lost
        team_1.points += 0

        team_2.games_played += 1
        team_2.wins += 1
        team_2.draws += 0
        team_2.lost += 0
        team_2.goal_scored += edit_game.goals_team_2
        team_2.goal_lost += edit_game.goals_team_1
        team_2.goal_balance = team_2.goal_scored - team_2.goal_lost
        team_2.points += 3

    elif int(edit_game.winner) == 0:
        team_1.games_played += 1
        team_1.wins += 0
        team_1.draws += 1
        team_1.lost += 0
        team_1.goal_scored += edit_game.goals_team_1
        team_1.goal_lost += edit_game.goals_team_2
        team_1.goal_balance = team_1.goal_scored - team_1.goal_lost
        team_1.points += 1

        team_2.games_played += 1
        team_2.wins += 0
        team_2.draws += 1
        team_2.lost += 0
        team_2.goal_scored += edit_game.goals_team_2
        team_2.goal_lost += edit_game.goals_team_1
        team_2.goal_balance = team_2.goal_scored - team_2.goal_lost
        team_2.points += 1
    db_session.commit()


@app.post('/admin/edit_all_games')
def edit_all_games():
    rows = Game.query.count()
    row = 1

    try:
        discipline = request.form.get('all_discipline')
        tournament = request.form.get('all_tournament')
        phase = request.form.get('all_phase')

        while row <= rows:
            edit_game = Game.query.filter_by(id=row).first()
            edit_game.game_discipline = discipline
            edit_game.tournament = tournament
            edit_game.game_phase = phase
            row += 1
        db_session.commit()
        flash("All games updated successfully!")
        return redirect(url_for('game_edit'))

    except:
        flash("Error! There was a problem edit all games... try again.")
    return redirect(url_for('game_edit'))


@app.post('/admin/delete_game/<int:game_id>')
def delete_game(game_id):
    game = Game.query.filter_by(id=game_id).first()

    try:
        db_session.delete(game)
        db_session.commit()
        games = Game.query.all()
        flash("Game deleted successfully!")
        return render_template('gamesedit.html', games=games)
    except:
        flash("Whoops! There was a problem deleting game, try again...")

    return redirect(url_for('game_edit'))


@app.route('/user/tips', methods=['GET', 'POST'])
def tips():
    games = Game.query.all()
    user_tips = Tip.query.all()

    # user_id = current_user.get_id()
    user_id = 1
    user = User.query.filter_by(id=user_id).first()

    for user_tip in user_tips:
        is_date_locked(user_tip.id)

    return render_template('accounts/usertips.html', user_tips=user_tips, games=games, user=user)


@app.post('/user/load_tips')
def load_tips():
    #
    user_id = 1
    tournament_name = "World Cup 2022"
    user = User.query.filter_by(id=user_id).first()
    games = Game.query.all()

    if is_tournament_exist(tournament_name, user):
        flash("Tournament exist!")
        return redirect(url_for('tips'))
    else:
        try:
            for game in games:
                user_tip = Tip(
                    game_id=game.id,
                    tip_goals_team_1=None,
                    tip_goals_team_2=None,
                    tip_points=None,
                    user_id=user_id)
                db_session.add(user_tip)

            user_tournament = UserTournaments(
                tournament=game.tournament,
                user_id=user_id)
            db_session.add(user_tournament)
            db_session.commit()
            flash("Tips addes successfully!")
            return redirect(url_for('tips'))
        except:
            flash('Whoops! There was a problem to add games for tips!')
            return redirect(url_for('tips'))


def is_tournament_exist(tournament_name, user):
    for tournament in user.tournaments:
        if tournament_name == tournament.tournament:
            return True


@app.post('/user/edit_tip/<int:tip_id>')
def edit_tip(tip_id):

    edit_tip = Tip.query.filter_by(id=tip_id).first()
    team1 = request.form.get('team1')
    team2 = request.form.get('team2')

    if edit_tip.tip_lock == 0 or edit_tip.tip_lock == None:

        if is_date_locked(tip_id):
            flash("Sorry, it's to late for tip this game!")
        else:
            try:
                edit_tip.tip_goals_team_1 = team1
                edit_tip.tip_goals_team_2 = team2
                tip_winner(edit_tip)
                db_session.commit()
                flash("Tip updated successfully!")
            except:
                flash("Error! There was a problem edit tip... try again.")
            return redirect(url_for('tips'))
    else:
        flash("Sorry, it's to late for tip this game!")
    return redirect(url_for('tips'))


def tip_winner(edit_tip):
    if edit_tip.tip_goals_team_1 > edit_tip.tip_goals_team_2:
        edit_tip.winner = 1
    elif edit_tip.tip_goals_team_1 < edit_tip.tip_goals_team_2:
        edit_tip.winner = 2
    else:
        edit_tip.winner = 0


def is_date_locked(tip_id):
    game = Game.query.filter_by(id=tip_id).first()
    game_day = game.game_day
    game_time = game.game_time

    present = datetime.now()
    string_date_time = f"{game_day} {game_time}"
    date_time = datetime.strptime(string_date_time, "%Y-%m-%d %H:%M:%S")

    if present >= date_time:
        lock_tip(tip_id)
        return True


def lock_tip(tip_id):
    edit_tip = Tip.query.filter_by(id=tip_id).first()
    edit_tip.tip_lock = 1
    db_session.commit()


@ app.route('/admin/db_update', methods=['GET', 'POST'])
def db_update():

    if request.method == 'POST':
        try:
            table_name1 = 'tip'
            table_name2 = 'games'

            column_name1 = 'tournament'
            column_name2 = 'tournament'

            query1 = f"ALTER TABLE {table_name1} ADD {column_name1} VARCHAR(20);"
            db_session.execute(query1)

            query2 = f"ALTER TABLE {table_name2} ADD {column_name2} VARCHAR(20);"
            db_session.execute(query2)

            flash("Database update successfully!")
        except:
            flash("There was a problem edit database...!")
    return render_template('dbupdate.html')

# Errors


@ app.errorhandler(404)
def page_not_found(error_description):
    return render_template('404.html', error_description=error_description)
