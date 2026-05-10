from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

# endereço do banco do docker
SQLALCHEMY_DATABASE_URL = "postgresql://user_meetup:password_123@localhost:5432/db_meetup"

# o motor dos comandos
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# fabrica de sessoes (abre e fecha conversas com o banco)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# clases base para os modelos
Base = declarative_base()

@contextmanager
def get_db_context():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()