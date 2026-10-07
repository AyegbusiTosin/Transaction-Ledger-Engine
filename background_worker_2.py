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


async def claim_job(conn, worker_id):
    query = """
        WITH job_to_claim AS (
            SELECT id
            FROM jobs
            WHERE status = 'CREATED'
            ORDER BY id
            FOR UPDATE SKIP LOCKED
            LIMIT 1
        )
        UPDATE jobs
        SET
            status = 'PROCESSING',
            worker_id = $1,
            attempt_count = attempt_count + 1,
            lease_expires_at = NOW() + INTERVAL '30 seconds',
            ownership_version = ownership_version + 1
        FROM job_to_claim
        WHERE jobs.id = job_to_claim.id
        RETURNING
            jobs.id,
            jobs.status,
            jobs.worker_id,
            jobs.attempt_count;
    """

    return await conn.fetchrow(query, worker_id)


async def main():
    worker_id = "worker-B"

    conn = await asyncpg.connect(DATABASE_URL)

    while True:
        job = await claim_job(conn, worker_id)

        if not job:
            print(f"{worker_id}: no jobs available")
            await asyncio.sleep(2)
            continue

        print(
            f"{worker_id}: claimed job {job['id']} "
            f"(attempt {job['attempt_count']})"
        )

        # Temporary fake work.
        # Later this will become the actual operation.
        await asyncio.sleep(5)

        print(f"{worker_id}: finished job {job['id']}")

        await conn.execute(
            """
            UPDATE jobs
            SET status = 'SUCCESS'
            WHERE id = $1
            """,
            job["id"]
        )


if __name__ == "__main__":
    asyncio.run(main())