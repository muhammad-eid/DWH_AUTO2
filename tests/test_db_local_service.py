
# Test File: test_sqlite_manager.py
"""
Unit Tests for SQLite Manager

Test Cases:
- Test basic CRUD operations
- Test concurrent read/write operations
- Test DDL schema updates
- Test CSV export functionality
- Test maintenance tasks
- Test graceful shutdown
- Load testing with concurrent users
"""

import pytest
import os
import time
import sqlite3
from sqlite_manager import SQLiteManager
import threading
import statistics

TEST_DB_DIR = "test_dbs"
TEST_DB_NAME = "testdb"

@pytest.fixture(scope="module")
def db_manager():
    """Fixture providing clean database manager for tests"""
    manager = SQLiteManager(db_name=TEST_DB_NAME, db_dir=TEST_DB_DIR)
    yield manager
    manager.shutdown()
    if os.path.exists(TEST_DB_DIR):
        for f in os.listdir(TEST_DB_DIR):
            os.remove(os.path.join(TEST_DB_DIR, f))
        os.rmdir(TEST_DB_DIR)

def test_concurrent_writes(db_manager):
    """Test concurrent write operations"""
    results = []
    errors = []
    
    def write_callback(success, error, context):
        if success:
            results.append(1)
        else:
            errors.append(str(error))

    # Create test table
    db_manager.execute_query("CREATE TABLE concurrent_test (id INTEGER PRIMARY KEY, data TEXT)")

    # Start 50 concurrent writers
    threads = []
    for i in range(50):
        t = threading.Thread(
            target=db_manager.execute_query,
            args=("INSERT INTO concurrent_test (data) VALUES (?)", (f"test{i}",)),
            kwargs={"callback": write_callback}
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    assert len(results) == 50
    assert len(errors) == 0

    # Verify writes
    records = db_manager.execute_query("SELECT COUNT(*) FROM concurrent_test")
    assert records[0]['COUNT(*)'] == 50

def test_load_performance(db_manager):
    """Test read/write performance under load"""
    # Warm-up
    db_manager.execute_query("CREATE TABLE perf_test (id INTEGER PRIMARY KEY, data TEXT)")

    # Write performance
    start = time.time()
    for i in range(1000):
        db_manager.execute_query(
            "INSERT INTO perf_test (data) VALUES (?)",
            (f"data{i}",)
        )
    write_time = time.time() - start
    print(f"\nWrite throughput: {1000/write_time:.2f} ops/sec")

    # Read performance
    start = time.time()
    for _ in range(1000):
        db_manager.execute_query("SELECT * FROM perf_test LIMIT 100")
    read_time = time.time() - start
    print(f"Read throughput: {1000/read_time:.2f} ops/sec")

    assert write_time < 2.0, "Write performance degraded"
    assert read_time < 1.5, "Read performance degraded"

def test_ddl_concurrency(db_manager):
    """Test DDL updates during concurrent operations"""
    ddl_path = os.path.join(TEST_DB_DIR, "testdb_ddl.sql")
    
    # Initial DDL
    with open(ddl_path, 'w') as f:
        f.write("CREATE TABLE ddl_test (id INTEGER PRIMARY KEY);")

    results = []
    
    def worker():
        try:
            for _ in range(100):
                db_manager.execute_query("INSERT INTO ddl_test DEFAULT VALUES")
                db_manager.execute_query("SELECT * FROM ddl_test")
            results.append(1)
        except Exception as e:
            results.append(str(e))

    # Start workers
    threads = []
    for _ in range(10):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()

    # Update DDL during operations
    time.sleep(0.1)
    with open(ddl_path, 'a') as f:
        f.write("\nALTER TABLE ddl_test ADD COLUMN new_col TEXT;")

    for t in threads:
        t.join()

    assert len(results) == 10
    assert all(isinstance(r, int) for r in results)

def test_graceful_shutdown():
    """Test proper shutdown with pending operations"""
    manager = SQLiteManager(db_name="shutdown_test", db_dir=TEST_DB_DIR)
    
    # Add pending operation
    manager.execute_query("CREATE TABLE shutdown_test (id INTEGER PRIMARY KEY)")
    
    # Initiate shutdown
    manager.shutdown()
    
    # Try operation after shutdown
    with pytest.raises(sqlite3.ProgrammingError):
        manager.execute_query("SELECT * FROM shutdown_test")