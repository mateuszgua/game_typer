from game_app.database import db_session
from game_app.my_error import DatabaseWriterError


class DatabaseWriter:

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
