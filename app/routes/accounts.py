#creates identity in users table
#creeates amount info  in account table

from schemas import AccountCreate
from fastapi import APIRouter, Depends, HTTPException
from database import get_db
import asyncpg
from utils.password import hash_password
from services.account import create_account
from exceptions import EmailAlreadyRegisteredError


router = APIRouter()

@router.post("/createaccount")
async def account_creation(users: AccountCreate,
            conn = Depends(get_db) ): 

        try:
             result = await create_account(users, conn)
             return result

        except EmailAlreadyRegisteredError:
                        raise HTTPException(
                        status_code=409,
                        detail="Email already registered"
                        )