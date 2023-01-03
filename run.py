from game_app import app, database, config


if __name__ == '__main__':
    with app.app_context():
        configuration = config.Config()
        database.init_db()
    app.run(host=configuration.HOST, port=configuration.PORT,
            debug=configuration.DEBUG)
