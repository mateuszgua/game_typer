# from game_app import app as application
# 
# if __name__ == "__main__":
    # application.run()

from game_app import app as application
from game_app import database, config


if __name__ == '__main__':
    with application.app_context():
        configuration = config.Config()
        database.init_db()
    application.run(host=configuration.HOST, port=configuration.PORT, debug=configuration.DEBUG)