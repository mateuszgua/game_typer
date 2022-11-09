import os
from flask import Flask
from flask import render_template
from flask import url_for
from flask import redirect
from flask import request

from flask_sqlalchemy import SQLAlchemy
from flask_settings import Config
from sqlalchemy.sql import func

from dotenv import load_dotenv

load_dotenv()
USERNAME = os.getenv('MYSQL_USERNAME')
PASSWORD = os.getenv('MYSQL_PASSWORD')
HOST = os.getenv('MYSQL_HOST')
DB_NAME = os.getenv('MYSQL_DB_NAME')
TABLE_NAME = os.getenv('MYSQL_TABLE_NAME')
url = f"mysql+mysqlconnector://{USERNAME}:{PASSWORD}@{HOST}/{DB_NAME}"

app = Flask(__name__, instance_relative_config=False)
app.config.from_object('flask_settings.Config')
app.config['SQLALCHEMY_DATABASE_URI'] = url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    nick = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f'<User {self.firstname}'


@app.route('/')
def index():
    users = User.query.all()

    return render_template('index.html', users=users)


@app.route('/<int:user_id>/')
def user(user_id):
    user = User.query.get_or_404(user_id)

    return render_template('user.html', user=user)


@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        nick = request.form['nick']
        user = User(firstname=firstname,
                    lastname=lastname,
                    email=email,
                    nick=nick)
        db.session.add(user)
        db.session.commit()

    return render_template('create.html')


@app.route('/<int:user_id>/edit/', methods=('GET', 'POST'))
def edit(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        nick = request.form['nick']

        user.firstname = firstname
        user.lastname = lastname
        user.email = email
        user.nick = nick

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('edit.html', user=user)


@app.post('/<int:user_id>/delete/')
def delete(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('index'))


if __name__ == '__main__':
    config = Config()
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
