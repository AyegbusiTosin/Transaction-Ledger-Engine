#handles network logic for login endpoint

from schemas import LoginRequest
from fastapi import APIRouter, Depends, HTTPException
from database import get_db 
from services.login import process_login
from exceptions import InvalidCredentialsError
from utils.auth import security, get_current_user

router = APIRouter()

@router.post("/login")
async def login(login_data: LoginRequest,
                conn = Depends(get_db)):

    try:
            result = await process_login(login_data, conn)
            return result 
    
    except InvalidCredentialsError:
            raise HTTPException(status_code=401,
                                detail="Invalid email or password")


#from fastapi import Depends
#rom fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
#from utils.auth import security


#@router.get("/test-auth")
#async def test_auth(
 #   current_user = Depends(get_current_user)
#):
 #   return {
  #      "message": "Token accepted"
   # }