import os
from click import DateTime
from dotenv import load_dotenv
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy_utils import database_exists
from sqlalchemy_utils import create_database

load_dotenv()
USERNAME = os.getenv('MYSQL_USERNAME')
PASSWORD = os.getenv('MYSQL_PASSWORD')
HOST = os.getenv('MYSQL_HOST')
DB_NAME = os.getenv('MYSQL_DB_NAME')
TABLE_NAME = os.getenv('MYSQL_TABLE_NAME')


class MyDatabase:
    url = f"mysql://{USERNAME}:{PASSWORD}@{HOST}/{DB_NAME}"

    engine = create_engine(url, echo=True)

    if not database_exists(engine.url):
        create_database(engine.url)

    else:
        engine.connect()

    if not engine.dialect.has_table(engine, TABLE_NAME):
        metadata = MetaData(engine)
        Table(TABLE_NAME, metadata,
              Column('Id', Integer, primary_key=True, nullable=False),
              Column('Firstname', String(100), nullable=False),
              Column('Lastname', String(100), nullable=False),
              Column('Nick', String(100), nullable=False, unique=True),
              Column('Email', String(100), nullable=False),
              Column('Created_at', DateTime(timezone=True),
                     server_default=func.now(), nullable=False),
              )
        metadata.create_all()
