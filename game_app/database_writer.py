import uuid

from game_app.database import db_session
from game_app.my_error import DatabaseWriterError
from game_app.models import User


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
