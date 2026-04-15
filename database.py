from sqlalchemy import create_engine
from sqlalchemy.orm import Session, DeclarativeBase

DATABASE_URL="postgresql://postgres:postgres123@localhost/postgres"
engine=create_engine(DATABASE_URL)


class Base(DeclarativeBase):
    pass

def get_db():
    db=Session(engine)
    try:
        yield db
    finally:
        db.close()

    