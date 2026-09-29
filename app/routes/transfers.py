#Networking aspect of the transfer operation endpoint
#handles HTTP request for transfer operations
#parse/validate request
#obtain database connection
#call operation

from schemas import TransferRequest
from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from services.transfers import process_transfer
from utils.auth import get_current_user
from exceptions import(
      SenderNotFoundError,
    ReceiverNotFoundError,
    InsufficientFundsError,
    IdempotencyConflictError
)



router = APIRouter()

@router.post("/transfer")
async def make_transfer(transfers: TransferRequest,
                                #dependency injection
                                #meeaning- this function needs these things to run 
                         conn=Depends (get_db),
                         current_user=Depends(get_current_user)):

    try:

        result = await process_transfer(transfers, conn, current_user)
        return result 

    except SenderNotFoundError:
        raise HTTPException(status_code=404,
                            detail="Sender account not found")

    except ReceiverNotFoundError:
        raise HTTPException(status_code=404,
                            detail="Receiver account not found")

    except InsufficientFundsError:
            raise HTTPException(status_code=400,
                                detail="Insufficient funds")

    except IdempotencyConflictError:
            raise HTTPException(status_code=409,
                                detail="Operation already performed")
    
    
    