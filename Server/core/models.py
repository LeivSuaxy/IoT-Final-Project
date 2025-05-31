from sqlmodel import SQLModel, Field
import uuid
from typing import Optional

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
