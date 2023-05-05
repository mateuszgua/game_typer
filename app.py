from app import application, database, config


if __name__ == '__main__':
    with application.app_context():
        configuration = config.Config()
        database.init_db()
    application.run(host=configuration.HOST, port=configuration.PORT, debug=configuration.DEBUG)
