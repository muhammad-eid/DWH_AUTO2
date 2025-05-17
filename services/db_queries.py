# 1. Get the last record for a job name by the last modification date
GET_LAST_RECORD_FOR_JOB = """
SELECT * 
FROM job_status 
WHERE job_name = ? 
ORDER BY mod_date DESC 
LIMIT 1
"""

# 2. Get all records
GET_ALL_RECORDS = """
SELECT * 
FROM job_status
"""

# 3. Get all records for a specific job in the last month
GET_RECORDS_FOR_JOB_LAST_MONTH = """
SELECT * 
FROM job_status 
WHERE job_name = ? 
AND mod_date >= DATE('now', '-1 month')
"""

# 4. Insert a new record
INSERT_NEW_RECORD = """
INSERT INTO job_status (
    production, job_name, seq_name, status, error, oci_name, date, advice, note, sql_id, mod_date
) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

# 5. Update a record with job name and last modification date
UPDATE_RECORD_WITH_JOB_NAME_AND_MOD_DATE = """
UPDATE job_status 
SET production = ?, seq_name = ?, status = ?, error = ?, oci_name = ?, date = ?, advice = ?, note = ?, sql_id = ?, mod_date = ? 
WHERE job_name = ? 
AND mod_date = ?
"""
