import sqlite3
import random
from datetime import datetime, timedelta
import string
import os

def generate_job_name():
    job_types = ['LOAD', 'TRF', 'RPT']
    domains = ['CUSTOMER', 'SALES', 'PRODUCT', 'FINANCE', 'INVENTORY', 'BILLING', 'ORDER', 'ACCOUNT']
    frequencies = ['DAILY', 'WEEKLY', 'MONTHLY', 'HOURLY']
    return f"DS_{random.choice(job_types)}_{random.choice(domains)}_{random.choice(frequencies)}_{random.randint(1, 100)}"

def generate_error_message(status):
    if status not in ['Aborted', 'stoped']:
        return ''
    
    errors = [
        'ORA-00001: Connection timeout while accessing source database',
        'ORA-04088: Insufficient memory for transformation operation',
        'ORA-01653: Source table structure changed during execution',
        'DSE-1173: Invalid data format in source records',
        'DSE-1435: Job terminated by user during execution',
        'ORA-01555: Snapshot too old: rollback segment with ID 0x not available',
        'DSE-1180: Lookup table memory allocation failed',
        'ORA-12541: Network transport: Cannot connect to destination host'
    ]
    return random.choice(errors)

def generate_advice(status):
    if status not in ['Aborted', 'stoped', 'Exceeding']:
        return ''
    
    advice_list = [
        'Check source system connectivity and retry after confirming availability',
        'Verify source data integrity and rerun after validation',
        'Monitor system resources and schedule during off-peak hours',
        'Review job parameters and adjust memory allocation',
        'Contact database team for space allocation issues',
        'Investigate network connectivity issues with source system'
    ]
    return random.choice(advice_list)

def generate_note():
    if random.random() > 0.2:  # 80% chance of no note
        return ''
    
    notes = [
        'Regular maintenance window: Job scheduled to run after completion',
        'Performance optimization required: Adding to next sprint',
        'Source system upgrade pending: Monitor closely',
        'New columns added: Validation in progress',
        'Scheduled for retirement: Migration planning in progress'
    ]
    return random.choice(notes)

def generate_sample_data(num_records=1000):
    db_path = os.path.join(os.path.dirname(__file__), 'JobStatus.db')
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("DELETE FROM job_status")
    
    # Generate records
    base_date = datetime.now() - timedelta(days=30)
    
    for _ in range(num_records):
        # Generate random date within last 30 days
        random_days = random.randint(0, 30)
        random_hours = random.randint(0, 23)
        random_minutes = random.randint(0, 59)
        date = base_date + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
        
        # Status with weighted distribution
        status_choices = [
            ('Finished', 60),
            ('Checking', 15),
            ('Exceeding', 10),
            ('Aborted', 7),
            ('stoped', 5),
            ('Other', 3)
        ]
        status = random.choices([s[0] for s in status_choices], weights=[s[1] for s in status_choices])[0]
        
        # Production environment with weighted distribution
        prod_env = random.choices(
            ['PROD', 'DEV', 'TEST', 'UAT'],
            weights=[70, 10, 10, 10]
        )[0]
        
        # Generate record
        record = {
            'production': prod_env,
            'job_name': generate_job_name(),
            'seq_name': f"SEQ_{random.randint(1,5)}_{random.choice(['MAIN', 'DELTA', 'FULL'])}",
            'status': status,
            'init_status': 'Checking',  # All jobs start as Checking
            'error': generate_error_message(status),
            'oci_name': f"OCI_{random.choice(['SALES', 'CUSTOMER', 'PRODUCT', 'BILLING', 'INVENTORY'])}_{random.randint(1,10)}" if status == 'Exceeding' else '',
            'date': date.strftime('%Y-%m-%d %H:%M:%S'),
            'owner': random.choices(
                ['system.automated', 'john.smith', 'mary.jones', 'david.wilson', 'sarah.davis', 'mike.brown'],
                weights=[95, 1, 1, 1, 1, 1]
            )[0],
            'advice': generate_advice(status),
            'note': generate_note(),
            'mod_date': (date + timedelta(minutes=random.randint(1, 30))).strftime('%Y-%m-%d %H:%M:%S'),
            'sql_id': f"SQL_{os.urandom(4).hex()}" if status in ['Exceeding', 'Aborted'] else ''
        }
        
        # Insert record
        cursor.execute("""
            INSERT INTO job_status (
                production, job_name, seq_name, status, init_status,
                error, oci_name, date, owner, advice, note, mod_date, sql_id
            ) VALUES (
                :production, :job_name, :seq_name, :status, :init_status,
                :error, :oci_name, :date, :owner, :advice, :note, :mod_date, :sql_id
            )
        """, record)
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"Successfully generated {num_records} sample records!")

if __name__ == "__main__":
    generate_sample_data()
