#External Bank Simulator

import asyncio

from fastapi import FastAPI
from pydantic import BaseModel
from decimal import Decimal
from contextlib import asynccontextmanager


processed_transfers = {}

class BankTransferRequest(BaseModel):
    from_account: str
    to_account: str
    amount: Decimal
    idempotency_key: str 


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Fast API connected!")
    yield
    print("FastAPI disconnected!")

app = FastAPI(lifespan=lifespan)


@app.post("/bank/transfer")
async def make_transfer(transfer: BankTransferRequest):

    #checks if the operation has been processed
    if transfer.idempotency_key in processed_transfers:
        print("BANK: duplicate request detected")
        print("BANK: returning previous result")

        return processed_transfers[transfer.idempotency_key]

    #first time processing the operation
    result = {
        "sender": transfer.from_account,
        "receiver": transfer.to_account,
        "amount": transfer.amount,
        "status": "SUCCESS",
        "message": "transfer processed"
    }

    #record the completed operation
    processed_transfers[transfer.idempotency_key] = result

    print("BANK: transfer processed")
    print(processed_transfers)   

    #simulate response getting lost/delayed
    await asyncio.sleep(5)

    return result 