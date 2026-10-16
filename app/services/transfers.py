#handles accepting a transfer and reserving its funds
#the background worker will execute accepted transfers later

from exceptions import(
      SenderNotFoundError,
    ReceiverNotFoundError,
    InsufficientFundsError,
    IdempotencyConflictError
)



async def process_transfer(transfers, conn,current_user ):

            #DATABASE TRANSACTION
            # Everything that changes financial state happens inside
            # one transaction. If anything fails, PostgreSQL rolls the entire operation back.
            async with conn.transaction():
    
                #'FOR UPDATE' row locking to prevent concurrency(race condition)
                # (row locked , no other allowed operation at the time )
                #Pessimistic row lock
                sender_query = """
                SELECT id, user_id, balance, reserved_balance
                FROM account
                WHERE user_id = $1
                FOR UPDATE;   
                """
                sender = await conn.fetchrow(
                                sender_query,
                                 current_user)
    
                if not sender:
                    raise SenderNotFoundError()

                #return{
                 #   "authenticated_user": current_user,
                  #  "sender_account":sender["id"],
                   #  "balance": sender["balance"] }
    
                #if sender["balance"] < transfers.amount:
                 #   raise InsufficientFundsError()

                 # IDEMPOTENCY CHECK
                    # ---------------------------------------------------------
                    # Check whether this logical transfer has already been
                    # processed. A retry with the same key should not create another transfer.
                existing_transfer_query = """
                            SELECT id, sender_id, receiver_id, amount, status
                            FROM transfers
                            WHERE idempotency_key = $1
                            """
                    
                existing_transfer = await conn.fetchrow(
                                existing_transfer_query,
                                transfers.idempotency_key
                            )
                    
                            
                if existing_transfer:
                    if (
                        existing_transfer["sender_id"] == sender["id"]
                        and existing_transfer["receiver_id"] == transfers.receiver_id
                        and existing_transfer["amount"] == transfers.amount
                        ):
                    
                        return {"id": existing_transfer["id"],
                                "status": existing_transfer["status"],
                                "amount": existing_transfer["amount"] }
                    
                    else:
                            # Same key but different transfer details means the
                            # client is attempting to reuse an operation key.
                            raise IdempotencyConflictError()
                                
                #A transfer cannot be sent to an account that doesn't exist 
                receiver_query = """
                SELECT id, user_id, balance
                FROM account
                WHERE id = $1;
                """ 
                receiver = await conn.fetchrow(receiver_query,
                                           transfers.receiver_id)
    
                if not receiver:
                    raise ReceiverNotFoundError()


                #only unreserved funds are avaliable for a new transfer
                available_funds = sender["balance"] - sender["reserved_balance"]

                if transfers.amount <= 0:
                      raise ValueError("Transfer amount must be positive")

                if available_funds < transfers.amount:
                      raise InsufficientFundsError()

                #Reserve funds and create the durable operation record
                #In the same transaction, if either steps fails, both roll back
                #Optimistic /Lock free 
                reserve_query = """
                UPDATE account
                SET reserved_balance = reserved_balance + $1
                WHERE id = $2
                RETURNING id, reserved_balance
                """

                await conn.fetchrow(
                      reserve_query,
                      transfers.amount,
                      sender["id"],
                )

                transferLog_query = """
                    INSERT INTO transfers (sender_id, receiver_id, amount, status, idempotency_key)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING id, sender_id, receiver_id, amount, status, created_at, idempotency_key;
                    """
                transfer_log = await conn.fetchrow(transferLog_query,
                                               sender["id"],
                                                transfers.receiver_id,
                                                 transfers.amount,
                                                  "CREATED",
                                                transfers.idempotency_key)
    
            return {
                "message": "Transfer logged. To be processed",
                "transfer_log" :  transfer_log["id"],
                "status": transfer_log["status"],
                "amount": f"${transfers.amount:.2f}",
                "sender":{
                    "account_id": sender["id"],
                    "user_id": sender["user_id"],
                    "avaliable_funds": (
                    f"${available_funds - transfers.amount: 2f}"
                    ),
                },
                } 

#after successfully gettiNG a 200 OK SUCCESS from the external bank simulator
async def finalize_transfer(
            conn, 
            transfer_id: int,
            worker_id:str,
            ownership_version: int,
            ):

      async with conn.transaction():
            #Locks down the transfer 
            #and verify the  background worker still owns the task

            transfer = await conn.fetchrow(
                  """
                SELECT id, sender_id, receiver_id, amount, status
                FROM transfers
                WHERE id = $1
                    AND status = 'PROCESSING'
                    AND worker_id = $2
                    AND ownership_version = $3
                    AND lease_expires_at > NOW()
                    FOR UPDATE;
                """, transfer_id, worker_id, ownership_version
            )

            if transfer is None:
                  return False
             
            #lock both accounts in a consistent order to prevent deadlocks
            accounts = await conn.fetch(
                  """
                    SELECT id
                    FROM account 
                    WHERE id = ANY($1::int[])
                    ORDER BY id
                    FOR UPDATE;
                  """,
                  [transfer["sender_id"], transfer["receiver_id"]],      
            )
            if len(accounts) != 2:
                  raise RuntimeError("Transfer account not found")
            
            amount = transfer["amount"]

            #money is deducted from the sender from both balance and reserved_balance
            sender = await conn.fetchrow(
                  """
                UPDATE account
                SET balance = balance - $1,
                    reserved_balance = reserved_balance - $1
                WHERE id = $2
                    AND reserved_balance >= $1
                    AND balance >= $1
                RETURNING id;
            """, amount, transfer["sender_id"],
            )

            if sender is None:
                  raise RuntimeError("Sender balance or resevation is invalid")

            #money is credited to the receiver 
            await conn.execute(
                  """
                UPDATE account
                SET balance = balance + $1
                WHERE id = $2;
            """, amount, transfer["receiver_id"],
            )

            #change state to SUCCESS
            await conn.execute(
                  """
                UPDATE transfers
                SET status = 'SUCCESS',
                    worker_id = NULL,
                    lease_expires_at = NULL
                WHERE id = $1;
            """, transfer_id
            )
            return True