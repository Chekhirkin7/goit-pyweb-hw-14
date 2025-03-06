from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import app_hw as repositories_app_hw
from src.schemas.app_hw import ContactSchema, ContactResponse
from src.services.auth import auth_service
from src.entity.models import User

router = APIRouter(prefix="/app_hw", tags=["app_hw"])


@router.get("/", response_model=list[ContactResponse])
def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = (Query(0, ge=0)), db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    contacts = repositories_app_hw.get_contacts(limit, offset, db, user.id)
    return contacts


@router.get("/birthdays", response_model=list[ContactResponse])
def get_birthdays(
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)  # 🔒 Авторизація
):
    contacts = repositories_app_hw.get_upcoming_birthdays(db, user.id)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No upcoming birthdays found")
    return contacts

@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact_by_id(
    contact_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)  # 🔒 Авторизація
):
    contact = repositories_app_hw.get_contact_by_id(contact_id, db)
    if contact is None or contact.id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found or access denied")
    return contact

@router.get("/first_name/{first_name}", response_model=list[ContactResponse])
def get_contact_by_firstname(
    first_name: str,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)  # 🔒 Авторизація
):
    contacts = repositories_app_hw.get_contact_by_firstname(first_name, db, user.id)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No contacts found with this first name")
    return contacts

@router.get("/last_name/{last_name}", response_model=list[ContactResponse])
def get_contact_by_lastname(
    last_name: str,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)  # 🔒 Авторизація
):
    contacts = repositories_app_hw.get_contact_by_lastname(last_name, db, user.id)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No contacts found with this last name")
    return contacts

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def add_contact(
    body: ContactSchema,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)  # 🔒 Авторизація
):
    contact = repositories_app_hw.add_contact(body, db, user.id)
    return contact

@router.put("/{contact_id}")
def update_contact(
    body: ContactSchema,
    contact_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)  # 🔒 Авторизація
):
    contact = repositories_app_hw.get_contact_by_id(contact_id, db)
    if contact is None or contact.id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found or access denied")

    contact = repositories_app_hw.update_contact(contact_id, body, db)
    return contact

@router.delete("/{contact_id}")
def delete_contact(
    contact_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)  # 🔒 Авторизація
):
    contact = repositories_app_hw.get_contact_by_id(contact_id, db)
    if contact is None or contact.id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found or access denied")

    repositories_app_hw.delete_contact(contact_id, db)
    return contact