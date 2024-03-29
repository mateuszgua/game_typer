from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy_utils import database_exists, create_database

from app.config import url

engine = create_engine(url, pool_pre_ping=True, echo=True,
                       pool_size=40, max_overflow=0)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    if not database_exists(engine.url):
        create_database(engine.url)

    import app.models
    Base.metadata.create_all(engine)
