from pydantic import BaseModel, EmailStr
from datetime import date

class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: date
    additional_info: str | None = None

class ContactUpdate(ContactCreate):
    pass

class ContactResponse(ContactCreate):
    id: int

    class Config:
        from_attributes = True  # Замість orm_mode = True

