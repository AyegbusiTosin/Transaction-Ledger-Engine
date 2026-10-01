#External Bank Simulator

from fastapi import FastAPI
from pydantic import BaseModel
from decimal import Decimal
from contextlib import asynccontextmanager


class BankTransferRequest(BaseModel):
    from_account: str
    to_account: str
    amount: Decimal 


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Fast API connected!")
    yield
    print("FastAPI disconnected!")

app = FastAPI(lifespan=lifespan)


@app.post("/bank/transfer")
async def make_transfer(transfer: BankTransferRequest):

    #result = transfer.from_account, 

    return {"sender": transfer.from_account,
            "receiver": transfer.to_account,
            "amount": transfer.amount, 
            "status": "SUCCESS",
            "message": "Transfer Processed",
            "message2": "it worked!!!"}