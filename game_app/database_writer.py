import uuid

from game_app.database import db_session
from game_app.my_error import DatabaseWriterError
from game_app.models import User, UploadFile, Team, Game, GamesPlayed


class TeamWriter:

    def sort_team_table(group_list):
        try:
            for group in group_list:
                i = 1
                for team in group:
                    team.group_position = i
                    db_session.commit()
                    i += 1
        except:
            raise DatabaseWriterError()

    def save_team_data(data, i):
        try:
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
        except:
            raise DatabaseWriterError()

    def edit_team_table(edit_game, team_1, team_2):
        try:
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
        except:
            raise DatabaseWriterError()


class UserWriter:

    def register_user(form_firstname, form_lastname, form_email, form_nick, form_password):
        try:
            user = User(firstname=form_firstname,
                        lastname=form_lastname,
                        email=form_email,
                        nick=form_nick,
                        )
            user.set_password(form_password)
            if user.fs_uniquifier is None:
                user.fs_uniquifier = uuid.uuid4().hex
            db_session.add(user)
            db_session.commit()
        except:
            raise DatabaseWriterError()

    def login_user_in_account(user):
        try:
            user.authenticated = True
            db_session.add(user)
            db_session.commit()
        except:
            raise DatabaseWriterError()

    def logout_user_from_account(user):
        try:
            user.authenticated = False
            db_session.add(user)
            db_session.commit()
        except:
            raise DatabaseWriterError()

    def edit_user_data(user, firstname, lastname, password, email, nick):
        try:
            user.firstname = firstname
            user.lastname = lastname
            user.password = password
            user.email = email
            user.nick = nick
            db_session.commit()
        except:
            raise DatabaseWriterError()

    def delete_user(user):
        try:
            db_session.delete(user)
            db_session.commit()
        except:
            raise DatabaseWriterError()


class FileWriter:

    def save_file(file):
        try:
            upload = UploadFile(filename=file.filename,
                                data=file.read())
            db_session.add(upload)
            db_session.commit()
        except:
            raise DatabaseWriterError()


class GameWriter:

    def save_game_data(form_id, form_discipline, form_game_name, form_game_phase, form_team_1, form_team_2, form_game_day, form_game_time):
        try:
            game = Game(id=form_id,
                        discipline=form_discipline,
                        game_name=form_game_name,
                        game_phase=form_game_phase,
                        team_1=form_team_1,
                        team_2=form_team_2,
                        game_day=form_game_day,
                        game_time=form_game_time,
                        )
            db_session.add(game)
            db_session.commit()
        except:
            raise DatabaseWriterError()

    def edit_game_data(edit_game, discipline, tournament, phase, name_team_1, name_team_2, game_date, game_time, finished):
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
        except:
            raise DatabaseWriterError()

    def save_game_winner(edit_game, winner):
        try:
            edit_game.winner = winner
            db_session.commit()
        except:
            raise DatabaseWriterError()

    def save_edited_game(edit_game, discipline, tournament, phase):
        try:
            edit_game.game_discipline = discipline
            edit_game.tournament = tournament
            edit_game.game_phase = phase
            db_session.commit()
        except:
            raise DatabaseWriterError()

    def delete_game(game):
        try:
            db_session.delete(game)
            db_session.commit()
        except:
            raise DatabaseWriterError()


class BetWriter:

    def save_points_from_bet(bet, points):
        try:
            bet.bet_points = points
            db_session.commit()
        except:
            raise DatabaseWriterError()


class GamePlayedWriter:

    def save_game_played(game_id, team_id):
        try:
            game_played_team = GamesPlayed(
                game_id=game_id,
                team_id=team_id)
            db_session.add(game_played_team)
            db_session.commit()
        except:
            raise DatabaseWriterError()
