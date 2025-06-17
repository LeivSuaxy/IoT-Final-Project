from sqlmodel import SQLModel, Field
import uuid
from typing import Optional
from datetime import datetime

class Identifier(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    rfid: str = Field(
        index=True,
        nullable=False,
    )
    name: str = Field(
        nullable=False,
    )
    access: bool = Field(
        default=False,
        nullable=False,
    )
    image_path: Optional[str] = Field(
        default=None,
        nullable=True
    )

class User(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)

class PassRegister(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    rfid: str = Field(
        index=True,
        nullable=False,
    )
    date: datetime = Field(
        default_factory=datetime.now,
        nullable=False,
    )

