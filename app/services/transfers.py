#handles business logic of Transfer endpoint

from exceptions import(
      SenderNotFoundError,
    ReceiverNotFoundError,
    InsufficientFundsError,
    IdempotencyConflictError
)

async def process_transfer(transfers, conn):
    #check idempotency key if operation has been performed
            existing_transfer_query = """
            SELECT id, sender_id, receiver_id, amount, status
            FROM transfers
            WHERE idempotency_key = $1
            """
    
            existing_transfer = await conn.fetchrow(
                existing_transfer_query,
                transfers.idempotency_key
            )
    
            #
            if existing_transfer:
                if (
                    existing_transfer["sender_id"] == transfers.sender_id
                    and existing_transfer["receiver_id"] == transfers.receiver_id
                    and existing_transfer["amount"] == transfers.amount
                ):
    
                    return {"id": existing_transfer["id"],
                        "status": existing_transfer["status"],
                        "amount": existing_transfer["amount"] }
    
                else:
                    raise IdempotencyConflictError()
                
    
             #Atomicity- implementation of the ACID database principle
             #all execution must succeed or none does. 
            async with conn.transaction():
    
                #'FOR UPDATE' row locking to prevent concurrency(race condition)
                # (row locked , no other allowed operation at the time )
                sender_query = """
                SELECT id, owner, balance
                FROM account
                WHERE id = $1
                FOR UPDATE;   
                """
                sender = await conn.fetchrow(sender_query,
                                 transfers.sender_id)
    
                if not sender:
                    raise SenderNotFoundError()
    
                if sender["balance"] < transfers.amount:
                    raise InsufficientFundsError()
    
                receiver_query = """
                SELECT id, owner, balance
                FROM account
                WHERE id = $1;
                """ 
                receiver = await conn.fetchrow(receiver_query,
                                           transfers.receiver_id)
    
                if not receiver:
                    raise ReceiverNotFoundError()
    
    
                deduct_query = """
                    UPDATE account
                    SET balance = balance - $1
                    WHERE id = $2
                    RETURNING id, owner, balance;
                    """
    
                deduct = await conn.fetchrow(deduct_query, 
                                         transfers.amount, 
                                         transfers.sender_id)
                   
                add_query="""
                    UPDATE account
                    SET balance = balance + $1
                    WHERE id = $2
                    RETURNING id, owner, balance;
                    """
                add = await conn.fetchrow(add_query, 
                                      transfers.amount, 
                                      transfers.receiver_id)
        
            
                transferLog_query = """
                    INSERT INTO transfers (sender_id, receiver_id, amount, status, idempotency_key)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING id, sender_id, receiver_id, amount, status, created_at, idempotency_key;
                    """
                transfer_log = await conn.fetchrow(transferLog_query,
                                               transfers.sender_id,
                                                transfers.receiver_id,
                                                 transfers.amount,
                                                  "SUCCESS",
                                                transfers.idempotency_key)
    
            return {
                "message": "Transfer processed successfully",
                "transfer_log" :  transfer_log["id"],
                "status": transfer_log["status"],
                "amount": f"${transfers.amount:.2f}",
                "sender":{
                    "id": sender["id"],
                    "owner": sender["owner"],
                    "new_balance": f"${deduct['balance']:.2f}"
                }} 
            
    