import os
from datetime import datetime, timedelta, date, time

from game_app.my_error import ImagesNotExist, TeamsDatabaseEmpty
from game_app.database_reader import TeamReader, GameReader


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

    def list_next_games():
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