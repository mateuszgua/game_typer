import os
from datetime import datetime, timedelta, date
from flask import json

from game_app.my_error import ImagesNotExist, TeamsDatabaseEmpty
from game_app.database_reader import TeamReader, GameReader, FilesReader, BetReader, GamesPlayedReader, UserBetGroupReader
from game_app.database_writer import GameWriter, TeamWriter, BetWriter, GamePlayedWriter, UserBetGroupWriter, UserWriter


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

        last_games = GameReader.get_all_games_by_day_order(day_yesterday)
        return last_games

    def get_list_current_games():
        current_day = date.today()

        current_games = GameReader.get_all_games_by_day_order(current_day)
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

        next_games = GameReader.get_all_games_by_day_order(day_tommorow)
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
        game = GameReader.get_one_game_filter("id", game_id)
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

    def is_date_locked(bet_id):
        game = GameReader.get_one_game_filter("id", bet_id)
        game_day = game.game_day
        game_time = game.game_time

        present = datetime.now()
        string_date_time = f"{game_day} {game_time}"
        date_time = datetime.strptime(string_date_time, "%Y-%m-%d %H:%M:%S")

        if present >= date_time:
            lock_tip(bet_id)
            return True

    def is_tournament_exist(tournament_name, user):
        for tournament in user.tournaments:
            if tournament_name == tournament.tournament:
                return True

    def bet_winner(edit_bet):
        if edit_bet.bet_goals_team_1 > edit_bet.bet_goals_team_2:
            winner = 1
        elif edit_bet.bet_goals_team_1 < edit_bet.bet_goals_team_2:
            winner = 2
        else:
            winner = 0
        return winner

    def sort_users_in_group(user_groups):
        place = 1
        for user_group in user_groups:
            UserBetGroupWriter.save_user_place(user_group, place)
            place += 1

    def find_last_game():
        present_day = date.today()
        present = datetime.now()
        present_time = present.strftime("%H:%M:%S")
        i = 1
        j = 1
        game_day = present_day

        while GameReader.get_games_by_day_count(game_day) == 0:
            game_day -= timedelta(days=i)
            j += 1
            if j > 365:
                break

        if game_day == present_day:
            game = GameReader.get_one_game_filter_order_asc(
                "game_day", game_day)
            if game.game_time >= present_time:
                game_id = game.id - 1
                game = GameReader.get_one_game_filter("id", game_id)
        else:
            game = GameReader.get_one_game_filter_order_desc(
                "game_day", game_day)
        return game

    def update_user_points(user_groups):
        for user in user_groups:
            user.points = 0

            user_bets = BetReader.get_all_bets_filter("user_id", user.user_id)
            for user_bet in user_bets:
                UserWriter.update_bet_points(user_bet, user)

    def add_user_to_group_if_not_exist(user, group_id):
        if UserBetGroupReader.get_count_user_group_filter("user_id", user.id) == 0:
            UserBetGroupWriter.save_user_bet_group(group_id, user.id)
            message = "User added successfully!"
        else:
            message = "User exist in group!"
        return message


def is_game_played_exist(edit_game, games_played):
    for game_played in games_played:
        if edit_game.id == game_played.game_id:
            return True


def fill_teams_table(edit_game, team_1, team_2):
    GameWriter.edit_game_data(edit_game, team_1, team_2)


def lock_tip(bet_id):
    edit_bet = BetReader.get_all_bets_filter("game_id", bet_id)
    for bet in edit_bet:
        lock = 1
        BetWriter.edit_lock_bet(bet, lock)
