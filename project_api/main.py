from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
from models import Contact
from schemas import ContactCreate, ContactResponse, ContactUpdate
from datetime import date, timedelta

app = FastAPI()

# Ініціалізація бази даних
Base.metadata.create_all(bind=engine)

# Залежність для роботи з базою даних
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD операції
@app.post("/contacts/", response_model=ContactResponse)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    db_contact = Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

@app.get("/contacts/", response_model=list[ContactResponse])
def get_contacts(
    name: str | None = Query(None), email: str | None = Query(None), db: Session = Depends(get_db)
):
    query = db.query(Contact)
    if name:
        query = query.filter(
            (Contact.first_name.contains(name)) | (Contact.last_name.contains(name))
        )
    if email:
        query = query.filter(Contact.email.contains(email))
    return query.all()

@app.get("/contacts/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@app.put("/contacts/{contact_id}", response_model=ContactResponse)
def update_contact(contact_id: int, contact: ContactUpdate, db: Session = Depends(get_db)):
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    for key, value in contact.dict().items():
        setattr(db_contact, key, value)
    db.commit()
    db.refresh(db_contact)
    return db_contact

@app.delete("/contacts/{contact_id}", response_model=dict)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(db_contact)
    db.commit()
    return {"detail": "Contact deleted"}

@app.get("/contacts/upcoming-birthdays/", response_model=list[ContactResponse])
def get_upcoming_birthdays(db: Session = Depends(get_db)):
    today = date.today()
    next_week = today + timedelta(days=7)
    contacts = db.query(Contact).filter(Contact.birthday.between(today, next_week)).all()
    return contacts
