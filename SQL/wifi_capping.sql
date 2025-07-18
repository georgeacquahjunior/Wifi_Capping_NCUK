-- Table 1: students
-- Stores student login credentials and profile information
CREATE TABLE students (
    id SERIAL PRIMARY KEY,                            -- Auto-incremented student ID
    student_id VARCHAR(50) UNIQUE NOT NULL,           -- Unique identifier (e.g., index number)
    first_name VARCHAR(100) NOT NULL,                 -- Student's first name
    last_name VARCHAR(100) NOT NULL,                  -- Student's last name
    password_hash VARCHAR(255) NOT NULL,              -- Hashed login password for security
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP    -- Timestamp of account creation
);

-- Table 2: data_usage_logs
-- Logs each instance of student data usage or allocation
CREATE TABLE data_usage_logs (
    id SERIAL PRIMARY KEY,                                        -- Auto-incremented log ID
    student_id INT REFERENCES students(id) ON DELETE CASCADE,     -- FK linking to students
    allocated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,             -- Timestamp of data allocation
    amount_allocated FLOAT,                                       -- Optional: data allocated in this session (in MB or GB)
    amount_used_mb FLOAT NOT NULL,                                -- Actual amount of data used in MB
    amount_remaining FLOAT                                        -- Optional: estimated data remaining
);

-- Table 3: monthly_usage
-- Tracks monthly data usage and capping status per student
CREATE TABLE monthly_usage (
    id SERIAL PRIMARY KEY,                                        -- Auto-incremented record ID
    student_id INT REFERENCES students(id) ON DELETE CASCADE,     -- FK linking to students
    month DATE NOT NULL,                                          -- Usage month (e.g. '2025-07-01')
    total_mb FLOAT NOT NULL,                                      -- Total monthly data used in MB
    capped BOOLEAN DEFAULT FALSE,                                 -- Indicates whether 20GB cap is reached
    UNIQUE(student_id, month)                                     -- Prevent duplicate records per month
);

-- Table 4: admins
-- Stores system administrator credentials

CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    admin_id VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    password_hash TEXT NOT NULL
);
