from fastapi.security.api_key import APIKeyHeader
from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import Session, select
from core.database import engine
from core.models import Identifier
import uuid
from pydantic import BaseModel

app = FastAPI()

class IdentifierCreate(BaseModel):
    rfid: str
    name: str
    access: bool = False

def get_db():
    with Session(engine) as session:
        yield session

@app.get("/identifier/{rfid_id}")
async def identifier(rfid_id: str, db: Session = Depends(get_db)):
    statement = select(Identifier).where(Identifier.rfid == rfid_id)
    result = db.exec(statement).first()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = { "error": f"Identifier with RFID {rfid_id} not found", "rfid": rfid_id }
        )

    return result


@app.post("/identifier", response_model=Identifier)
async def create_identifier(identifier_data: IdentifierCreate, db: Session = Depends(get_db)):
    # Check if RFID already exists
    statement = select(Identifier).where(Identifier.rfid == identifier_data.rfid)
    existing = db.exec(statement).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Identifier with RFID {identifier_data.rfid} already exists"
        )

    # Create new identifier
    new_identifier = Identifier(**identifier_data.dict())
    db.add(new_identifier)
    db.commit()
    db.refresh(new_identifier)
    return new_identifier

