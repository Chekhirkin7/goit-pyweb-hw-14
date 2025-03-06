from pydantic import BaseModel, EmailStr, Field
from datetime import date


class ContactSchema(BaseModel):
    first_name: str = Field(min_length=3, max_length=25)
    last_name: str = Field(min_length=3, max_length=25)
    email: str = Field()
    phone_number: str = Field(min_length=5, max_length=20)
    date_of_birth: date
    description: str = Field()


class ContactResponse(BaseModel):
    id: int = 1
    first_name: str
    last_name: str
    email: str
    phone_number: str
    date_of_birth: date
    description: str

    class Config:
        from_attributes = True
