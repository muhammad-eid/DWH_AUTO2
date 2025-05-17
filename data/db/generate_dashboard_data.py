import sqlite3
import random
from datetime import datetime, timedelta
import os
import sys

def create_connection():
    """Create a database connection"""
    try:
        db_path = os.path.join(os.path.dirname(__file__), 'Dashboard.db')
        conn = sqlite3.connect(db_path)
        print(f"Successfully connected to database at {db_path}")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        sys.exit(1)

def execute_sql_file(conn, sql_file):
    """Execute SQL file"""
    try:
        print(f"Executing SQL file: {sql_file}")
        with open(sql_file, 'r') as f:
            sql = f.read()
        conn.executescript(sql)
        conn.commit()
        print("SQL file executed successfully")
    except Exception as e:
        print(f"Error executing SQL file: {str(e)}")
        sys.exit(1)

def generate_table_metrics(conn, num_tables=20, days=30):
    """Generate sample table metrics data"""
    print(f"Generating metrics for {num_tables} tables over {days} days...")
    tables = [f"TABLE_{i}" for i in range(1, num_tables + 1)]
    current_date = datetime.now()
    
    for table in tables:
        base_count = random.randint(10000, 1000000)
        for day in range(days):
            date = current_date - timedelta(days=day)
            variance = random.randint(-1000, 1000)
            today_count = base_count + variance
            last_week_count = today_count - random.randint(-500, 500)
            
            conn.execute("""
                INSERT INTO table_metrics (
                    table_name, load_data_flag, availability, trend,
                    today_rows_count, last_same_day_rows_count,
                    variance_flag, date_of_run
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                table,
                random.choice(['Y', 'N', '-']),
                random.choice(['sys-date', 'sys-date-1', 'sys-date-2']),
                round(random.uniform(0.8, 1.2), 2),
                today_count,
                last_week_count,
                'Y' if abs(variance) > 800 else 'N',
                date.strftime('%Y-%m-%d')
            ))
    print(f"Generated {num_tables * days} table metric records")

def generate_missing_runs(conn):
    """Generate missing runs data"""
    print("Generating missing runs data...")
    jobs = [f"JOB_{i}" for i in range(1, 11)]
    productions = ['PROD1', 'PROD2', 'PROD3']
    
    for job in jobs:
        if random.random() < 0.3:  # 30% chance of missing run
            conn.execute("""
                INSERT INTO missing_runs (job_name, production, expected_run_date)
                VALUES (?, ?, ?)
            """, (
                job,
                random.choice(productions),
                (datetime.now() - timedelta(days=random.randint(1, 5))).strftime('%Y-%m-%d')
            ))
    print("Missing runs data generated")

def generate_golden_gates(conn):
    """Generate Golden Gates status data"""
    print("Generating Golden Gates status data...")
    nodes = [f"NODE_{i}" for i in range(1, 6)]
    
    for node in nodes:
        delay = random.randint(0, 600)
        conn.execute("""
            INSERT INTO golden_gates_status (
                node_name, status, delay_seconds, last_check, rpa_changes
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            node,
            'OK' if delay < 300 else random.choice(['WARNING', 'ERROR']),
            delay,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            random.randint(0, 100)
        ))
    print("Golden Gates status data generated")

def generate_online_jobs(conn):
    """Generate online jobs status data"""
    print("Generating online jobs status data...")
    jobs = [f"ONLINE_JOB_{i}" for i in range(1, 8)]
    
    for job in jobs:
        duration = random.randint(30, 90)
        conn.execute("""
            INSERT INTO online_jobs (
                job_name, status, start_time, run_duration
            ) VALUES (?, ?, ?, ?)
        """, (
            job,
            'Running' if duration > 60 else 'Finished',
            (datetime.now() - timedelta(minutes=duration)).strftime('%Y-%m-%d %H:%M:%S'),
            duration
        ))
    print("Online jobs status data generated")

def generate_job_status(conn, table_name, num_jobs=5):
    """Generate status for dumps/extraction/daily jobs"""
    print(f"Generating {table_name} data...")
    jobs = [f"{table_name}_JOB_{i}" for i in range(1, num_jobs + 1)]
    
    for job in jobs:
        status = random.choice(['Normal', 'Error', 'Warning'])
        last_run = datetime.now() - timedelta(minutes=random.randint(30, 480))
        
        conn.execute(f"""
            INSERT INTO {table_name} (
                job_name, status, last_run, normal_end_time
            ) VALUES (?, ?, ?, ?)
        """, (
            job,
            status,
            last_run.strftime('%Y-%m-%d %H:%M:%S'),
            '23:00:00' if status == 'Normal' else None
        ))
    print(f"{table_name} data generated")

def main():
    """Main function to generate all test data"""
    print("Starting test data generation...")
    
    try:
        # Create and get connection
        conn = create_connection()
        
        # Create tables
        sql_file = os.path.join(os.path.dirname(__file__), 'Dashboard.sql')
        execute_sql_file(conn, sql_file)
        
        # Generate data
        generate_table_metrics(conn)
        generate_missing_runs(conn)
        generate_golden_gates(conn)
        generate_online_jobs(conn)
        
        # Generate job status for different types
        generate_job_status(conn, 'dumps_jobs')
        generate_job_status(conn, 'extraction_jobs')
        generate_job_status(conn, 'daily_jobs')
        
        conn.commit()
        print("All data committed to database")
        
        # Verify data
        cur = conn.cursor()
        for table in ['table_metrics', 'missing_runs', 'golden_gates_status', 
                     'online_jobs', 'dumps_jobs', 'extraction_jobs', 'daily_jobs']:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"{table}: {count} records")
        
        conn.close()
        print("Test data generation completed successfully!")
        
    except Exception as e:
        print(f"Error during data generation: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
