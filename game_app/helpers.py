import os

from game_app.my_error import ImagesNotExist, TeamsDatabaseEmpty
from game_app.database_reader import TeamReader


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
