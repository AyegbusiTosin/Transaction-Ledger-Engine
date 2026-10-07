CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    status VARCHAR(50) NOT NULL DEFAULT 'CREATED',
    worker_id VARCHAR(100),
    lease_expires_at TIMESTAMPTZ,
    attempt_count INTEGER NOT NULL DEFAULT 0
);

#create fresh jobs
INSERT INTO jobs (status)
SELECT 'CREATED'
FROM generate_series(1, 5);


#assign job to worker
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


#worker lease time
UPDATE jobs
SET lease_expires_at = NOW() + INTERVAL '30 seconds'
WHERE id = 6
  AND worker_id = 'worker-A'
RETURNING id, status, worker_id, lease_expires_at;


#compare job lease time and expiring lease time
SELECT
    id,
    status,
    worker_id,
    lease_expires_at,
    NOW() AS current_time
FROM jobs
WHERE id = 6;


#find all created and expired_lease jobs
SELECT
    id,
    status,
    worker_id,
    lease_expires_at,
    attempt_count
FROM jobs
WHERE
    status = 'CREATED'
    OR
    (
        status = 'PROCESSING'
        and lease_expires_at < NOW()
    )
ORDER BY id 


#find all expired lease jobs and reassign to another worker
WITH job_to_claim AS (
    SELECT id
    FROM jobs
    WHERE
        status = 'CREATED'
        OR
        (
            status = 'PROCESSING'
            AND lease_expires_at < NOW()
        )
    ORDER by id
    FOR UPDATE SKIP LOCKED
    LIMIT 1
)
UPDATE jobs
SET
    status = 'PROCESSING',
    worker_id = 'worker-B',
    lease_expires_at = NOW() + INTERVAL '30 seconds',
    attempt_count = attempt_count + 1
FROM job_to_claim
WHERE jobs.id = job_to_claim.id
RETURNING
    jobs.id,
    jobs.status,
    jobs.worker_id,
    jobs.lease_expires_at,
    jobs.attempt_count


#worker ownership validation
ALTER TABLE jobs
ADD COLUMN ownership_version INTEGER NOT NULL DEFAULT 0; 


UPDATE jobs
SET
    status = 'PROCESSING',
    worker_id = 'worker-B',
    ownership_version = 1,
    lease_expires_at = NOW() + INTERVAL '30 seconds'
WHERE id = 6;


#find expired lease jobs and reclaim job ownership to other workers
#fencing token 
WITH job_to_claim AS (
    SELECT id
    FROM jobs
    WHERE
        status = 'PROCESSING'
        AND lease_expires_at < NOW()
    ORDER BY id
    FOR UPDATE SKIP LOCKED
    LIMIT 1
)
UPDATE jobs
SET
    status = 'PROCESSING',
    worker_id = 'worker-C',
    lease_expires_at = NOW() + INTERVAL '30 seconds',
    attempt_count = attempt_count + 1,
    ownership_version = ownership_version + 1
FROM job_to_claim
WHERE jobs.id = job_to_claim.id
RETURNING
    jobs.id,
    jobs.status,
    jobs.worker_id,
    jobs.ownership_version,
    jobs.attempt_count,
    jobs.lease_expires_at;


#testing ownership versions
UPDATE jobs
SET status = 'SUCCESS'
WHERE id = 18
  AND ownership_version = 1
RETURNING
    id,
    status,
    worker_id,
    ownership_version,
    attempt_count;


INSERT INTO jobs (status)
SELECT 'CREATED'
FROM generate_series(1, 10);