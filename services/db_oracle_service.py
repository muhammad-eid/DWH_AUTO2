from typing import Callable, Dict, Optional
import cx_Oracle
import streamlit as st
import pandas as pd

@st.cache_resource
class OracleService:
    """
    A class to manage Oracle database connections and queries.
    This class provides methods to connect to an Oracle database and execute SQL queries.
    Attributes:
        
    """
    def __init__(self, user, password, dsn):
        self.conn = cx_Oracle.connect(user=user, password=password, dsn=dsn)
        
    def run_query(self, query: str, params: tuple = ()) -> pd.DataFrame:
        """
        Execute a SQL query and return the result as a DataFrame.
        Args:
            query (str): The SQL query to execute
            params (tuple): The parameters to bind to the query
        Returns:
            pd.DataFrame: The result of the query as a DataFrame
        """
        df = pd.read_sql(query, self.conn, params=params)
        return df    