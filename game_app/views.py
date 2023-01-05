from game_app import app, login_manager, admin
from game_app.forms import RegistrationForm, LoginForm, EditUserForm, AddGameForm, AddGroupForm
from game_app.models import User, Role, Team, UserAdminView, RoleAdminView, UploadFile, Game, Bet, UserTournaments, GamesPlayed, BetGroup, UserBetGroup
from game_app.database import db_session
from game_app.config import Config
from game_app.helpers import Helpers
from game_app.database_reader import TeamReader, GameReader, UserReader, TournamentReader, BetReader, UserBetGroupReader, FilesReader, BetGroupReader
from game_app.my_error import TeamsDatabaseEmpty, ImagesNotExist, GameNotExist, DatabaseReaderProblem, DatabaseWriterError, GamesDatabaseEmpty, BetsDatabaseEmpty
from game_app.database_writer import GameWriter, TeamWriter, FileWriter, UserWriter, BetWriter, TournamentWriter, BetGroupWriter, UserBetGroupWriter

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

        final_1_8 = GameReader.get_all_games_filter("game_phase", "1/8")
        final_1_4 = GameReader.get_all_games_filter("game_phase", "1/4")
        final_1_2 = GameReader.get_all_games_filter("game_phase", "1/2")
        final_3rd = GameReader.get_all_games_filter("game_phase", "3rd")
        final = GameReader.get_all_games_filter("game_phase", "final")

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
        user = UserReader.get_one_user_filter("id", user_id)
        images_list = Helpers.get_images_list()
        tournaments = TournamentReader.get_all_tournaments_filter(
            "user_id", user_id)
        user_bets = BetReader.get_all_bets_filter("user_id", user_id)
        user_points = 0
        user_groups = UserBetGroupReader.get_all_user_groups_filter(
            "user_id", user_id)
        user_points = Helpers.count_user_points_from_bet(
            user_bets, user_points)
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
        existing_user = UserReader.get_one_user_filter(
            "email", form.email.data)
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
        user = UserReader.get_one_user_filter("email", form.email.data)
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
        user = UserReader.get_one_user_filter("id", user_id)
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
    user = UserReader.get_one_user_filter("id", user_id)

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
        user = UserReader.get_one_user_filter("id", user_id)

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
        user = UserReader.get_one_user_filter("id", user_id)

        if form.validate_on_submit():
            existing_game = GameReader.get_one_game_filter(
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
        edit_game = GameReader.get_one_game_filter("id", game_id)

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
            edit_game = GameReader.get_one_game_filter("id", row)
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
        game = GameReader.get_one_game_filter("id", game_id)
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
    try:
        user_id = current_user.get_id()
        games = GameReader.get_all_games()
        bets_amount = BetReader.get_count_bets_filter("user_id", user_id)
        user_bets = BetReader.get_all_bets_filter("user_id", user_id)
        user_points = 0
        user_points = Helpers.count_user_points_from_bet(
            user_bets, user_points)

        if bets_amount == 0:
            flash("Please add tournament for your account to show any bet")
        else:
            for user_bet in user_bets:
                Helpers.is_date_locked(user_bet.game_id)
    except GamesDatabaseEmpty:
        error_description = GamesDatabaseEmpty()
        page_not_found(error_description)
        abort(500, error_description)
    except DatabaseReaderProblem:
        error_description = DatabaseReaderProblem()
        flash(error_description)
        return redirect(url_for('bets'))
    except DatabaseWriterError:
        error_description = DatabaseWriterError()
        flash(error_description)
        return redirect(url_for('bets'))
    else:
        return render_template('accounts/user_bets.html',
                               user_points=user_points,
                               user_bets=user_bets,
                               games=games,
                               bets_amount=bets_amount)


@app.post('/user/load_bets')
@login_required
def load_bets():
    try:
        user_id = current_user.get_id()
        tournament_name = "World Cup 2022"
        user = UserReader.get_one_user_filter("id", user_id)
        games = GameReader.get_all_games()

        if Helpers.is_tournament_exist(tournament_name, user):
            flash("Tournament exist!")
            return redirect(url_for('user'))
        else:
            try:
                for game in games:
                    BetWriter.save_user_bet(game.id, user_id)
                    TournamentWriter.save_user_tournament(
                        game.tournament, user_id)
                flash("Bets addes successfully!")
            except:
                flash('Whoops! There was a problem to add games for bets!')
    except DatabaseReaderProblem:
        error_description = DatabaseReaderProblem()
        flash(error_description)
        return redirect(url_for('user'))
    except GamesDatabaseEmpty:
        error_description = GamesDatabaseEmpty()
        page_not_found(error_description)
        abort(500, error_description)
    except DatabaseWriterError:
        error_description = DatabaseWriterError()
        page_not_found(error_description)
        abort(500, error_description)
    else:
        return redirect(url_for('user'))


@app.post('/user/edit_bet/<int:bet_id>')
@login_required
def edit_bet(bet_id):

    try:
        edit_bet = BetReader.get_one_bet_filter("id", bet_id)
        team1 = request.form.get('team1')
        team2 = request.form.get('team2')

        if edit_bet.bet_lock == 0 or edit_bet.bet_lock == None:

            if Helpers.is_date_locked(edit_bet.game_id):
                flash("Sorry, it's to late for bet this game!")
            else:
                try:
                    winner = Helpers.bet_winner(edit_bet)
                    BetWriter.edit_user_bet(edit_bet, team1, team2, winner)
                except DatabaseWriterError:
                    error_description = DatabaseWriterError()
                    flash(error_description)
                    flash("Error! There was a problem edit bet... try again.")
                    return redirect(url_for('bets'))
                else:
                    flash("Bet updated successfully!")
                finally:
                    return redirect(url_for('bets'))
        else:
            flash("Sorry, it's to late for bet this game!")
    except DatabaseReaderProblem:
        error_description = DatabaseReaderProblem()
        flash(error_description)
        return redirect(url_for('bets'))
    else:
        return redirect(url_for('bets'))


@app.route('/user/add_group', methods=('GET', 'POST'))
@login_required
def add_group():
    try:
        user_id = current_user.get_id()
        form = AddGroupForm()

        if form.validate_on_submit():
            existing_group = BetGroupReader.get_one_bet_group_filter(
                "name", form.name.data)

            if existing_group is None:
                BetGroupWriter.save_bet_group(
                    form.name.data, form.tournament.data)
                bet_group = BetGroupReader.get_one_bet_group_filter(
                    "name", form.name.data)
                UserBetGroupWriter.save_user_bet_group(bet_group.id, user_id)
                flash('Group add successfully.')
                return redirect(url_for('user'))
            flash('A group name already exist.')
    except DatabaseReaderProblem:
        error_description = DatabaseReaderProblem()
        flash(error_description)
        return redirect(url_for('add_group'))
    except DatabaseWriterError:
        error_description = DatabaseWriterError()
        page_not_found(error_description)
        abort(500, error_description)
    else:
        return render_template('add_group.html', form=form)


# TODO tu skończone

@app.route('/user/group/<int:group_id>', methods=['GET', 'POST'])
@login_required
def group(group_id):
    try:

        user_id = current_user.get_id()
        bet_amount = UserBetGroupReader.get_count_user_group_filter(
            "user_id", user_id)
        user_groups = UserBetGroupReader.get_all_user_group_filter_order(
            "bet_group_id", group_id)
        bet_group = BetGroupReader.get_one_bet_group_filter("id", group_id)
        Helpers.sort_users_in_group(user_groups)
        last_game = Helpers.find_last_game()
        users_bets = BetReader.get_all_bets_filter("game_id", last_game.id)
        Helpers.update_user_points(user_groups)
        if bet_amount == 0:
            flash("Please add bet group for your account to show any bets.")
    except DatabaseReaderProblem:
        error_description = DatabaseReaderProblem()
        flash(error_description)
        return redirect(url_for('add_group'))
    except DatabaseWriterError:
        error_description = DatabaseWriterError()
        page_not_found(error_description)
        abort(500, error_description)
    else:
        return render_template('accounts/bet_group.html',
                               user_groups=user_groups,
                               bet_group=bet_group,
                               last_game=last_game,
                               users_bets=users_bets)


@app.post('/user/group/add_user_bet_group/<int:group_id>')
@login_required
def add_user_bet_group(group_id):
    try:
        user_email = request.form.get('user_email')
        user_nick = request.form.get('nick_name')

        if user_email != None:
            user = UserReader.get_one_user_filter("email", user_email)
            if user != None:
                message = Helpers.add_user_to_group_if_not_exist(
                    user, group_id)
                flash(message)
            else:
                flash("User not exist! Please check email.")

        elif user_nick != None:
            user = UserReader.get_one_user_filter("nick", user_nick)
            if user != None:
                Helpers.add_user_to_group_if_not_exist(user, group_id)
            else:
                flash("User not exist! Please check nick.")

        else:
            flash("Please fill user email or nick!")
    except DatabaseReaderProblem:
        error_description = DatabaseReaderProblem()
        flash(error_description)
        return redirect(url_for('add_group'))
    except DatabaseWriterError:
        error_description = DatabaseWriterError()
        page_not_found(error_description)
        abort(500, error_description)
    else:
        return redirect(url_for('group', group_id=group_id))


@ app.route('/admin/db_update', methods=['GET', 'POST'])
@login_required
def db_update():

    if request.method == 'POST':
        try:
            table_name1 = 'bet'
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
