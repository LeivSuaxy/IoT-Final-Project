from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security.api_key import APIKeyHeader
from fastapi import Depends, FastAPI, HTTPException, status, File, UploadFile, Form
from jose import JWTError
from sqlmodel import Session, select
from starlette.staticfiles import StaticFiles
import shutil
from pathlib import Path
from core.database import engine
from core.models import Identifier, User
from core.security import *
import uuid
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

os.makedirs("static/images", exist_ok=True)

def get_db():
    with Session(engine) as session:
        yield session

class IdentifierCreate(BaseModel):
    rfid: str
    name: str
    access: bool = False
    image_path: Optional[str] = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

api_key_header = APIKeyHeader(name="X-API-Key")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError as e:
        print(e)
        raise credentials_exception

    statement = select(User).where(User.username == username)
    user = db.exec(statement).first()
    if user is None:
        raise credentials_exception

    return user

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions - admin access required"
        )
    return current_user


# APP
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    statement = select(User).where(User.username == form_data.username)
    user = db.exec(statement).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/register", response_model=User)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if username exists
    statement = select(User).where(User.username == user_data.username)
    if db.exec(statement).first():
        raise HTTPException(status_code=400, detail="Username already registered")

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Remove password from response
    return new_user


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
        db: Session = Depends(get_db),
        admin_user: User = Depends(get_admin_user),
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
