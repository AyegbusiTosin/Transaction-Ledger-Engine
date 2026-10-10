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
                OR (
                    status =    'PROCESSING'
                    AND lease_expires_at < NOW()
                    )
            ORDER BY id
            FOR UPDATE SKIP LOCKED
            LIMIT 1
        )
        UPDATE jobs
        SET
            status = 'PROCESSING',
            worker_id = $1,
            lease_expires_at = NOW() + INTERVAL '15 seconds',
            attempt_count = attempt_count + 1,
            ownership_version = ownership_version + 1
        FROM job_to_claim
        WHERE jobs.id = job_to_claim.id
        RETURNING
            jobs.id,
            jobs.status,
            jobs.worker_id,
            jobs.attempt_count,
            jobs.ownership_version,
            jobs.lease_expires_at;
    """

    return await conn.fetchrow(query, worker_id)


async def main():
    worker_id = "worker-A"

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

        
        #await asyncio.sleep(5)

        #simulates slow worker taking time to process job

        if worker_id == "worker-A":
            await asyncio.sleep(25)

        else:
            await asyncio.sleep(3)


        print(
            f"{worker_id}: processing job {job['id']} "
            f"with ownership version {job['ownership_version']}")

        

        print(f"{worker_id}: finished job {job['id']}")

        result = await conn.execute(
            """
            UPDATE jobs
            SET 
                status = 'SUCCESS',
                lease_expires_at = NULL
            WHERE id = $1
            AND worker_id = $2
            AND ownership_version = $3
            AND lease_expires_at > NOW()
            AND status = 'PROCESSING';
            """,
            job["id"],
            worker_id,
            job["ownership_version"]
        )
        if result == "UPDATE 1":
            print(f"{worker_id}: completed job {job['id']}")

        else:
            print(
                f"{worker_id}: lost ownership of job {job['id']}; "
            )


if __name__ == "__main__":
    asyncio.run(main())