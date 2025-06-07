from fastapi.security.api_key import APIKeyHeader
from fastapi import Depends, FastAPI, HTTPException, status, File, UploadFile, Form
from sqlmodel import Session, select
from starlette.staticfiles import StaticFiles
import shutil
from pathlib import Path
from core.database import engine
from core.models import Identifier
import uuid
from pydantic import BaseModel
from typing import Optional
import os

os.makedirs("static/images", exist_ok=True)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


class IdentifierCreate(BaseModel):
    rfid: str
    name: str
    access: bool = False
    image_path: Optional[str] = None


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
            detail={"error": f"Identifier with RFID {rfid_id} not found", "rfid": rfid_id}
        )

    return result


@app.post("/identifier", response_model=Identifier)
async def create_identifier(
        rfid: str = Form(...),
        name: str = Form(...),
        access: bool = Form(False),
        image: UploadFile = File(None),
        db: Session = Depends(get_db)
):
    statement = select(Identifier).where(Identifier.rfid == rfid)
    existing = db.exec(statement).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Identifier with RFID {rfid} already exists"
        )

    identifier_data = {"rfid": rfid, "name": name, "access": access}

    if image and image.filename:
        # Generate unique filename
        filename = f"{uuid.uuid4()}_{image.filename}"
        file_path = Path(f"static/images/{filename}")

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        identifier_data["image_path"] = f"/static/images/{filename}"

    new_identifier = Identifier(**identifier_data)
    db.add(new_identifier)
    db.commit()
    db.refresh(new_identifier)
    return new_identifier
