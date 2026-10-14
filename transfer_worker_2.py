#automated background workers

import asyncio
import asyncpg
import os
from dotenv import load_dotenv


load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")


DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@127.0.0.1:5432/{POSTGRES_DB}"



async def claim_transfer(conn, worker_id):
    """Atomicallly claim one transfer that is ready for processing"""

    query = """
    WITH transfer_to_claim AS (
    SELECT id
    FROM transfers
    WHERE 
        status = 'CREATED'
        OR (
            status = 'PROCESSING'
        AND lease_expires_at < NOW()
    )
    ORDER BY id
    FOR UPDATE SKIP LOCKED
    LIMIT 1
    )
    UPDATE transfers
    SET
        status = 'PROCESSING',
        worker_id = $1,
        lease_expires_at = NOW() + INTERVAL  '15 seconds',
        ownership_version = ownership_version + 1,
        attempt_count = attempt_count + 1
    FROM transfer_to_claim
    WHERE transfers.id = transfer_to_claim.id
    RETURNING
        transfers.id,
        transfers.sender_id,
        transfers.receiver_id,
        transfers.amount,
        transfers.status,
        transfers.idempotency_key,
        transfers.worker_id,
        transfers.lease_expires_at,
        transfers.ownership_version,
        transfers.attempt_count;
    """

    async with conn.transaction():
        return await conn.fetchrow(query, worker_id)


async def main():
    worker_id = "worker-B"

    conn = await asyncpg.connect(DATABASE_URL)

    try:
        transfer = await claim_transfer(conn, worker_id)


       # if transfer is not None:
        #  print(
         #       f"Claimed transfer ID: {transfer['id']} | "
          #      f"Status: {transfer['status']} | "
           #     f"Lease expires: {transfer['lease_expires_at']}"
            # )


        if transfer is None:
            print(f"{worker_id}: no CREATED transfers avaliable")
            return

        print(
            f"{worker_id}: claimed transfer {transfer['id']} "
            f"(attempt {transfer['attempt_count']}, "
            f"ownership version {transfer['ownership_version']})"
        )
    finally:
        await conn.close()

if __name__ =="__main__":
    asyncio.run(main())