#handles the issuing and verfication of JWT Tokens

import jwt
from dotenv import load_dotenv
import os
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials 
from fastapi import Depends, HTTPException
from datetime import datetime, timedelta, timezone

security = HTTPBearer()

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

#creates JWT tokens
def create_access_token(user_id: int):

    #expiration time for token
    expiration = datetime.now(timezone.utc) + timedelta(minutes=50)

    payload = {
        "sub": str(user_id),
        "exp": expiration
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

    try:
    #verify token's signature and decode payload
    #payload contains user_id - HEADER.PAYLOAD.SIGNATURE
        payload =jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

    #Extract user ID placed in token when user logged in
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token: missing user identifier")

    return int(user_id)