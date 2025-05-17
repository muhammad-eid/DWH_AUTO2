-- Dashboard tables DDL

-- Table metrics for trend analysis
CREATE TABLE IF NOT EXISTS table_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    load_data_flag CHAR(1) CHECK (load_data_flag IN ('Y', 'N', '-')),
    availability TEXT CHECK (availability IN ('sys-date', 'sys-date-1', 'sys-date-2')),
    trend DECIMAL(10,2),
    today_rows_count INTEGER,
    last_same_day_rows_count INTEGER,
    variance_flag CHAR(1) CHECK (variance_flag IN ('Y', 'N', '-')),
    date_of_run DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Missing runs tracking
CREATE TABLE IF NOT EXISTS missing_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_name TEXT NOT NULL,
    production TEXT NOT NULL,
    expected_run_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Golden Gates status
CREATE TABLE IF NOT EXISTS golden_gates_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_name TEXT NOT NULL,
    status TEXT CHECK (status IN ('OK', 'ERROR', 'WARNING')),
    delay_seconds INTEGER,
    last_check TIMESTAMP,
    rpa_changes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Online jobs status
CREATE TABLE IF NOT EXISTS online_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_name TEXT NOT NULL,
    status TEXT CHECK (status IN ('Running', 'Finished', 'Error')),
    start_time TIMESTAMP,
    run_duration INTEGER, -- in minutes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dumps jobs status
CREATE TABLE IF NOT EXISTS dumps_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_name TEXT NOT NULL,
    status TEXT CHECK (status IN ('Normal', 'Error', 'Warning')),
    last_run TIMESTAMP,
    normal_end_time TIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Extraction jobs status
CREATE TABLE IF NOT EXISTS extraction_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_name TEXT NOT NULL,
    status TEXT CHECK (status IN ('Normal', 'Error', 'Warning')),
    last_run TIMESTAMP,
    normal_end_time TIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Daily jobs status
CREATE TABLE IF NOT EXISTS daily_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_name TEXT NOT NULL,
    status TEXT CHECK (status IN ('Normal', 'Error', 'Warning')),
    last_run TIMESTAMP,
    normal_end_time TIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
