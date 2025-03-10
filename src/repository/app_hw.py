from datetime import date, timedelta

from sqlalchemy import select, func
from sqlalchemy.orm import Session
from src.entity.models import Contact
from src.schemas.app_hw import ContactSchema


def get_contacts(limit: int, offset: int, db: Session, user_id: int):
    """
    Get contacts based on the provided parameters.

    :param limit: Maximum number of contacts to return.
    :param offset: Number of contacts to skip before returning results.
    :param db: SQLAlchemy session object.
    :param user_id: User ID for filtering contacts.
    :return: List of Contact objects.
    """

    stmt = select(Contact).filter(Contact.owner_id == user_id).offset(offset).limit(limit)
    contacts = db.execute(stmt)
    return contacts.scalars().all()


def get_contact_by_id(contact_id: int, db: Session, user_id: int):
    """
    Get contact by ID and check if it belongs to the provided user.

    :param contact_id: ID of the contact to retrieve.
    :param db: SQLAlchemy session object.
    :param user_id: User ID for filtering contacts.
    :return: Contact object if found, otherwise None.
    """

    stmt = select(Contact).filter(Contact.id == contact_id, Contact.owner_id == user_id)
    contact = db.execute(stmt)
    return contact.scalar_one_or_none()


def get_contact_by_firstname(first_name: str, db: Session, user_id: int):
    """
    Get contact by first name and check if it belongs to the provided user.

    :param first_name: First name of the contact to retrieve.
    :param db: SQLAlchemy session object.
    :param user_id: User ID for filtering contacts.
    :return: Contact object if found, otherwise None.
    """

    stmt = select(Contact).filter(Contact.first_name == first_name, Contact.owner_id == user_id)
    result = db.execute(stmt)
    return result.scalars().all()


def get_contact_by_lastname(last_name: str, db: Session, user_id: int):
    """
    Get contact by last name and check if it belongs to the provided user.

    :param last_name: Last name of the contact to retrieve.
    :param db: SQLAlchemy session object.
    :param user_id: User ID for filtering contacts.
    :return: Contact object if found, otherwise None.
    """

    stmt = select(Contact).filter(Contact.last_name == last_name, Contact.owner_id == user_id)
    result = db.execute(stmt)
    return result.scalars().all()


def get_upcoming_birthdays(db: Session, user_id: int):
    """
    Get contacts with upcoming birthdays within the next week and belonging to the provided user.

    :param db: SQLAlchemy session object.
    :param user_id: User ID for filtering contacts.
    :return: List of Contact objects with upcoming birthdays.
    """
    today = date.today()
    next_week = today + timedelta(days=7)

    stmt = select(Contact).where(
        (func.to_char(Contact.date_of_birth, 'MM-DD') >= today.strftime('%m-%d')) &
        (func.to_char(Contact.date_of_birth, 'MM-DD') <= next_week.strftime('%m-%d')) &
        (Contact.owner_id == user_id)
    )

    result = db.execute(stmt)
    contacts = result.scalars().all()

    return contacts


def add_contact(body: ContactSchema, db: Session, user_id: int):
    """
    Add a new contact to the database.

    :param body:
    :param db:
    :param user_id:
    :return:
    """

    contact = Contact(**body.model_dump(exclude_unset=True), owner_id=user_id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def update_contact(contact_id: int, body: ContactSchema, db: Session, user_id: int):
    """
    Update an existing contact in the database.

    :param contact_id: ID of the contact to update.
    :param body: Updated contact data.
    :param db: SQLAlchemy session object.
    :param user_id: User ID for filtering contacts.
    :return: Updated contact object if found, otherwise None.
    """
    stmt = select(Contact).filter(Contact.id == contact_id, Contact.owner_id == user_id)
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


def delete_contact(contact_id: int, db: Session, user_id: int):
    """
    Delete a contact from the database.

    :param contact_id: ID of the contact to delete.
    :param db: SQLAlchemy session object.
    :param user_id: User ID for filtering contacts.
    :return: Deleted contact object if found, otherwise None.
    """

    stmt = select(Contact).filter(Contact.id == contact_id, Contact.owner_id == user_id)
    result = db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        db.delete(contact)
        db.commit()
    return contact

def add_avatar_url(contact_id: int, url: str, db: Session):
    """
    Add an avatar URL to a contact.

    :param contact_id: ID of the contact to update.
    :param url: Avatar URL.
    :param db: SQLAlchemy session object.
    :return: Updated contact object if found, otherwise None.
    """

    stmt = select(Contact).filter(Contact.id == contact_id)
    result = db.execute(stmt)
    contact = result.scalar_one_or_none()
    contact.avatar = url
    db.commit()
    db.refresh(contact)
    return contact
