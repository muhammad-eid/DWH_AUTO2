import streamlit as st
from datetime import datetime
from services.session_state import StateManager
from services.db_local_service import SQLiteManager
import pandas as pd

_default_job_status_staes = {
    'show_add_job_section': False,
    'show_hist_job_section': False,
    'show_job_status_section': False,
    'show_statistic_section':  False,

    'editable_columns':["status", 'error', 'oci_name', "fix", "advice", "owner", "note"],

    'update_in_progress': False,
    'production': '',
    'job_name': '',
    'seq_name': '',
    'status': '',
    'init_status': '',
    'error': '',
    'oci_name': '',
    'date': '',
    'advice': '',
    '_OWNER': '',
    'note': '',
    'sql_id': '',
    'mod_date': '',
    'job_status_df': None,
    'job_status_edited_df': None,
    'job_status_hist_df': None,
    'job_status_hist_options': None,

    'show_notification': False,
    'notification_message': '',
    'notification_icon': '',
}


class JobStatusManager:
    """
    Class to manage job status operations, including loading data, adding new jobs
    and saving changes to the database.
    """
    def __init__(self):
        self.owner = self.__class__.__name__.replace("Manager", "")
        self.states = _default_job_status_staes
        self.db = SQLiteManager(self.owner)
        self.state = StateManager(self.owner, self.states)
        self.status_options_add_job = ["Aborted", "Stoped", "Exceeding"]
        self.status_options = ["Checking", "Finished", "Ignore", "Aborted", "Stoped", "Exceeding", "Other"]
        
    def get_state_manager(self):
        """
        Get the current state of the job status manager.
        """
        return self.state

    def load_last_job_details(self):
        """
        Load the latest job details for the entered job name and populate the form fields.
        """
        job_name: str = self.state.get("job_name")
        if not job_name:
            return

        latest_data = self.db.execute_query('''
                                SELECT * 
                                FROM job_status 
                                WHERE job_name = ? 
                                ORDER BY mod_date DESC 
                                LIMIT 1
                                ''', (job_name.upper(),), as_dataframe=False)
        if latest_data:
            latest_data = latest_data[0]
            self.state.set("seq_name", latest_data.get("seq_name", ""))
            self.state.set("status", latest_data.get("status", ""))
            self.state.set("production", latest_data.get("production", ""))
            self.state.set("oci_name", latest_data.get("oci_name", ""))



    def add_new_job(self):
        """
        Submit new job status data to the database.
        """
        # Validate required fields
        required_fields = ["production", "job_name", "seq_name", "status"]
        for field in required_fields:
            if not self.state.get(field):
                st.error(f"Please fill in the {field} field.")
                return
        if self.state.get("status") != "Exceeding" and not self.state.get("error") :
            st.error(f"Please fill in the error field.")
            return
        if self.state.get("status") == "Exceeding" and not self.state.get("oci_name"):
            st.error(f"Please fill in the oci_name field.")
            return

        query = """
        INSERT INTO job_status (
            production, job_name, seq_name, status, init_status, error, oci_name, date, advice, note, sql_id, mod_date
        ) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            self.state.get("production").upper(),
            self.state.get("job_name").upper(),
            self.state.get("seq_name").upper(),
            self.state.get("status"),
            self.state.get("status"), #init_status
            self.state.get("error"),
            self.state.get("oci_name").upper(),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            self.state.get("advice"),
            self.state.get("note"),
            self.state.get("sql_id"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        # st.error(f'query {query}')
        # st.error(f'params {params}')

        try:
            if self.db.execute_query(query, params):
                st.success("Job status added successfully!")
                self.state.set("show_add_job_section", False)
            else:
                st.error("Failed to add job status. Please try again.")

        except Exception as e:
            st.error(f"An error occurred: {e}")




    def load_last_jobs(self):
        """
        Load the latest job details for the entered job name and populate the form fields.
        """
        latest_data_df = self.db.execute_query('''
                                SELECT * 
                                FROM job_status 
                                WHERE id in (select max(id) from job_status group by job_name) 
                                and mod_date >= DATE('now', '-1 day')
                                ORDER BY mod_date DESC 
                                ''')
        self.state.set("job_status_df", latest_data_df)

    def load_hist_jobs_options(self):
        """
        Load the latest job details for the entered job name and populate the form fields.
        """
        distinct_job_name = self.db.execute_query(f'SELECT distinct job_name FROM job_status')
        distinct_production_name = self.db.execute_query(f'SELECT distinct production FROM job_status')
        distinct_owner = self.db.execute_query(f'SELECT distinct owner FROM job_status')

        self.state.set("job_status_hist_options", {
            'job_name': [name for name in distinct_job_name['job_name'].tolist() if name],
            'production': [name for name in distinct_production_name['production'].tolist() if name],
            'owner': [name for name in distinct_owner['owner'].tolist() if name]
        })

    
    def load_hist_jobs(self, days: int = -30):
        """
        Load the latest job details for the entered job name and populate the form fields.
        """
        filter_job_name = self.state.get("filter_job_name")
        filter_production = self.state.get("filter_production")
        filtter_init_status = self.state.get("filtter_init_status")
        filter_user = self.state.get("filter_user")
        filter_start_date = self.state.get("filter_start_date")
        filter_end_date = self.state.get("filter_end_date")
        # Prepare filters, ignoring "All" and empty values
        filter_conditions = []
        params = []

        filter_fields = {
            "job_name": filter_job_name,
            "production": filter_production,
            "init_status": filtter_init_status,
            "owner": filter_user,
        }
        for field, value in filter_fields.items():
            if value and value != "All":
                filter_conditions.append(f"{field} = ?")
                params.append(value)

        if filter_start_date:
            filter_conditions.append("date >= ?")
            params.append(filter_start_date)
        if filter_end_date:
            filter_conditions.append("date <= ?")
            params.append(filter_end_date)

        query = "SELECT * FROM job_status"
        if filter_conditions:
            query += " WHERE " + " AND ".join(filter_conditions)
        query += " ORDER BY mod_date DESC"

        result = self.db.execute_query(query, tuple(params))
        self.state.set("job_status_hist_df", result)

    def reorder_hist_df(self):
        """
        Reorder the DataFrame based on user-selected column order.
        """
        col_order = self.state.get("col_order_hist")
        if col_order:
            df = self.state.get("job_status_hist_df")
            if df is not None:
                # Reorder columns according to col_order, keeping only columns that exist in df
                col_order_existing = [col for col in col_order if col in df.columns]
                # df = df[col_order_existing]
                # Sort the DataFrame by the selected columns
                if col_order_existing:
                    df = df.sort_values(by=col_order_existing)
                self.state.set("job_status_hist_df", df)
            else:
                st.warning("No data available to reorder.")
        else:
            st.warning("No column order selected.")
 


    
    def save_changes(self):
        updated_df = self.state.get("job_status_edited_df")['edited_rows']
        update_dict = {}
        for index, data in updated_df.items():
            original_row = self.state.get("job_status_df").iloc[int(index)]
            row_id = str(original_row['id'])
            update_dict[row_id] = data
            # Generate and run update query for each edited row
            set_clause = ', '.join([f"{col} = ?" for col in data.keys()])
            query = f"UPDATE job_status SET {set_clause}, mod_date = ? WHERE id = ?"
            params = list(data.values()) + [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), row_id]
            # st.error(f'query {query}')
            # st.error(f'params {params}')
            try:
                self.db.execute_query(query, params)
            except Exception as e:
                st.error(f"Failed to update row {row_id}: {e}")
        st.success("Changes saved successfully!")

    def get_status_distribution(self):
        """Get job status distribution data for charts"""
        query = """
        SELECT status, COUNT(*) as count
        FROM job_status 
        WHERE id IN (SELECT MAX(id) FROM job_status GROUP BY job_name)
        GROUP BY status
        """#self.status_options_add_job
        return self.db.execute_query(query)

    def get_status_by_production(self):
        """Get status distribution by production"""
        query = """
        SELECT production, status, COUNT(*) as count
        FROM job_status 
        WHERE id IN (SELECT MAX(id) FROM job_status GROUP BY job_name)
        GROUP BY production, status
        """
        return self.db.execute_query(query)

    def get_status_trend(self, days=30):
        """Get status trend over time"""
        query = """
        SELECT 
            DATE(date) as date,
            status,
            COUNT(*) as count
        FROM job_status
        WHERE date >= DATE('now', ?)
        GROUP BY DATE(date), status
        ORDER BY date
        """
        return self.db.execute_query(query, (f'-{days} days',))

    def get_error_distribution(self):
        """Get error distribution data"""
        query = """
        SELECT 
            CASE 
                WHEN error IS NULL OR error = '' THEN 'No Error'
                ELSE error
            END as error_type,
            COUNT(*) as count
        FROM job_status
        WHERE id IN (SELECT MAX(id) FROM job_status GROUP BY job_name)
        GROUP BY error_type
        ORDER BY count DESC
        LIMIT 10
        """
        return self.db.execute_query(query)
####################################################
    def get_total_jobs(self, days=None):
        """Get total jobs count with optional time filter"""
        query = """
        SELECT COUNT(*) as count
        FROM job_status 
        WHERE id IN (SELECT MAX(id) FROM job_status GROUP BY job_name)
        """
        if days:
            query += f" AND date >= DATE('now', '-{days} days')"
        result = self.db.execute_query(query)
        return result['count'].iloc[0] if not result.empty else 0    

    def get_job_trends(self):
        """Get job count trends for different time periods with accurate time-based comparison"""
        trends = {}
        
        # Get current time for consistent comparison
        current_time = datetime.now().strftime('%H:%M:%S')
        
        # Get today's jobs until current time
        today_query = f"""
        SELECT COUNT(*) as count
        FROM job_status
        WHERE DATE(date) = DATE('now')
        AND TIME(date) <= TIME('{current_time}')
        """
        today_result = self.db.execute_query(today_query)
        trends['today'] = today_result['count'].iloc[0] if not today_result.empty else 0
        
        # Get yesterday's jobs until same time
        yesterday_query = f"""
        SELECT COUNT(*) as count
        FROM job_status
        WHERE DATE(date) = DATE('now', '-1 day')
        AND TIME(date) <= TIME('{current_time}')
        """
        yesterday_result = self.db.execute_query(yesterday_query)
        yesterday_count = yesterday_result['count'].iloc[0] if not yesterday_result.empty else 0
        
        # Calculate day-over-day change
        if yesterday_count > 0:
            trends['today_change'] = ((trends['today'] - yesterday_count) / yesterday_count) * 100
        else:
            trends['today_change'] = 0
            
        # Get last 7 days and 30 days trends
        for period_name, days in {'last_7_days': 7, 'last_30_days': 30, 'last_90_days': 90}.items():
            current_query = f"""
            SELECT COUNT(*) as count
            FROM job_status
            WHERE date >= DATE('now', '-{days} days')
            """
            current_result = self.db.execute_query(current_query)
            trends[period_name] = current_result['count'].iloc[0] if not current_result.empty else 0
            
            # Calculate change percentage from previous period
            prev_query = f"""
            SELECT COUNT(*) as count
            FROM job_status
            WHERE date >= DATE('now', '-{days*2} days')
            AND date < DATE('now', '-{days} days')
            """
            prev_result = self.db.execute_query(prev_query)
            prev_count = prev_result['count'].iloc[0] if not prev_result.empty else 0
            if prev_count > 0:
                trends[f'{period_name}_change'] = ((trends[period_name] - prev_count) / prev_count) * 100
            else:
                trends[f'{period_name}_change'] = 0

            # st.error(f'query {current_query}')
            # st.error(f'query {prev_query}')

                    
        return trends
        
    def get_status_metrics(self):
        """Get detailed status metrics including init_status vs current status"""
        query = """
        SELECT 
            init_status,
            status as current_status,
            COUNT(*) as count
        FROM job_status
        GROUP BY init_status, status
        """
        return self.db.execute_query(query)

    def get_init_status_distribution(self):
        """Get initial status distribution data for charts"""
        query = """
        SELECT init_status, COUNT(*) as count
        FROM job_status 
        GROUP BY init_status
        """
        return self.db.execute_query(query)

    def get_init_status_by_production(self):
        """Get initial status distribution by production"""
        query = """
        SELECT production, init_status, COUNT(*) as count
        FROM job_status 
        GROUP BY production, init_status
        """
        return self.db.execute_query(query)

    def get_init_status_trend(self, days=30):
        """Get initial status trend over time"""
        query = """
        SELECT 
            DATE(date) as date,
            init_status,
            COUNT(*) as count
        FROM job_status
        WHERE date >= DATE('now', ?)
        GROUP BY DATE(date), init_status
        ORDER BY date
        """
        return self.db.execute_query(query, (f'-{days} days',))

    def get_init_status_metrics(self):
        """Get initial status metrics with transitions to current status"""
        query = """
        SELECT 
            init_status,
            status as final_status,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY init_status), 2) as percentage
        FROM job_status
        GROUP BY init_status, status
        ORDER BY init_status, count DESC
        """
        return self.db.execute_query(query)

    def get_most_repeated_jobs(self, limit=5):
        """Get the most frequently running jobs with their initial states"""
        query = """
        WITH JobCounts AS (
            SELECT 
                job_name,
                COUNT(*) as execution_count,
                GROUP_CONCAT(DISTINCT init_status) as init_states,
                COUNT(DISTINCT init_status) as state_count
            FROM job_status
            GROUP BY job_name
            ORDER BY execution_count DESC
            LIMIT ?
        )
        SELECT 
            job_name,
            execution_count,
            init_states,
            state_count,
            ROUND(execution_count * 100.0 / (SELECT COUNT(*) FROM job_status), 2) as percentage
        FROM JobCounts
        """
        return self.db.execute_query(query, (limit,))





