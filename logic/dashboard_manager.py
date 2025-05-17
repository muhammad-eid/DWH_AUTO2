import streamlit as st
from datetime import datetime
from services.session_state import StateManager
from services.db_local_service import SQLiteManager
import pandas as pd
import subprocess

_default_dashboard_states = {
    'show_advanced_trend_section': False,
    'show_basic_trend_section': False,
    'show_missing_runs_section': False,
    'show_not_handled_section': False,
    'show_golden_gates_section': False,
    'show_online_jobs_section': False,
    'show_dumps_section': False,
    'show_extraction_section': False,
    'show_daily_section': False,
    
    'advanced_trend_data': None,
    'basic_trend_data': None,
    'missing_runs_data': None,
    'not_handled_data': None,
    'golden_gates_data': None,
    'online_jobs_data': None,
    'dumps_data': None,
    'extraction_data': None,
    'daily_data': None,
    
    'show_notification': False,
    'notification_message': '',
    'notification_icon': '',
    
    'filter_trend_view': 'all',  # 'all' or 'abnormal'
    'selected_date_range': '7d',  # '7d', '4w', etc.
}

class DashboardManager:
    """
    Class to manage Dashboard metrics and data.
    """
    def __init__(self):
        self.owner = self.__class__.__name__.replace("Manager", "")
        self.states = _default_dashboard_states
        self.db = SQLiteManager(self.owner)
        self.state = StateManager(self.owner, self.states)

    def get_state_manager(self):
        """Get the current state manager instance."""
        return self.state

    def analyze_table_trends(self):
        """Analyze trends using Prophet model for all tables."""
        try:
            query = """
            SELECT table_name, load_data_flag, availability, trend,
                   today_rows_count, last_same_day_rows_count,
                   variance_flag, date_of_run
            FROM table_metrics
            ORDER BY date_of_run DESC
            """
            df = self.db.execute_query(query)
            # TODO: Implement Prophet model analysis
            return df
        except Exception as e:
            st.error(f"Error analyzing trends: {str(e)}")
            return pd.DataFrame()

    def get_basic_trends(self):
        """Get basic trend analysis for tables with Y or '-' flags."""
        try:
            query = """
            SELECT table_name, load_data_flag, availability, trend,
                   today_rows_count, last_same_day_rows_count,
                   variance_flag, date_of_run
            FROM table_metrics
            WHERE load_data_flag IN ('Y', '-')
            ORDER BY date_of_run DESC
            """
            return self.db.execute_query(query)
        except Exception as e:
            st.error(f"Error getting basic trends: {str(e)}")
            return pd.DataFrame()

    def get_missing_runs(self):
        """Get list of missing job runs."""
        try:
            query = """
            SELECT job_name, production
            FROM missing_runs
            """
            return self.db.execute_query(query)
        except Exception as e:
            st.error(f"Error getting missing runs: {str(e)}")
            return pd.DataFrame()

    def get_not_handled_jobs(self):
        """Get list of jobs that haven't been handled."""
        try:
            query = """
            SELECT job_name, production, status, last_run
            FROM job_status
            WHERE handled = 'N'
            """
            return self.db.execute_query(query)
        except Exception as e:
            st.error(f"Error getting not handled jobs: {str(e)}")
            return pd.DataFrame()

    def get_golden_gates_status(self):
        """Get status of Golden Gate nodes."""
        try:
            query = """
            SELECT node_name, status, delay_seconds, last_check
            FROM golden_gates_status
            """
            return self.db.execute_query(query)
        except Exception as e:
            st.error(f"Error getting Golden Gates status: {str(e)}")
            return pd.DataFrame()

    def get_online_jobs_status(self):
        """Get status of online jobs running more than 60 minutes."""
        try:
            # This would typically use dsjob command
            # For now, using placeholder query
            query = """
            SELECT job_name, status, start_time, run_duration
            FROM online_jobs
            WHERE status = 'Running'
            AND run_duration > 60
            """
            return self.db.execute_query(query)
        except Exception as e:
            st.error(f"Error getting online jobs status: {str(e)}")
            return pd.DataFrame()

    def get_dumps_status(self):
        """Get status of dump jobs."""
        try:
            query = """
            SELECT job_name, status, last_run, normal_end_time
            FROM dumps_jobs
            """
            return self.db.execute_query(query)
        except Exception as e:
            st.error(f"Error getting dumps status: {str(e)}")
            return pd.DataFrame()

    def get_extraction_status(self):
        """Get status of extraction jobs."""
        try:
            query = """
            SELECT job_name, status, last_run, normal_end_time
            FROM extraction_jobs
            """
            return self.db.execute_query(query)
        except Exception as e:
            st.error(f"Error getting extraction status: {str(e)}")
            return pd.DataFrame()

    def get_daily_jobs_status(self):
        """Get status of daily jobs."""
        try:
            query = """
            SELECT job_name, status, last_run, normal_end_time
            FROM daily_jobs
            """
            return self.db.execute_query(query)
        except Exception as e:
            st.error(f"Error getting daily jobs status: {str(e)}")
            return pd.DataFrame()

    def update_table_status(self, table_name: str, new_status: str):
        """Update the status of a table manually."""
        try:
            query = """
            UPDATE table_metrics
            SET status = ?
            WHERE table_name = ?
            """
            self.db.execute_query(query, (new_status, table_name))
            return True
        except Exception as e:
            st.error(f"Error updating table status: {str(e)}")
            return False

    def run_dsjob_command(self, command: str) -> str:
        """Execute a dsjob command and return its output."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            st.error(f"Error running dsjob command: {str(e)}")
            return ""

