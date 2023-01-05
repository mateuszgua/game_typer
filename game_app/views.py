from game_app import app, login_manager, admin
from game_app.forms import RegistrationForm, LoginForm, EditUserForm, AddGameForm, AddGroupForm
from game_app.models import User, Role, Team, UserAdminView, RoleAdminView, UploadFile, Game, Bet, UserTournaments, GamesPlayed, BetGroup, UserBetGroup
from game_app.database import db_session
from game_app.config import Config
from game_app.helpers import Helpers
from game_app.database_reader import TeamReader, GameReader, UserReader, TournamentReader, BetReader, UserBetGroupReader, FilesReader
from game_app.my_error import TeamsDatabaseEmpty, ImagesNotExist, GameNotExist, DatabaseReaderProblem, DatabaseWriterError, GamesDatabaseEmpty, BetsDatabaseEmpty
from game_app.database_writer import GameWriter, TeamWriter, FileWriter, UserWriter, BetWriter

import os
from flask import render_template, url_for, redirect, request, flash
from flask import abort
from flask_login import login_user, current_user, logout_user, login_required

from werkzeug.utils import secure_filename
from datetime import datetime, timedelta, date

config = Config()

admin.add_view(UserAdminView(User, db_session))
admin.add_view(RoleAdminView(Role, db_session))
admin.add_view(RoleAdminView(Game, db_session))
admin.add_view(RoleAdminView(Team, db_session))
admin.add_view(RoleAdminView(GamesPlayed, db_session))
admin.add_view(RoleAdminView(UploadFile, db_session))
admin.add_view(RoleAdminView(UserTournaments, db_session))
admin.add_view(RoleAdminView(Bet, db_session))
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


@app.route('/')
def index():
    try:
        print(f"Flask ENV is set to: {Config.ENV}")
    except:
        error_description = 'There is a problem to load ENV'
        abort(404, error_description)
    else:
        return render_template('home.html')


@app.route('/home')
def home():
    try:
        teams = TeamReader.get_all_teams()
        images_list = Helpers.get_images_list()
        last_games = Helpers.get_list_last_games()
        current_games = Helpers.get_list_last_games()
        next_games = Helpers.get_list_next_games()
        group_list = Helpers.create_sorted_list()
        TeamWriter.sort_team_table(group_list)

        final_1_8 = GameReader.get_games_by_filter("game_phase", "1/8")
        final_1_4 = GameReader.get_games_by_filter("game_phase", "1/4")
        final_1_2 = GameReader.get_games_by_filter("game_phase", "1/2")
        final_3rd = GameReader.get_games_by_filter("game_phase", "3rd")
        final = GameReader.get_games_by_filter("game_phase", "final")

    except TeamsDatabaseEmpty:
        error_description = TeamsDatabaseEmpty()
        page_not_found(error_description)
        abort(500, error_description)
    except ImagesNotExist:
        error_description = ImagesNotExist()
        page_not_found(error_description)
        abort(404, error_description)
    except GameNotExist:
        error_description = GameNotExist()
        page_not_found(error_description)
        abort(500, error_description)
    except DatabaseReaderProblem:
        error_description = DatabaseReaderProblem()
        flash(error_description)
        return render_template('index.html')
    except DatabaseWriterError:
        error_description = DatabaseWriterError()
        flash(error_description)
        return render_template('index.html')
    else:
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


@app.route('/user')
@login_required
def user():
    try:
        user_id = current_user.get_id()
        user = UserReader.get_user("id", user_id)
        images_list = Helpers.get_images_list()
        tournaments = TournamentReader.get_all_tournaments_filter(
            "user_id", user_id)
        user_tips = BetReader.get_all_bets_filter("user_id", user_id)
        user_points = 0
        user_groups = UserBetGroupReader.get_all_user_groups_filter(
            "user_id", user_id)
        user_points = Helpers.count_user_points_from_bet(
            user_tips, user_points)
    except DatabaseReaderProblem:
        error_description = DatabaseReaderProblem()
        flash(error_description)
        return render_template('accounts/user.html')
    except DatabaseWriterError:
        error_description = DatabaseWriterError()
        flash(error_description)
        return render_template('accounts/user.html')
    else:
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
        existing_user = UserReader.get_user("email", form.email.data)
        if existing_user is None:
            try:
                UserWriter.register_user(
                    form.firstname.data,
                    form.lastname.data,
                    form.email.data,
                    form.nick.data,
                    form.password1.data,
                )
            except DatabaseWriterError:
                error_description = DatabaseWriterError()
                flash(error_description)
                return redirect(url_for('register'))
            else:
                return redirect(url_for('login'))
        flash('A user already exist with that email address.')
    return render_template('accounts/register.html', form=form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user', user_id=user.id))

    form = LoginForm()
    if form.validate_on_submit():
        user = UserReader.get_user("email", form.email.data)
        if user:
            if user.check_password(password=form.password1.data):
                try:
                    UserWriter.login_user_in_account(user)
                    login_user(user, remember=form.remember.data)
                    next = request.args.get('next')
                except DatabaseWriterError:
                    error_description = DatabaseWriterError()
                    flash(error_description)
                    return redirect(url_for('login'))
                else:
                    return redirect(next or (url_for('user', user_id=user.id)))
            flash("Wrong Password - Try Again!")
        else:
            flash("That User Doesn't Exist! Try Again...")
    return render_template('accounts/login.html', form=form)


@app.route('/logout', methods=('GET', 'POST'))
@login_required
def logout():
    try:
        user = current_user
        UserWriter.logout_user_from_account(user)
        logout_user()
        flash("You have been logged out!")
    except DatabaseWriterError:
        error_description = DatabaseWriterError()
        flash(error_description)
        abort(500, error_description)
    else:
        return redirect(url_for('home'))


@app.route('/user_info')
@login_required
def user_info():
    try:
        user_id = current_user.get_id()
        user = UserReader.get_user("id", user_id)
    except DatabaseReaderProblem:
        error_description = DatabaseReaderProblem()
        flash(error_description)
        return render_template('accounts/user_info.html')
    else:
        return render_template('accounts/user_info.html', user=user)


@app.route('/edit/<int:user_id>', methods=('GET', 'POST'))
@login_required
def edit(user_id):
    form = EditUserForm()
    user = UserReader.get_user("id", user_id)

    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        password = request.form['password']
        email = request.form['email']
        nick = request.form['nick']

        try:
            UserWriter.edit_user_data(user,
                                      firstname,
                                      lastname,
                                      password,
                                      email,
                                      nick)
        except DatabaseWriterError:
            error_description = DatabaseWriterError()
            flash(error_description)
            flash("Error! There was a problem edit user... try again.")
            return render_template('accounts/edit.html')
        else:
            flash("User updated successfully!")
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
        form = RegistrationForm()
        user = UserReader.get_user("id", user_id)

        try:
            UserWriter.delete_user(user)
        except DatabaseWriterError:
            error_description = DatabaseWriterError()
            flash(error_description)
            flash("Whoops! There was a problem deleting user, try again...")
            return redirect(url_for('edit'))
        else:
            flash("User deleted successfully!")
            return render_template('accounts/register.html', form=form)

    else:
        flash("Sorry, you can't delete that user!")
        return redirect(url_for('home'))


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

        if file and Helpers.get_allowed_file(config, file.filename):
            try:
                filename = secure_filename(file.filename)
                file.save(os.path.join(config.UPLOAD_FOLDER, filename))
                FileWriter.save_file(file)
            except DatabaseWriterError:
                error_description = DatabaseWriterError()
                flash(error_description)
                return redirect(url_for('upload_file'))
            else:
                flash(f"Uploaded: {file.filename}")
    return render_template('load_file.html')


@app.route('/admin/select_file', methods=['GET', 'POST'])
@login_required
def select_file():
    try:
        files = FilesReader.get_all_files()
        if request.method == 'POST':
            if request.form.get('mycheckbox') != None:
                file_idx = request.form.get('mycheckbox')
                Helpers.get_process_json(file_idx)
                flash(f"Load successfully!")
            else:
                flash(f"Please chose one.")
    except DatabaseReaderProblem:
        error_description = DatabaseReaderProblem()
        flash(error_description)
        return render_template('select_file.html')
    else:
        return render_template('select_file.html', files=files)


@app.route('/admin/games', methods=['GET', 'POST'])
@login_required
def games():
    try:
        games = GameReader.get_all_games()
        teams = TeamReader.get_all_teams()
        form = AddGameForm()
        user_id = current_user.get_id()
        user = UserReader.get_user("id", user_id)

        if form.validate_on_submit():
            existing_game = GameReader.get_one_game_by_filter(
                "id", form.id.data)
            if existing_game is None:
                GameWriter.save_game_data(form.id.data,
                                          form.discipline.data,
                                          form.tournament.data,
                                          form.game_phase.data,
                                          form.team_1.data,
                                          form.team_2.data,
                                          form.game_day.data,
                                          form.game_time.data)
                flash('Add game successfully.')
                return redirect(url_for('games'))
            flash('Whoops! There was a problem!')
    except GamesDatabaseEmpty:
        error_description = GamesDatabaseEmpty()
        page_not_found(error_description)
        abort(500, error_description)
    except TeamsDatabaseEmpty:
        error_description = TeamsDatabaseEmpty()
        page_not_found(error_description)
        abort(500, error_description)
    except DatabaseWriterError:
        error_description = DatabaseWriterError()
        flash(error_description)
        abort(500, error_description)
    except GameNotExist:
        error_description = GameNotExist()
        page_not_found(error_description)
        abort(500, error_description)
    else:
        return render_template('games_list.html',
                               teams=teams,
                               games=games,
                               form=form,
                               user=user)


@app.route('/admin/game_edit', methods=['GET', 'POST'])
@login_required
def game_edit():
    try:
        games = GameReader.get_all_games()
    except GamesDatabaseEmpty:
        error_description = GamesDatabaseEmpty()
        page_not_found(error_description)
        abort(500, error_description)
    else:
        return render_template('games_edit.html', games=games)


@app.post('/admin/edit_one_game/<int:game_id>')
@login_required
def edit_one_game(game_id):
    try:
        edit_game = GameReader.get_one_game_by_filter("id", game_id)

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

        GameWriter.edit_game_data(edit_game,
                                  discipline,
                                  tournament,
                                  phase,
                                  name_team_1,
                                  name_team_2,
                                  game_date,
                                  game_time,
                                  finished)

        if finished == True:
            Helpers.set_game_winner(edit_game)
            Helpers.update_bet_points_from_game(game_id)
            Helpers.update_team_points_from_game(edit_game)

    except GameNotExist:
        error_description = GameNotExist()
        page_not_found(error_description)
        flash("Error! There was a problem edit game... try again.")
        return redirect(url_for('game_edit'))
    except DatabaseWriterError:
        error_description = DatabaseWriterError()
        flash(error_description)
        flash("Error! There was a problem edit game... try again.")
        return redirect(url_for('game_edit'))
    except BetsDatabaseEmpty:
        error_description = BetsDatabaseEmpty()
        flash(error_description)
        return redirect(url_for('game_edit'))
    except DatabaseReaderProblem:
        error_description = DatabaseReaderProblem()
        flash(error_description)
        return redirect(url_for('game_edit'))
    else:
        flash("Game updated successfully!")
    finally:
        if team1 != None and team2 != None:
            edit_game.goals_team_1 = team1
            edit_game.goals_team_2 = team2
            db_session.commit()
        return redirect(url_for('game_edit'))


@app.post('/admin/edit_all_games')
@login_required
def edit_all_games():
    try:
        rows = GameReader.get_count_games()
        row = 1
        discipline = request.form.get('all_discipline')
        tournament = request.form.get('all_tournament')
        phase = request.form.get('all_phase')

        while row <= rows:
            edit_game = GameReader.get_one_game_by_filter("id", row)
            GameWriter.save_edited_game(
                edit_game, discipline, tournament, phase)
            row += 1
        flash("All games updated successfully!")
    except GamesDatabaseEmpty:
        error_description = GamesDatabaseEmpty()
        page_not_found(error_description)
        abort(500, error_description)
    except DatabaseWriterError:
        error_description = DatabaseWriterError()
        flash(error_description)
        flash("Error! There was a problem edit all games... try again.")
        return redirect(url_for('game_edit'))
    except GameNotExist:
        error_description = GameNotExist()
        page_not_found(error_description)
        abort(500, error_description)
    else:
        return redirect(url_for('game_edit'))


@app.post('/admin/delete_game/<int:game_id>')
@login_required
def delete_game(game_id):
    try:
        game = GameReader.get_one_game_by_filter("id", game_id)
        GameWriter.delete_game(game)
        games = GameReader.get_all_games()
    except GameNotExist:
        error_description = GameNotExist()
        page_not_found(error_description)
        abort(500, error_description)
    except DatabaseWriterError:
        error_description = DatabaseWriterError()
        flash(error_description)
        flash("Whoops! There was a problem deleting game, try again...")
        return redirect(url_for('game_edit'))
    except GamesDatabaseEmpty:
        error_description = GamesDatabaseEmpty()
        page_not_found(error_description)
        abort(500, error_description)
    else:
        flash("Game deleted successfully!")
        return render_template('games_edit.html', games=games)


@app.route('/user/bets', methods=['GET', 'POST'])
@login_required
def bets():
    user_id = current_user.get_id()
    games = Game.query.all()
    bets_amount = Bet.query.filter_by(user_id=user_id).count()
    user_bets = Bet.query.filter_by(user_id=user_id).all()
    user_points = 0
    user_points = count_user_points_from_bet(user_bets, user_points)

    if bets_amount == 0:
        flash("Please add tournament for your account to show any bet")
    else:
        for user_bet in user_bets:
            is_date_locked(user_bet.game_id)

    return render_template('accounts/user_tips.html',
                           user_points=user_points,
                           user_tips=user_bets,
                           games=games,
                           tips_amount=bets_amount)


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
                user_tip = Bet(
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

    edit_tip = Bet.query.filter_by(id=tip_id).first()
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
    edit_tip = Bet.query.filter_by(game_id=tip_id).all()
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
    users_bets = Bet.query.filter_by(game_id=last_game.id).all()
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

        user_tips = Bet.query.filter_by(user_id=user.user_id).all()
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
def page_not_found(e):
    return render_template('404.html', e=e)


@ app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', e=e)
