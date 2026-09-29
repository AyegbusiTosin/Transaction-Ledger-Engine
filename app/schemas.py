# Validates API JSON structure

from pydantic import BaseModel, Field
from decimal import Decimal

class AccountCreate(BaseModel):
    name: str
    email: str
    password: str

class TransferRequest(BaseModel):

    #The client chooses the destination account
    receiver_id: int

    #the amount the authenticated user wants to transfer
    amount: Decimal

    #identifies operation ID so retries dont create duplicates
    idempotency_key: str   


class LoginRequest(BaseModel):
    email: str
    password: str