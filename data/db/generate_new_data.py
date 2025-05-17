import sqlite3
import random
from datetime import datetime, timedelta
import os

def generate_random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_seconds = random.randrange(86400)  # Seconds in a day
    return start_date + timedelta(days=random_number_of_days, seconds=random_seconds)

def generate_sample_data(num_records=10000):
    # Connect to database
    db_path = os.path.join(os.path.dirname(__file__), 'JobStatus.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Clear existing data
    cursor.execute('DELETE FROM job_status')
    conn.commit()

    # Constants
    init_statuses = ["Aborted", "Soped", "Exceeding"]
    statuses = ["Checking", "Finished", "Ignore", "Other"]
    productions_66 = ["prod1_66", "prod2_66", "quality_66"]
    productions_95 = ["prod2_95", "prod3_95", "cvm_95"]
    productions = productions_66 + productions_95
    owners = ["owner1", "owner2", "owner3", "owner4", "owner5"]
    
    # Current time for the cutoff
    current_time = datetime.now()
    start_date = current_time - timedelta(days=90)  # Data from last 90 days

    # Common error messages
    error_messages = [
        "ORA-00001: Connection timeout",
        "ORA-01653: Data validation failed",
        "ORA-04088: Memory allocation error",
        "ORA-12541: Database connection lost",
        "DSE-1173: File not found",
        None  # For no error cases
    ]

    # Generate records
    records = []
    for i in range(num_records):
        # Generate dates ensuring date <= mod_date <= current_time
        date = generate_random_date(start_date, current_time)
        mod_date = generate_random_date(date, current_time)
        
        # Basic job info
        job_name = f"JOB_{random.randint(1, 500):03d}"
        seq_name = f"SEQ_{random.randint(1, 50):02d}"
        production = random.choice(productions)
        init_status = random.choice(init_statuses)
        status = random.choice(statuses)
        owner = random.choice(owners)
        
        # Error and SQL ID logic
        error = None
        sql_id = None
        oci_name = None
        
        if init_status == "Exceeding":
            sql_id = f"SQL_{random.randint(1000, 9999)}"
            oci_name = f"OCI_{random.randint(100, 999)}"
        else:
            if random.random() > 0.3:  # 70% chance of having an error for non-Exceeding statuses
                error = random.choice(error_messages)

        # Generate random advice and note (30% chance each)
        advice = f"Advice for {job_name}" if random.random() > 0.7 else None
        note = f"Note for {job_name}" if random.random() > 0.7 else None

        record = (
            production, job_name, seq_name, status, init_status,
            error, oci_name, date.strftime('%Y-%m-%d %H:%M:%S'),
            owner, advice, note, mod_date.strftime('%Y-%m-%d %H:%M:%S'),
            sql_id
        )
        records.append(record)

    # Insert records in batches
    insert_query = '''
    INSERT INTO job_status (
        production, job_name, seq_name, status, init_status,
        error, oci_name, date, owner, advice, note, mod_date,
        sql_id
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    
    # Insert in batches of 1000
    batch_size = 1000
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        cursor.executemany(insert_query, batch)
        conn.commit()

    cursor.execute("SELECT COUNT(*) FROM job_status")
    count = cursor.fetchone()[0]
    conn.close()
    print(f"Generated {count} sample records successfully!")

if __name__ == "__main__":
    generate_sample_data(10000)
