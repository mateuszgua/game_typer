from datetime import datetime, timedelta, date, time

from game_app.forms import RegistrationForm, LoginForm, EditUserForm, AddGameForm, AddGroupForm
from game_app.models import User, Role, Team, UserAdminView, RoleAdminView, UploadFile, Game, Tip, UserTournaments, GamesPlayed, BetGroup, UserBetGroup
from game_app.my_error import TeamsDatabaseEmpty, GameNotExist


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

    def list_last_games():
        present = date.today()
        i = 1
        day_yesterday = present - timedelta(days=i)

        last_games = Game.query.filter_by(
            game_day=day_yesterday).order_by(Game.game_time.asc()).all()
        if last_games is None:
            raise Exception('No any game in last day')
        else:
            return last_games

    def list_current_games():
        present = date.today()

        current_games = Game.query.filter_by(
            game_day=present).order_by(Game.game_time.asc()).all()
        if current_games is None:
            raise Exception('No any game in current day')
        else:
            return current_games

    def list_next_games():
        present = date.today()
        i = 1
        number_of_games = 64
        day_tommorow = present + timedelta(days=i)

        while Game.query.filter_by(game_day=day_tommorow).count() == 0:
            day_tommorow += timedelta(days=i)
            number_of_games -= i
            if number_of_games == 0:
                break

        next_games = Game.query.filter_by(
            game_day=day_tommorow).order_by(Game.game_time.asc()).all()
        if next_games is None:
            raise Exception('No any game in next day')
        else:
            return next_games
