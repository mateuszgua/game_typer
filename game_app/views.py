from game_app import app, login_manager, admin
from game_app.forms import RegistrationForm, LoginForm, EditUserForm, AddGameForm, AddGroupForm
from game_app.models import User, Role, Team, UserAdminView, RoleAdminView, UploadFile, Game, Tip, UserTournaments, GamesPlayed, BetGroup, UserBetGroup
from game_app.database import db_session
from game_app.config import Config

import os
import uuid
from flask import render_template, url_for, redirect, request, flash, json
from flask_login import login_user, current_user, logout_user, login_required

from werkzeug.utils import secure_filename
from datetime import datetime, timedelta, date, time

config = Config()

admin.add_view(UserAdminView(User, db_session))
admin.add_view(RoleAdminView(Role, db_session))
admin.add_view(RoleAdminView(Game, db_session))
admin.add_view(RoleAdminView(Team, db_session))
admin.add_view(RoleAdminView(GamesPlayed, db_session))
admin.add_view(RoleAdminView(UploadFile, db_session))
admin.add_view(RoleAdminView(UserTournaments, db_session))
admin.add_view(RoleAdminView(Tip, db_session))
admin.add_view(RoleAdminView(UserBetGroup, db_session))
admin.add_view(RoleAdminView(BetGroup, db_session))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to view that page.')
    return redirect(url_for('login'))


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/home')
def home():
    teams = Team.query.all()

    try:
        images_list = os.listdir('game_app/static/files')
        images_list = ['files/' + image for image in images_list]
    except:
        flash('There is a problem to load all images of flags.')

    last_games = list_last_games()
    current_games = list_current_games()
    next_games = list_next_games()

    group_list = create_sorted_list()
    sort_team_table(group_list)

    final_1_8 = Game.query.filter_by(game_phase="1/8").all()
    final_1_4 = Game.query.filter_by(game_phase="1/4").all()
    final_1_2 = Game.query.filter_by(game_phase="1/2").all()
    final_3rd = Game.query.filter_by(game_phase="3rd").all()
    final = Game.query.filter_by(game_phase="final").all()

    return render_template('index.html',
                           teams=teams,
                           image_list=images_list,
                           group_list=group_list,
                           last_games=last_games,
                           current_games=current_games,
                           next_games=next_games,
                           final_1_8=final_1_8,
                           final_1_4=final_1_4,
                           final_1_2=final_1_2,
                           final_3rd=final_3rd,
                           final=final)


def create_sorted_list():
    group_list = []
    group_A = Team.query.filter_by(
        group="A").order_by(Team.points.desc(), Team.goal_balance.desc()).all()
    group_list.insert(0, group_A)
    group_B = Team.query.filter_by(
        group="B").order_by(Team.points.desc(), Team.goal_balance.desc()).all()
    group_list.insert(1, group_B)
    group_C = Team.query.filter_by(
        group="C").order_by(Team.points.desc(), Team.goal_balance.desc()).all()
    group_list.insert(2, group_C)
    group_D = Team.query.filter_by(
        group="D").order_by(Team.points.desc(), Team.goal_balance.desc()).all()
    group_list.insert(3, group_D)
    group_E = Team.query.filter_by(
        group="E").order_by(Team.points.desc(), Team.goal_balance.desc()).all()
    group_list.insert(4, group_E)
    group_F = Team.query.filter_by(
        group="F").order_by(Team.points.desc(), Team.goal_balance.desc()).all()
    group_list.insert(5, group_F)
    group_G = Team.query.filter_by(
        group="G").order_by(Team.points.desc(), Team.goal_balance.desc()).all()
    group_list.insert(6, group_G)
    group_H = Team.query.filter_by(
        group="H").order_by(Team.points.desc(), Team.goal_balance.desc()).all()
    group_list.insert(7, group_H)
    return group_list


def sort_team_table(group_list):
    for group in group_list:
        i = 1
        for team in group:
            team.group_position = i
            db_session.commit()
            i += 1


def list_last_games():
    present = date.today()
    i = 1
    day_yesterday = present - timedelta(days=i)

    last_games = Game.query.filter_by(
        game_day=day_yesterday).order_by(Game.game_time.asc()).all()
    return last_games


def list_current_games():
    present = date.today()

    current_games = Game.query.filter_by(
        game_day=present).order_by(Game.game_time.asc()).all()
    return current_games


def list_next_games():
    present = date.today()
    i = 1
    number_of_games = 64
    day_tommorow = present + timedelta(days=i)

    while Game.query.filter_by(game_day=day_tommorow).count() == 0:
        day_tommorow += timedelta(days=i)
        if i > number_of_games:
            break

    next_games = Game.query.filter_by(
        game_day=day_tommorow).order_by(Game.game_time.asc()).all()
    return next_games


@app.route('/user')
@login_required
def user():
    user_id = current_user.get_id()
    user = User.query.filter_by(id=user_id).first()
    images_list = os.listdir('game_app/static/files')
    images_list = ['files/' + image for image in images_list]
    tournaments = UserTournaments.query.filter_by(user_id=user_id).all()
    user_tips = Tip.query.filter_by(user_id=user_id).all()
    user_points = 0
    user_groups = UserBetGroup.query.filter_by(user_id=user_id).all()

    user_points = count_user_points_from_bet(user_tips, user_points)

    return render_template('accounts/user.html',
                           user=user,
                           image_list=images_list,
                           tournaments=tournaments,
                           user_points=user_points,
                           user_groups=user_groups)


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
                db_session.add(user)
                db_session.commit()
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
    db_session.add(user)
    db_session.commit()
    logout_user()
    flash("You have been logged out!")
    return redirect(url_for('home'))


@app.route('/user_info')
@login_required
def user_info():
    user_id = current_user.get_id()
    user = User.query.filter_by(id=user_id).first()
    return render_template('accounts/user_info.html', user=user)


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
        except:
            flash("Error! There was a problem edit user... try again.")
        finally:
            return render_template('accounts/edit.html',
                                   form=form,
                                   user=user,
                                   id=user_id)
    else:
        return render_template('accounts/edit.html',
                               form=form,
                               user=user,
                               id=user_id)


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
    return render_template('load_file.html')


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
    return render_template('select_file.html', files=files)


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
@login_required
def games():
    games = Game.query.all()
    teams = Team.query.all()
    form = AddGameForm()

    user_id = current_user.get_id()
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
    return render_template('games_list.html',
                           teams=teams,
                           games=games,
                           form=form,
                           user=user)


@app.route('/admin/game_edit', methods=['GET', 'POST'])
@login_required
def game_edit():
    games = Game.query.all()
    return render_template('games_edit.html', games=games)


@app.post('/admin/edit_one_game/<int:game_id>')
@login_required
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
    finally:
        if team1 != None and team2 != None:
            edit_game.goals_team_1 = team1
            edit_game.goals_team_2 = team2
            db_session.commit()
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
        if edit_game.game_phase != "group":
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
@login_required
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
    finally:
        return redirect(url_for('game_edit'))


@app.post('/admin/delete_game/<int:game_id>')
@login_required
def delete_game(game_id):
    game = Game.query.filter_by(id=game_id).first()

    try:
        db_session.delete(game)
        db_session.commit()
        games = Game.query.all()
        flash("Game deleted successfully!")
        return render_template('games_edit.html', games=games)
    except:
        flash("Whoops! There was a problem deleting game, try again...")
    finally:
        return redirect(url_for('game_edit'))


@app.route('/user/tips', methods=['GET', 'POST'])
@login_required
def tips():
    user_id = current_user.get_id()
    games = Game.query.all()
    tips_amount = Tip.query.filter_by(user_id=user_id).count()
    user_tips = Tip.query.filter_by(user_id=user_id).all()
    user_points = 0
    user_points = count_user_points_from_bet(user_tips, user_points)

    if tips_amount == 0:
        flash("Please add tournament for your account to show any bet")
    else:
        for user_tip in user_tips:
            is_date_locked(user_tip.game_id)

    return render_template('accounts/user_tips.html',
                           user_points=user_points,
                           user_tips=user_tips,
                           games=games,
                           tips_amount=tips_amount)


def count_user_points_from_bet(user_tips, user_points):
    for user_tip in user_tips:
        if user_tip.tip_points == None:
            user_points += 0
        else:
            user_points += int(user_tip.tip_points)
    return user_points


@app.post('/user/load_tips')
@login_required
def load_tips():
    user_id = current_user.get_id()
    tournament_name = "World Cup 2022"
    user = User.query.filter_by(id=user_id).first()
    games = Game.query.all()

    if is_tournament_exist(tournament_name, user):
        flash("Tournament exist!")
        return redirect(url_for('user'))
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
        except:
            flash('Whoops! There was a problem to add games for tips!')
        finally:
            return redirect(url_for('user'))


def is_tournament_exist(tournament_name, user):
    for tournament in user.tournaments:
        if tournament_name == tournament.tournament:
            return True


@app.post('/user/edit_tip/<int:tip_id>')
@login_required
def edit_tip(tip_id):

    edit_tip = Tip.query.filter_by(id=tip_id).first()
    team1 = request.form.get('team1')
    team2 = request.form.get('team2')

    if edit_tip.tip_lock == 0 or edit_tip.tip_lock == None:

        if is_date_locked(edit_tip.game_id):
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
            finally:
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
    edit_tip = Tip.query.filter_by(game_id=tip_id).all()
    for tip in edit_tip:
        tip.tip_lock = 1
    db_session.commit()


@app.route('/user/add_group', methods=('GET', 'POST'))
@login_required
def add_group():
    user_id = current_user.get_id()
    form = AddGroupForm()
    if form.validate_on_submit():
        existing_group = BetGroup.query.filter_by(name=form.name.data).first()
        if existing_group is None:
            bet_group = BetGroup(
                name=form.name.data,
                tournament=form.tournament.data,
                number_of_users=1,
            )
            db_session.add(bet_group)
            db_session.commit()

            bet_group = BetGroup.query.filter_by(
                name=form.name.data).first()
            user_group = UserBetGroup(
                bet_group_id=bet_group.id,
                user_id=user_id,
            )
            db_session.add(user_group)
            db_session.commit()
            flash('Group add successfully.')
            return redirect(url_for('user'))
        flash('A group name already exist.')
    return render_template('add_group.html', form=form)


@app.route('/user/group/<int:group_id>', methods=['GET', 'POST'])
@login_required
def group(group_id):
    user_id = current_user.get_id()
    bet_amount = UserBetGroup.query.filter_by(user_id=user_id).count()
    user_groups = UserBetGroup.query.filter_by(
        bet_group_id=group_id).order_by(UserBetGroup.points.desc()).all()
    bet_group = BetGroup.query.filter_by(id=group_id).first()

    sort_users_in_group(user_groups)
    last_game = find_last_game()
    users_bets = Tip.query.filter_by(game_id=last_game.id).all()
    update_user_points(user_groups)

    if bet_amount == 0:
        flash("Please add bet group for your account to show any bets.")

    return render_template('accounts/bet_group.html',
                           user_groups=user_groups,
                           bet_group=bet_group,
                           last_game=last_game,
                           users_bets=users_bets)


def sort_users_in_group(user_groups):
    place = 1
    for user_group in user_groups:
        user_group.place = place
        db_session.commit()
        place += 1


def find_last_game():
    present_day = date.today()
    present = datetime.now()
    present_time = present.strftime("%H:%M:%S")
    i = 1
    game_day = present_day

    while Game.query.filter_by(game_day=game_day).count() == 0:
        game_day -= timedelta(days=i)

    if game_day == present_day:
        game = Game.query.filter_by(game_day=game_day).order_by(
            Game.game_time.asc()).first()
        if game.game_time >= present_time:
            game_id = game.id - 1
            game = Game.query.filter_by(id=game_id).first()

    else:
        game = Game.query.filter_by(game_day=game_day).order_by(
            Game.game_time.desc()).first()

    return game


def update_user_points(user_groups):
    for user in user_groups:
        user.points = 0

        user_tips = Tip.query.filter_by(user_id=user.user_id).all()
        for user_tip in user_tips:
            if user_tip.tip_points == None:
                user.points += 0
            else:
                user.points += int(user_tip.tip_points)
        db_session.commit()


@app.post('/user/group/add_user_bet_group/<int:group_id>')
@login_required
def add_user_bet_group(group_id):

    try:
        user_email = request.form.get('user_email')
        user_nick = request.form.get('nick_name')

        if user_email != None:
            user = User.query.filter_by(email=user_email).first()
            if user != None:
                add_user_to_group_if_not_exist(user, group_id)
            else:
                flash("User not exist! Please check email.")

        elif user_nick != None:
            user = User.query.filter_by(nick=user_nick).first()
            if user != None:
                add_user_to_group_if_not_exist(user, group_id)
            else:
                flash("User not exist! Please check nick.")

        else:
            flash("Please fill user email or nick!")
    finally:
        return redirect(url_for('group', group_id=group_id))


def add_user_to_group_if_not_exist(user, group_id):
    if UserBetGroup.query.filter_by(user_id=user.id).count() == 0:
        user_group = UserBetGroup(
            bet_group_id=group_id,
            user_id=user.id,
        )
        db_session.add(user_group)
        db_session.commit()
        flash("User added successfully!")
    else:
        flash("User exist in group!")


@ app.route('/admin/db_update', methods=['GET', 'POST'])
@login_required
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
    return render_template('db_update.html')


@ app.errorhandler(404)
def page_not_found(error_description):
    return render_template('404.html', error_description=error_description)


@ app.errorhandler(500)
def internal_server_error(error_description):
    return render_template('500.html', error_description=error_description)
