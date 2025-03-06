from datetime import date, timedelta

from sqlalchemy import select, func
from sqlalchemy.orm import Session
from src.entity.models import Contact
from src.schemas.app_hw import ContactSchema


def get_contacts(limit: int, offset: int, db: Session, user_id: int):
    stmt = select(Contact).offset(offset).limit(limit).filter_by(id=user_id)
    contacts = db.execute(stmt)
    return contacts.scalars().all()


def get_contact_by_id(contact_id: int, db: Session):
    stmt = select(Contact).filter_by(id=contact_id)
    contact = db.execute(stmt)
    return contact.scalar_one_or_none()


def get_contact_by_firstname(first_name: str, db: Session, user_id: int):
    stmt = select(Contact).filter_by(first_name=first_name, id=user_id)
    result = db.execute(stmt)
    return result.scalars().all()


def get_upcoming_birthdays(db: Session, user_id: int):
    today = date.today()
    next_week = today + timedelta(days=7)

    stmt = select(Contact).where(
        (func.to_char(Contact.date_of_birth, 'MM-DD') >= today.strftime('%m-%d')) &
        (func.to_char(Contact.date_of_birth, 'MM-DD') <= next_week.strftime('%m-%d')) &
        (Contact.id == user_id)
    )

    result = db.execute(stmt)
    contacts = result.scalars().all()

    return contacts


def get_contact_by_lastname(last_name: str, db: Session, user_id: int):
    stmt = select(Contact).filter_by(last_name=last_name, id=user_id)
    result = db.execute(stmt)
    return result.scalars().all()


def add_contact(body: ContactSchema, db: Session, user_id: int):
    contact = Contact(**body.model_dump(exclude_unset=True), id=user_id)  # 👈 Додаємо owner_id
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def update_contact(contact_id: int, body: ContactSchema, db: Session):
    stmt = select(Contact).filter_by(id=contact_id)
    result = db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.date_of_birth = body.date_of_birth
        contact.description = body.description
        db.commit()
        db.refresh(contact)
    return contact


def delete_contact(contact_id: int, db: Session):
    stmt = select(Contact).filter_by(id=contact_id)
    result = db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        db.delete(contact)
        db.commit()
    return contact
