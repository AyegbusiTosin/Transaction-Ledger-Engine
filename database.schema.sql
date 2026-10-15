CREATE TABLE account (
    id SERIAL PRIMARY KEY,
    owner VARCHAR(100) NOT NULL,
    balance NUMERIC(10, 2) DEFAULT 0.00,  -- Use NUMERIC instead of INT
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



SELECT
    id,
    status,
    worker_id,
    ownership_version,
    lease_expires_at,
    lease_expires_at > NOW() AS lease_is_valid
FROM transfers
WHERE id = 1;