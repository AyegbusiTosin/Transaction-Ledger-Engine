#handles the issuing of JWT Tokens
import jwt
from dotenv import load_dotenv
import os
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials 
from fastapi import Depends

security = HTTPBearer()

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_access_token(user_id: int):
    payload = {
        "sub": str(user_id)
    }

    token = jwt.encode(
        payload, SECRET_KEY,
        algorithm=ALGORITHM
    )
    return token

async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security)):
    print(credentials)