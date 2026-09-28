#handles the issuing and verfication of JWT Tokens

import jwt
from dotenv import load_dotenv
import os
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials 
from fastapi import Depends, HTTPException

security = HTTPBearer()

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

#creates JWT tokens
def create_access_token(user_id: int):
    payload = {
        "sub": str(user_id)
    }

    token = jwt.encode(
        payload, 
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return token

#get current user attached to token
async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security)):

    #Extract JWT from Authorization header
    token = credentials.credentials

    #verify token's signature and decode payload
    #payload contains user_id - HEADER.PAYLOAD.SIGNATURE
    payload =jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )

    #Extract user ID placed in token when user logged in
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401,
                             detail="Invalid token: missing user identifier")

    return user_id