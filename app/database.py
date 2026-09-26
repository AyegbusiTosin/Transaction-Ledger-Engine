#Create connection to PostgreSQL 

import asyncpg
from fastapi import Request

DATABASE_URL = "postgresql://transaction_database:ayodeji0@127.0.0.1:5432/transaction_db"

#establishes collection of reusuable connections 
async def create_pool():
    return await asyncpg.create_pool(
        DATABASE_URL, min_size = 5,
        max_size=20
    )

#endpoints request and get database connection 
async def get_db(request :Request):
    async with request.app.state.pool.acquire() as conn:
        yield conn



