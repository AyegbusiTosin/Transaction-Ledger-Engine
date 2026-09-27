from utils.password import hash_password
from exceptions import EmailAlreadyRegisteredError
import asyncpg


async def create_account(users, conn):
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
    except asyncpg.UniqueViolationError:
           raise EmailAlreadyRegisteredError() 
          