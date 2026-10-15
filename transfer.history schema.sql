CREATE TABLE transfers(  
    id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    amount NUMERIC (10,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE transfer IS '';
COMMENT ON COLUMN transfer.name IS '';



ALTER TABLE transfers
ADD COLUMN worker_id VARCHAR(100),
ADD COLUMN lease_expires_at TIMESTAMPTZ,
ADD COLUMN ownership_version INTEGER NOT NULL DEFAULT 0,
ADD COLUMN attempt_count INTEGER NOT NULL DEFAULT 0;




SELECT
    id,
    status,
    worker_id,
    lease_expires_at,
    NOW() AS current_time,
    lease_expires_at < NOW() AS lease_expired,
    attempt_count,
    ownership_version
FROM transfers
ORDER BY id;


SELECT
    id,
    status,
    worker_id,
    lease_expires_at,
    CASE
        WHEN status = 'CREATED'
            THEN 'ELIGIBLE: new transfer'
        WHEN status = 'PROCESSING'
             AND lease_expires_at < NOW()
            THEN 'ELIGIBLE: expired lease'
        ELSE 'NOT ELIGIBLE'
    END AS eligibility
FROM transfers
ORDER BY id;
