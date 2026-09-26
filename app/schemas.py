# Validates API JSON structure

from pydantic import BaseModel, Field
from decimal import Decimal

class AccountCreate(BaseModel):
    name: str
    email: str
    password: str

class TransferRequest(BaseModel):
    sender_id: int
    receiver_id: int
    amount: Decimal
    idempotency_key: str    #identifies operation ID