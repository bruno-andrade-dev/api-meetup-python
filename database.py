import os
from contextlib import contextmanager
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Recupera as credenciais de forma segura
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

# endereço do banco do docker (montado dinamicamente)
SQLALCHEMY_DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

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
