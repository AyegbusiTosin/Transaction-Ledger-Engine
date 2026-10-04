#handles business logic of Transfer endpoint

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
                sender_query = """
                SELECT id, user_id, balance
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
    
                if sender["balance"] < transfers.amount:
                    raise InsufficientFundsError()

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
                    
                            #
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
                                
                    
                receiver_query = """
                SELECT id, user_id, balance
                FROM account
                WHERE id = $1;
                """ 
                receiver = await conn.fetchrow(receiver_query,
                                           transfers.receiver_id)
    
                if not receiver:
                    raise ReceiverNotFoundError()


                from services.bank import make_bank_transfer

                #External Bank service Simulation
                result = await make_bank_transfer(
                       from_account=str(sender["id"]),
                       to_account=str(transfers.receiver_id),
                       amount=transfers.amount,
                       idempotency_key=transfers.idempotency_key
                )


                print(result)

                #DELIBERATE FAILURE
                #raise Exception("Boom!!!")
                 
                deduct_query = """
                    UPDATE account
                    SET balance = balance - $1
                    WHERE id = $2
                    RETURNING id, user_id, balance;
                    """
    
                deduct = await conn.fetchrow(deduct_query, 
                                         transfers.amount,
                                         sender["id"])
                                                            
                                        
                add_query="""
                    UPDATE account
                    SET balance = balance + $1
                    WHERE id = $2
                    RETURNING id, user_id, balance;
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
                                               sender["id"],
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
                    "account_id": sender["id"],
                    "user_id": sender["user_id"],
                    "new_balance": f"${deduct['balance']:.2f}"
                }} 
            
    