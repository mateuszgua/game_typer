import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from sqlalchemy_utils import database_exists, create_database

from dotenv import load_dotenv


load_dotenv()
USERNAME = os.getenv('MYSQL_USERNAME')
PASSWORD = os.getenv('MYSQL_PASSWORD')
HOST = os.getenv('MYSQL_HOST')
DB_NAME = os.getenv('MYSQL_DB_NAME')
TABLE_NAME = os.getenv('MYSQL_TABLE_NAME')
url = f"mysql+mysqlconnector://{USERNAME}:{PASSWORD}@{HOST}/{DB_NAME}"

engine = create_engine(url, echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    if not database_exists(engine.url):
        create_database(engine.url)

    import models
    Base.metadata.create_all(engine)
