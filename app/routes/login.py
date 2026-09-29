#handles network for login endpoint

from schemas import LoginRequest
from fastapi import APIRouter, Depends, HTTPException
from database import get_db 
from services.login import process_login
from exceptions import InvalidCredentialsError
from utils.auth import security, get_current_user

router = APIRouter()

@router.post("/login")
async def login(login_data: LoginRequest,
                #dependency injections
                #meaning- this function needs these things to run 
                conn = Depends(get_db)):

    try:
            result = await process_login(login_data, conn)
            return result 
    
    except InvalidCredentialsError:
            raise HTTPException(status_code=401,
                                detail="Invalid email or password")


@router.get("/test-auth")
async def test_auth(
    current_user = Depends(get_current_user)
):
    return {
        "authenticated_user": current_user
    }