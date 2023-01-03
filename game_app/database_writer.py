from game_app.database import db_session


class DatabaseWriter:

    def sort_team_table(group_list):
        for group in group_list:
            i = 1
            for team in group:
                team.group_position = i
                db_session.commit()
                i += 1
