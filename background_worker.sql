CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    status VARCHAR(50) NOT NULL DEFAULT 'CREATED',
    worker_id VARCHAR(100),
    lease_expires_at TIMESTAMPTZ,
    attempt_count INTEGER NOT NULL DEFAULT 0
);


INSERT INTO jobs (status)
SELECT 'CREATED'
FROM generate_series(1, 5);



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
    worker_id = 'worker-A',
    attempt_count = attempt_count + 1
FROM job_to_claim
WHERE jobs.id = job_to_claim.id
RETURNING
    jobs.id,
    jobs.status,
    jobs.worker_id,
    jobs.attempt_count;