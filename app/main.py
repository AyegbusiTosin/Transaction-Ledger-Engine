#FastAPI webserver  lifecycle

from fastapi import FastAPI, HTTPException, status
from contextlib import asynccontextmanager 
from database import create_pool
from schemas import AccountCreate, TransferRequest
import asyncio
from routes.accounts import router as accounts_router
from routes.transfers import router as transfers_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    #created connection pools attached to application state
    app.state.pool = await create_pool()
    print("Database connected")

    yield
    await app.state.pool.close()
    print("Database closed")

app = FastAPI(lifespan=lifespan)

app.include_router(accounts_router)
app.include_router(transfers_router) 



        



















