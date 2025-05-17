import glob
import sqlite3
import os
import time
import re
from contextlib import contextmanager
from typing import Optional, List, Dict, Union
import logging
import pandas as pd  # Added for DataFrame support


class SQLiteManager:
    WRITE_KEYWORDS = {'insert', 'update', 'delete', 'replace', 'create', 
                      'drop', 'alter', 'vacuum', 'commit', 'begin', 'rollback', 'pragma'}
    MAX_RETRIES = 3  # Retry limit for write queries

    def __init__(self, db_name: str = 'test', db_dir: str = 'data/db'):
        self.db_name = db_name
        self.db_dir = os.path.abspath(db_dir)
        self.db_path = os.path.join(self.db_dir, f"{db_name}.db")

        self._init_directories()
        self._setup_logging()
        self._optimize_database()

    def _init_directories(self):
        os.makedirs(self.db_dir, exist_ok=True)

    def _setup_logging(self):
        self.logger = logging.getLogger(f"SQLiteManager-{self.db_name}")
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _optimize_database(self):
        """Apply database optimizations like index creation."""
        with self._get_connection() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=-20000")
            conn.execute("PRAGMA mmap_size=268435456")
            conn.execute("PRAGMA temp_store=MEMORY")
            conn.execute("PRAGMA optimize")

    def execute_query(
        self, 
        query: str, 
        params: tuple = (), 
        as_dataframe: bool = True
    ) -> Union[Optional[List[Dict]], pd.DataFrame, bool]:
        """
        Execute a query and return results or status.

        :param query: SQL query to execute.
        :param params: Parameters for the query.
        :param as_dataframe: If True, return results as a Pandas DataFrame.
        :return: Query results as a list of dictionaries, DataFrame, or execution status.
        """
        if self._is_write_query(query):
            return self._execute_write(query, params)
        return self._execute_read(query, params, as_dataframe)

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=30)
        try:
            yield conn
        finally:
            conn.close()

    def _is_write_query(self, query: str) -> bool:
        clean_query = re.sub(r'(--.*)|(/\*.*?\*/)', '', query, flags=re.DOTALL).strip()
        first_keyword = re.match(r'^\s*([a-zA-Z]+)', clean_query, re.IGNORECASE)
        return first_keyword and first_keyword.group(1).lower() in self.WRITE_KEYWORDS

    def _execute_write(self, query: str, params: tuple) -> bool:
        """Execute a write query with retry logic."""
        for attempt in range(self.MAX_RETRIES):
            try:
                with self._get_connection() as conn:
                    conn.execute(query, params)
                    conn.commit()
                    self.logger.info(f"Write query succeeded: {query}")
                    return True
            except sqlite3.Error as e:
                self.logger.error(f"Write query failed (attempt {attempt + 1}): {str(e)}")
                time.sleep(1)  # Wait before retrying
        self.logger.error(f"Write query failed after {self.MAX_RETRIES} attempts: {query}")
        return False

    def _execute_read(
        self, 
        query: str, 
        params: tuple, 
        as_dataframe: bool
    ) -> Union[List[Dict], pd.DataFrame]:
        """Execute a read query and return results."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            if as_dataframe:
                return pd.DataFrame(rows, columns=[col[0] for col in cursor.description])
            return [dict(row) for row in rows]

    def export_to_csv(self, query: str, params: tuple = (), filename: str = "export.csv") -> str:
        """
        Export query results to a CSV file.

        :param query: SQL query to execute.
        :param params: Parameters for the query.
        :param filename: Name of the CSV file to save.
        :return: Path to the saved CSV file.
        """
        # Ensure the files directory exists
        files_dir = os.path.join(os.path.dirname(self.db_dir), "files")
        os.makedirs(files_dir, exist_ok=True)

        # Execute the query and save results to CSV
        csv_path = os.path.join(files_dir, filename)
        df = self.execute_query(query, params, as_dataframe=True)
        df.to_csv(csv_path, index=False)
        self.logger.info(f"Exported query results to {csv_path}")
        return csv_path

    def refresh_ddl(self):
        """
        Execute SQL files in the database directory to manage database schema.
        """
        # sql_dir = os.path.join(self.db_dir, "ddl")
        # os.makedirs(sql_dir, exist_ok=True)  # Ensure the ddl directory exists

        sql_files = glob.glob(os.path.join(self.db_dir, "*.sql"))
        # Extract the database name from the file pattern
        for sql_file in sql_files:
            if sql_file.endswith(".sql"):
                db_name = sql_file.replace("_ddl", "").replace(".sql", "")

                db = SQLiteManager(db_name)

                print(f"Processing file: {sql_file}")
                with open(sql_file, "r") as f:
                    DDLs = f.read().split(";")

                for ddl in DDLs:
                    ddl = ddl.strip()
                    if not ddl:
                        continue
                    if ddl.startswith("CREATE") or ddl.startswith("ALTER") or ddl.startswith("DROP"):
                        print(f"Execution susessful: {db.execute_query(ddl)}")
                    else:
                        print(f"Skipping non-DDL statement: {ddl}")

if __name__ == "__main__":
    SQLiteManager().refresh_ddl()