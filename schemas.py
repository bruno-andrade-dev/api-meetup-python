from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    is_organizer: Optional[bool] = False

class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    is_organizer: bool

    model_config = {"from_attributes": True}

class EventCreate(BaseModel):
    title: str
    description: str
    date: str
    slots: int = 20
    
class EventOut(BaseModel):
    id: int
    title: str
    description: str
    date: str
    slots: int
    owner_id: int

    model_config = {"from_attributes": True}