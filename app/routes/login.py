#handles network logiv for login endpoint

from schemas import LoginRequest
from fastapi import APIRouter, Depends, HTTPException
from database import get_db 
from services.login import process_login
from exceptions import InvalidCredentialsError


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


from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.auth import security


@router.get("/test-auth")
async def test_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    return {
        "scheme": credentials.scheme,
        "credentials": credentials.credentials
    }