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


# Dependência para pegar uma conexão com o banco
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Verifica se o usuário já existe
    user_db = db.query(models.User).filter(models.User.email == user.email).first()
    if user_db:
        raise HTTPException(status_code=400, detail="Este email já está cadastrado")
    
    # 2. Cria o novo usuário (Ainda sem criptografar a senha, faremos isso no passo de segurança!)
    new_user = models.User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=get_password_hash(user.password), #cript aqui
        is_organizer=user.is_organizer
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # busca o usuario pelo email (o auth2 usa o campo 'username')
    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    # verifica se o user existe e se a senha bate
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="E-mail ou senha incorretos")

    # cria o token de acesso
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# função para validar quem é o usuario do token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        # decodifica o token usando a mesma chave security.py
        payload = jwt.decode(token, "sua_chave_secreta_aqui", algorithms=["HS256"])
        email: str = payload.get("sub")
        user = db.query(models.User).filter(models.User.email == email).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")
        return user
    except:
        raise HTTPException(status_code=401, detail="Token Inválido ou expirado.")
    
# rota protegida: so cria evento se passar um user valido
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
    skip: int = 0, # Quantos eventos pular (offset)
    limit: int = 10, # Quantos eventos mostrar por página
    search: str = ""
):

    query = db.query(models.Event)
    if search:
        query = query.filter(models.Event.title.ilike(f"%{search}%"))
    
    events = query.offset(skip).limit(limit).all()
    return events

    # O SQLAlchemy faz a mágica aqui com .offset() e .limit()
    events = db.query(models.Event).offset(skip).limit(limit).all()
    return events

@app.put("/events/{event_id}", response_model=schemas.EventOut)
def update_event(
    event_id: int,
    event_update: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # busca o evento no banco
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()

    # erro 404 (se n exister)
    if not db_event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # verificar se o usuário é o dono do evento
    if db_event.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para editar este evento")
    
    # atualiza os campos do evento
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
    
    # so o dono apaga
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
    #verificar se o evento existe
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # verificar se o usuario ja esta registrado no evento
    already_registered = db.query(models.Registration).filter(
        models.Registration.user_id == current_user.id,
        models.Registration.event_id == event_id
    ).first()
    if already_registered:
        raise HTTPException(status_code=400, detail="Você já está registrado neste evento")
    
    # verificar se ainda tem vagas no evento
    count = db.query(models.Registration).filter(models.Registration.event_id == event_id).count()
    if count >= event.slots:
        raise HTTPException(status_code=400, detail="Evento lotado!")
    
    #faz a inscrição
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