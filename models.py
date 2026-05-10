from sqlalchemy import Column, Integer, String, Boolean
from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

class User(Base):
    __tablename__ = "users"  #nome da tabela no postgres

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_organizer = Column(Boolean, default=False)

from sqlalchemy import ForeignKey # Adicione esta importação no topo
from sqlalchemy.orm import relationship

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    date = Column(String) # Para simplificar, usaremos String por enquanto
    slots = Column(Integer, default=20) # Total de vagas
    owner_id = Column(Integer, ForeignKey("users.id")) # Liga o evento a um usuário

    owner = relationship("User") # Permite acessar o criador do evento facilmente

class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_id = Column(Integer, ForeignKey("events.id"))