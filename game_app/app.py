import os
from flask import Flask
from flask import render_template
from flask import url_for
from flask import redirect

from flask_settings import Config
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv


app = Flask(__name__, instance_relative_config=False)
app.config.from_object('flask_settings.Config')


@app.route('/')
def main():
    return render_template('index.html')


if __name__ == '__main__':
    config = Config()
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
