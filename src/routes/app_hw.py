from fastapi import APIRouter, HTTPException, Depends, status, Path, Query, UploadFile, File
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.repository import app_hw as repositories_app_hw
from src.schemas.app_hw import ContactSchema, ContactResponse
from src.schemas.user import UserResponse
from src.services.auth import auth_service
from src.entity.models import User
from src.repository import app_hw as repositories_hw

import cloudinary
import cloudinary.uploader
from src.conf.config import config

router = APIRouter(prefix="/app_hw", tags=["app_hw"])
cloudinary.config(cloud_name=config.CLD_NAME, api_key=config.CLD_API_KRY, api_secret=config.CLD_API_SECRET, secure=True)

@router.get("/", response_model=list[ContactResponse])
def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Get a list of contacts.
    :param limit:
    :param offset:
    :param db:
    :param user:
    :return:
    """

    contacts = repositories_app_hw.get_contacts(limit, offset, db, user.id)
    return contacts


@router.get("/birthdays", response_model=list[ContactResponse])
def get_birthdays(
        db: Session = Depends(get_db),
        user: User = Depends(auth_service.get_current_user)
):
    """
    Get a list of upcoming birthdays.
    :param db:
    :param user:
    :return:
    """

    contacts = repositories_app_hw.get_upcoming_birthdays(db, user.id)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No upcoming birthdays found")
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact_by_id(
        contact_id: int,
        db: Session = Depends(get_db),
        user: User = Depends(auth_service.get_current_user)
):
    """
    Get a contact by ID.
    :param contact_id:
    :param db:
    :param user:
    :return:
    """

    contact = repositories_app_hw.get_contact_by_id(contact_id, db, user.id)
    if contact is None or contact.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found or access denied")
    return contact


@router.get("/first_name/{first_name}", response_model=list[ContactResponse])
def get_contact_by_firstname(
        first_name: str,
        db: Session = Depends(get_db),
        user: User = Depends(auth_service.get_current_user)
):
    """
    Get a list of contacts by first name.
    :param first_name:
    :param db:
    :param user:
    :return:
    """

    contacts = repositories_app_hw.get_contact_by_firstname(first_name, db, user.id)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No contacts found with this first name")
    return contacts


@router.get("/last_name/{last_name}", response_model=list[ContactResponse])
def get_contact_by_lastname(
        last_name: str,
        db: Session = Depends(get_db),
        user: User = Depends(auth_service.get_current_user)
):
    """
    Get a list of contacts by last name.
    :param last_name:
    :param db:
    :param user:
    :return:
    """

    contacts = repositories_app_hw.get_contact_by_lastname(last_name, db, user.id)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No contacts found with this last name")
    return contacts


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def add_contact(
        body: ContactSchema,
        db: Session = Depends(get_db),
        user: User = Depends(auth_service.get_current_user)
):
    """
    Add a new contact.
    :param body:
    :param db:
    :param user:
    :return:
    """

    contact = repositories_app_hw.add_contact(body, db, user.id)
    return contact

@router.patch(
    "/{contact_id}/avatar",
    response_model=ContactResponse
)
def add_avatar(
    contact_id: int = Path(ge=1),
    file: UploadFile = File(...),
    user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update contact avatar.
    :param contact_id:
    :param file:
    :param user:
    :param db:
    :return:
    """
    contact = repositories_hw.get_contact_by_id(contact_id, db, user.id)
    if contact is None or contact.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found or access denied")

    # Перевірка Cloudinary API Key
    if not cloudinary.config().api_key:
        raise ValueError("❌ Cloudinary API Key is missing!")

    # Завантажуємо зображення у Cloudinary
    public_id = f"ContactsAvatars/{contact.id}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)

    # Отримуємо URL нового аватара
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )

    # Оновлюємо запис контакту в базі даних
    updated_contact = repositories_hw.add_avatar_url(contact.id, res_url, db)
    return updated_contact


@router.put("/{contact_id}")
def update_contact(
        body: ContactSchema,
        contact_id: int = Path(ge=1),
        db: Session = Depends(get_db),
        user: User = Depends(auth_service.get_current_user)
):
    """
    Update a contact by ID.
    :param body:
    :param contact_id:
    :param db:
    :param user:
    :return:
    """

    contact = repositories_app_hw.get_contact_by_id(contact_id, db, user.id)
    if contact is None or contact.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found or access denied")

    contact = repositories_app_hw.update_contact(contact_id, body, db, user.id)
    return contact


@router.delete("/{contact_id}")
def delete_contact(
        contact_id: int = Path(ge=1),
        db: Session = Depends(get_db),
        user: User = Depends(auth_service.get_current_user)
):
    """
    Delete a contact by ID.
    :param contact_id:
    :param db:
    :param user:
    :return:
    """

    contact = repositories_app_hw.get_contact_by_id(contact_id, db, user.id)
    if contact is None or contact.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found or access denied")

    repositories_app_hw.delete_contact(contact_id, db, user.id)
    return contact
