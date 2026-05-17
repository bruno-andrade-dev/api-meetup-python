from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, database
from security import get_password_hash
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from security import verify_password, create_access_token
import jwt
from typing import List
import time
from fastapi import Request

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Meetup API")

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API de Meetups! Acesse /docs para testar."}


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    user_db = db.query(models.User).filter(models.User.email == user.email).first()
    if user_db:
        raise HTTPException(status_code=400, detail="Este email já está cadastrado")
    

    new_user = models.User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        is_organizer=user.is_organizer
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="E-mail ou senha incorretos")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:

        payload = jwt.decode(token, "sua_chave_secreta_aqui", algorithms=["HS256"])
        email: str = payload.get("sub")
        user = db.query(models.User).filter(models.User.email == email).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")
        return user
    except:
        raise HTTPException(status_code=401, detail="Token Inválido ou expirado.")
    
@app.post("/events", response_model=schemas.EventOut)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
   new_event = models.Event(**event.model_dump(), owner_id=current_user.id)
   db.add(new_event)
   db.commit()
   db.refresh(new_event)
   return new_event

@app.get("/events", response_model=List[schemas.EventOut])
def list_events(
    db: Session = Depends(get_db), 
    skip: int = 0,
    limit: int = 10,
    search: str = ""
):

    query = db.query(models.Event)
    if search:
        query = query.filter(models.Event.title.ilike(f"%{search}%"))
    
    events = query.offset(skip).limit(limit).all()
    return events

    events = db.query(models.Event).offset(skip).limit(limit).all()
    return events

@app.put("/events/{event_id}", response_model=schemas.EventOut)
def update_event(
    event_id: int,
    event_update: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()

    if not db_event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    if db_event.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para editar este evento")
    
    db_event.title = event_update.title
    db_event.description = event_update.description
    db_event.date = event_update.date

    db.commit()
    db.refresh(db_event)
    return db_event

@app.delete("/events/{event_id}")
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()

    if not db_event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    if db_event.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Você é um safado e não tem permissão para deletar os eventos de outros")
    
    db.delete(db_event)
    db.commit()
    return {"message": f"Evento {event_id} removido com sucesso!"}

@app.post("/events/{event_id}/register")
def register_for_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    already_registered = db.query(models.Registration).filter(
        models.Registration.user_id == current_user.id,
        models.Registration.event_id == event_id
    ).first()
    if already_registered:
        raise HTTPException(status_code=400, detail="Você já está registrado neste evento")
    
    count = db.query(models.Registration).filter(models.Registration.event_id == event_id).count()
    if count >= event.slots:
        raise HTTPException(status_code=400, detail="Evento lotado!")
    
    new_registration = models.Registration(user_id=current_user.id, event_id=event_id)
    db.add(new_registration)
    db.commit()

    return {"message": f"inscrição confirmada no evento: {event.title}"}

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response