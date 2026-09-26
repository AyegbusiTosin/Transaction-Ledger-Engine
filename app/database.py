#Create connection to PostgreSQL 

import asyncpg
from fastapi import Request
from dotenv import load_dotenv
import os

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")


DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@127.0.0.1:5432/{POSTGRES_DB}"

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



