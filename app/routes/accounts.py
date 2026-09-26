#creates identity in users table
#creeates amount info  in account table

from schemas import AccountCreate
from fastapi import APIRouter, Depends, HTTPException
from database import get_db
import asyncpg
from utils.password import hash_password

router = APIRouter()

@router.post("/createaccount")
async def create_account(users: AccountCreate,
            conn = Depends(get_db) ): 

        try:
            async with conn.transaction():

                #users table query
                user_query = """
                INSERT INTO users(name, email, password)
                VALUES($1, $2, $3 )
                RETURNING id, name, email;
                """

                hashed_password = hash_password(users.password)

                user = await conn.fetchrow(
                    user_query,
                    users.name, 
                    users.email, 
                    hashed_password 
                    )

                #raise Exception("Boom!!!")

                #account table query
                account_query = """
                INSERT INTO account(user_id, balance)
                VALUES($1, $2)
                RETURNING id, user_id, balance;
                """

                account = await conn.fetchrow(
                    account_query, 
                    user["id"],
                    0.00
                    )

        except asyncpg.UniqueViolationError:
            raise HTTPException(
            status_code=409,
            detail="Email already registered"
            )

        return {
            "user":{
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
                  },

            "account": {
            "id": account["id"],
            "balance": account["balance"]
                                }
                                    }  
      