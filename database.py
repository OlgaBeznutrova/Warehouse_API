from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker

from settings import settings

engine = create_engine(
    f"mysql+pymysql://{settings.db_user}:{settings.db_password}@localhost/{settings.db_name}",
    # echo=True
)

Session = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)


def get_session() -> Session:
    session = Session()
    try:
        yield session
    finally:
        session.close()
