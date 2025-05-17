CREATE TABLE job_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    production TEXT NOT NULL,
    job_name TEXT NOT NULL,
    seq_name TEXT,
    status TEXT NOT NULL,
    init_status TEXT NOT NULL,
    error TEXT,
    oci_name TEXT,
    date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    owner TEXT,
    advice TEXT,
    note TEXT,
    mod_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sql_id TEXT
);

CREATE INDEX idx_job_name ON job_status(job_name);
CREATE INDEX idx_status ON job_status(status);
-- CREATE INDEX idx_mod_date ON job_status(mod_date);

-- -- Sample insert
-- INSERT INTO job_status (production, job_name, seq_name, status, error, date, advice, owner, note, mod_date, version, sql_id)
-- VALUES ('Prod1', 'Job1', 'Seq1', 'Pending', '', '2023-10-01 12:00:00', '', 'Owner1', '', '2023-10-01 12:00:00', 1, 'SQL123');
