from datetime import datetime, timedelta, date, time

from game_app.forms import RegistrationForm, LoginForm, EditUserForm, AddGameForm, AddGroupForm
from game_app.models import User, Role, Team, UserAdminView, RoleAdminView, UploadFile, Game, Tip, UserTournaments, GamesPlayed, BetGroup, UserBetGroup
from game_app.my_error import TeamsDatabaseEmpty, GameNotExist, DatabaseReaderProblem


class TeamReader:

    def get_all_teams():
        teams = Team.query.all()
        if teams is None:
            raise TeamsDatabaseEmpty()
        else:
            return teams

    def get_one_team():
        pass

    def get_sort_group(group_name):
        sorted_group = Team.query.filter_by(
            group=group_name).order_by(Team.points.desc(), Team.goal_balance.desc()).all()
        if sorted_group is None:
            raise DatabaseReaderProblem()
        else:
            return sorted_group


class GameReader:

    def get_all_games():
        pass

    def get_one_game(filter_value_name, filter_value):
        game = Game.query.filter_by(filter_value_name=filter_value).all()
        if game is None:
            raise GameNotExist()
        else:
            return game

    def get_games_by_day_asc(day):
        games = Game.query.filter_by(
            game_day=day).order_by(Game.game_time.asc()).all()
        if games is None:
            raise DatabaseReaderProblem()
        else:
            return games

    def get_games_by_day_count(day):
        games = Game.query.filter_by(game_day=day).count()
        if games is None:
            raise DatabaseReaderProblem()
        else:
            return games
