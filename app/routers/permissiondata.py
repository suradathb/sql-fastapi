from fastapi import APIRouter, Depends, HTTPException,Form, Request, Response
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta


router = APIRouter(
    prefix='/Data Prmission',
    tags=['Geting Data Permission'],
    responses={404:{
        'message':'Not found'
    }}
)

users_db = {}

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Secret key for session
SECRET_KEY = "mysecretkey"

# Session manager
# session_manager = SessionManager(secret_key=SECRET_KEY)

# OAuth2PasswordBearer for token validation
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Custom class for user data
class UserRegister(BaseModel):
    username: str
    password: str

# Define timeout duration in seconds (e.g., 10 minutes)
TIMEOUT_DURATION = 600

# Routes
@router.post("/register/")
async def register_user(user: UserRegister):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = pwd_context.hash(user.password)
    users_db[user.username] = {"username": user.username, "hashed_password": hashed_password}
    return {"message": "User registered successfully"}

@router.post("/token/")
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    session = response.session
    session["username"] = user["username"]
    session["expires"] = datetime.utcnow() + timedelta(seconds=TIMEOUT_DURATION)
    return {"access_token": session.id, "token_type": "bearer"}

@router.post("/logout/")
async def logout(request:Request):
    session = request.session
    session.invalidate()
    return {"message": "Logged out"}

# Custom dependency to get the current user from the session
async def get_current_user(request: Request):
    session = request.session
    if "username" in session and session["expires"] > datetime.utcnow():
        return session["username"]
    raise HTTPException(status_code=401, detail="Not authenticated")

# Authenticate user based on username and password
def authenticate_user(username: str, password: str):
    user = users_db.get(username)
    if user and pwd_context.verify(password, user["hashed_password"]):
        return user
    return None
