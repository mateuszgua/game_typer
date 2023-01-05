import os
from datetime import timedelta, date
from flask import json

from game_app.my_error import ImagesNotExist, TeamsDatabaseEmpty
from game_app.database_reader import TeamReader, GameReader, FilesReader, BetReader, GamesPlayedReader
from game_app.database_writer import GameWriter, TeamWriter, BetWriter, GamePlayedWriter


class Helpers:
    def get_images_list():
        images_list = os.listdir('game_app/static/files')
        images_list = ['files/' + image for image in images_list]
        if images_list is None:
            raise ImagesNotExist()
        else:
            return images_list

    def create_sorted_list():
        group_list = []
        group_A = TeamReader.get_sort_group("A")
        group_list.insert(0, group_A)
        group_B = TeamReader.get_sort_group("B")
        group_list.insert(1, group_B)
        group_C = TeamReader.get_sort_group("C")
        group_list.insert(2, group_C)
        group_D = TeamReader.get_sort_group("D")
        group_list.insert(3, group_D)
        group_E = TeamReader.get_sort_group("E")
        group_list.insert(4, group_E)
        group_F = TeamReader.get_sort_group("F")
        group_list.insert(5, group_F)
        group_G = TeamReader.get_sort_group("G")
        group_list.insert(6, group_G)
        group_H = TeamReader.get_sort_group("H")
        group_list.insert(7, group_H)
        if group_list is None:
            raise TeamsDatabaseEmpty()
        else:
            return group_list

    def get_list_last_games():
        current_day = date.today()
        i = 1
        day_yesterday = current_day - timedelta(days=i)

        last_games = GameReader.get_games_by_day_asc(day_yesterday)
        return last_games

    def get_list_current_games():
        current_day = date.today()

        current_games = GameReader.get_games_by_day_asc(current_day)
        return current_games

    def get_list_next_games():
        present = date.today()
        i = 1
        number_of_games = 64
        day_tommorow = present + timedelta(days=i)

        while GameReader.get_games_by_day_count(day_tommorow) == 0:
            day_tommorow += timedelta(days=i)
            number_of_games -= i
            if number_of_games == 0:
                break

        next_games = GameReader.get_games_by_day_asc(day_tommorow)
        return next_games

    def count_user_points_from_bet(user_bets, user_points):
        for user_bet in user_bets:
            if user_bet.bet_points == None:
                user_points += 0
            else:
                user_points += int(user_bet.bet_points)
        return user_points

    def get_allowed_file(config, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

    def get_process_json(file_idx):
        file = FilesReader.get_file_by_filter(file_idx)
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "static/files", file.filename)
        data = json.load(open(json_url))

        i = 0
        while i < 32:
            TeamWriter.save_team_data(data, i)
            i += 1

    def set_game_winner(edit_game):
        if edit_game.goals_team_1 > edit_game.goals_team_2:
            winner = 1
        elif edit_game.goals_team_1 < edit_game.goals_team_2:
            winner = 2
        else:
            winner = 0
        GameWriter.save_game_winner(edit_game, winner)

    def update_bet_points_from_game(game_id):
        game = GameReader.get_one_game_by_filter("id", game_id)
        bets = BetReader.get_all_bets()

        for bet in bets:
            if bet.game_id == game_id:
                if bet.bet_goals_team_1 != None and bet.bet_goals_team_2 != None:
                    game_difference = game.goals_team_1 - game.goals_team_2
                    bet_difference = bet.bet_goals_team_1 - bet.bet_goals_team_2

                    if bet.bet_goals_team_1 == game.goals_team_1 and bet.bet_goals_team_2 == game.goals_team_2:
                        points = 5
                    elif bet.winner == game.winner and game_difference == bet_difference:
                        points = 3
                    elif bet.winner == game.winner:
                        points = 2
                    else:
                        points = 0
                else:
                    points = 0
                BetWriter.save_points_from_bet(bet, points)

    def update_team_points_from_game(edit_game):
        team_name_1 = edit_game.team_1
        team_name_2 = edit_game.team_2

        team_1 = TeamReader.get_one_team_by_filter(
            "name", team_name_1.lower())
        team_2 = TeamReader.get_one_team_by_filter(
            "name", team_name_2.lower().lower())

        games_played = GamesPlayedReader.get_all_games_played()

        if is_game_played_exist(edit_game, games_played):
            pass
        else:
            if edit_game.game_phase != "group":
                pass
            else:
                fill_teams_table(edit_game, team_1, team_2)
                GamePlayedWriter.save_game_played(edit_game.id, team_1.id)
                GamePlayedWriter.save_game_played(edit_game.id, team_2.id)


def is_game_played_exist(edit_game, games_played):
    for game_played in games_played:
        if edit_game.id == game_played.game_id:
            return True


def fill_teams_table(edit_game, team_1, team_2):
    GameWriter.edit_game_data(edit_game, team_1, team_2)
