#UPDATE account
#SET balance = 200
#WHERE id = 3;


#unique idempotency keys. No duplicates
#ALTER TABLE transfers
#ADD CONSTRAINT transfers_idempotency_key_unique
#UNIQUE (idempotency_key); 


