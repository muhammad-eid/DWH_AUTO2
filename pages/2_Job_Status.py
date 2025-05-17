import streamlit as st
from datetime import datetime
from logic.job_status_manager import JobStatusManager
from services.session_state import StateManager
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Job Status",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded"
)


logic_manager = JobStatusManager()
state_manager = logic_manager.get_state_manager()
_OWNER = logic_manager.owner

def show_notification():
    if state_manager.get("show_notification"):
        st.toast(state_manager.get("notification_message"), icon=state_manager.get("notification_icon"))


def add_job_form_section():
    if not state_manager.get("show_add_job_section"):
        st.button("Add Job", on_click=lambda: state_manager.toggle("show_add_job_section"), use_container_width=True)
    else:
        with st.container(border=True):
            st.markdown("#### Add New Job")
            col1, col2, col3 = st.columns([5, 3, 3])
            with col1:
                st.text_input("Job Name", key=f"{_OWNER}.job_name", on_change=logic_manager.load_last_job_details)
                st.text_input("Seq. Name", key=f"{_OWNER}.seq_name")
            with col2:
                st.selectbox("Status", logic_manager.status_options_add_job, key=f"{_OWNER}.status")
                st.text_input("Date", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), disabled=True, key=f"{_OWNER}.date")
            with col3:
                st.text_input("Production", key=f"{_OWNER}.production")
                st.text_input("Assigned", key=f"{_OWNER}.by")

            status_val = state_manager.get("status")
            if status_val == "Exceeding":
                st.text_input("OCI Name", key=f"{_OWNER}.oci_name")
            else:
                st.text_area("Error", key=f"{_OWNER}.error")

            col1, col2 = st.columns(2)
            with col1:
                st.button("Cancel", on_click=lambda: state_manager.set("show_add_job_section", False), use_container_width=True)
            with col2:
                st.button("Submit", on_click=logic_manager.add_new_job, use_container_width=True)




def show_data_editor():
    logic_manager.load_last_jobs()
    df = state_manager.get("job_status_df")  # Cached data
    

    st.markdown("### Job Status Table")
    if df.empty:
        st.warning("No data available.")
        return
    if "Fix" not in df.columns:
        df.insert(0, "Fix", False)
    
    if st.checkbox("Select All for Fix"):
        df.loc[df["init_status"] == "Exceeding", "Fix"] = True

    options = df.columns.tolist()
    col_order = st.multiselect("Drag to reorder columns", options=options, default=options, key=f"{_OWNER}.col_order")
    
    # Reorder the dataframe columns based on selection
    df = df[col_order]
    
    st.data_editor(
        df,
        key=f"{_OWNER}.job_status_edited",
        on_change=lambda: state_manager.set("job_status_edited_df", 
            st.session_state[f"{_OWNER}.job_status_edited"]),
        column_config={
            "status": st.column_config.SelectboxColumn("Status", options=logic_manager.status_options),
            "Fix": st.column_config.CheckboxColumn("Fix"),
        },
        disabled=[
            col for col in map(str.lower, state_manager.get("job_status_df").columns)
            if col not in logic_manager.state.get("editable_columns")
        ],
        use_container_width=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("Refresh", on_click=lambda: logic_manager.load_last_jobs(), use_container_width=True)    
    with col2:
        st.button("Fix", on_click=lambda: None, use_container_width=True)  # TODO: Implement apply_quick_fix
    with col3:
        st.button("Save", on_click=lambda: logic_manager.save_changes(), use_container_width=True)


def show_all_jobs():
    st.markdown("### All Jobs")
    if not state_manager.get("show_hist_job_section"):
        st.button("Show All Job", on_click=lambda: state_manager.toggle("show_hist_job_section"), use_container_width=True)
    else:
        logic_manager.load_hist_jobs_options()
        # st.button("Export to CSV", on_click=lambda: logic_manager.export_to_csv(), use_container_width=True)
        # st.button("Refresh DDL", on_click=lambda: logic_manager.refresh_ddl(), use_container_width=True)
        # st.button("Refresh DB", on_click=lambda: logic_manager.refresh_db(), use_container_width=True)
        
        job_status_hist_options = logic_manager.state.get("job_status_hist_options")

        # Show column names for debugging
        # st.write("Columns:", df.columns.tolist())
        # Get unique options for dropdowns
        job_name_options = ["All"] + sorted(job_status_hist_options['job_name'])
        production_options = ["All"] + sorted(job_status_hist_options['production'])
        user_options = ["All"] + sorted(job_status_hist_options['owner'])
        # order_by_options = df.columns.tolist()
        options=['status', 'job_name',  'production']


        with st.expander("Filter Jobs", expanded=state_manager.get("show_hist_job_section")):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.selectbox("Job Name", options=job_name_options, key=f"{_OWNER}.filter_job_name")
                st.selectbox("Production", options=production_options, key=f"{_OWNER}.filter_production")
            with col2:
                st.selectbox("Init Status", options=["All"] + logic_manager.status_options, key=f"{_OWNER}.filtter_init_status")
                st.selectbox("Assigned User", options=user_options, key=f"{_OWNER}.filter_user")
            with col3:
                today = datetime.now().date()
                thirty_days_ago = today - pd.Timedelta(days=30)
                st.date_input("Start Date", key=f"{_OWNER}.filter_start_date",value=thirty_days_ago,max_value=today)
                st.date_input("End Date",key=f"{_OWNER}.filter_end_date",value=today,max_value=today)
            st.button("Apply Filter", on_click=logic_manager.load_hist_jobs, use_container_width=True)

            # Allow drag-and-drop column ordering
            # col_order = st.multiselect("Drag to reorder columns", options=filtered_df.columns.tolist(), default=filtered_df.columns.tolist(), key="col_order")
            # filtered_df = filtered_df[col_order]
            # state_manager.set("job_status_df", filtered_df)
            # df = filtered_df  # For display below

            if state_manager.get("job_status_hist_df") is not None:
                # Drag-and-drop column ordering even without filter
                options=['status', 'job_name',  'production']
                # col_order = st.multiselect("Drag to reorder columns", options=df.columns.tolist(), default=df.columns.tolist(), key="col_order_main")
                st.multiselect("Drag to reorder columns", on_change=logic_manager.reorder_hist_df ,options=options, default=options, key=f"{_OWNER}.col_order_hist")
                
                df = state_manager.get("job_status_hist_df")  # Cached data

                if df.empty:
                    st.warning("No data available.")
                    return

                st.dataframe(df, use_container_width=True)



def show_statistic():
    """
    Display comprehensive job status statistics focusing on initial status:
    - Total jobs over different time periods with trend indicators
    - Initial status distribution and transitions
    - Production-wise analysis
    - Error patterns and distributions
    """
    st.markdown("### Job Status Statistics")  
    if st.button("Show Detailed Statistics", on_click=lambda: state_manager.toggle("show_statistic_section"), use_container_width=True):
        try:
            # Get all required data using init_status focused queries
            init_status_dist_df = logic_manager.get_init_status_distribution()
            init_prod_status_df = logic_manager.get_init_status_by_production()
            init_status_trend_df = logic_manager.get_init_status_trend()
            error_dist_df = logic_manager.get_error_distribution()
            init_status_metrics_df = logic_manager.get_init_status_metrics()
            job_trends = logic_manager.get_job_trends()
            most_repeated_jobs_df = logic_manager.get_most_repeated_jobs()        # Most Repeated Jobs
            

            # Job Counts over Time
            st.markdown("#### 🕒 Job Activity Overview")
            col1, col2, col3, col4 = st.columns(4)
            # Today's stats (compared to same time yesterday)
            with col1:
                with st.container(border=True):
                    st.metric(
                        "Today's Jobs",
                        job_trends['today'],
                        f"{job_trends.get('today_change', 0):.1f}%",
                        help="Number of unique jobs processed today until current time compared to same time yesterday"
                    )

            # Last 24 hours
            with col2:
                with st.container(border=True):
                    st.metric(                    "Last 7 Days",
                        job_trends['last_7_days'],
                        f"{job_trends.get('last_7_days_change', 0):.1f}%",
                        help="Jobs processed in the last 7 days compared to previous 7 days"
                    )

            # Last 30 days
            with col3:
                with st.container(border=True):
                    st.metric(
                        "Last 30 Days",
                        job_trends['last_30_days'],
                        f"{job_trends.get('last_30_days_change', 0):.1f}%",
                        help="Jobs processed in the last 30 days compared to previous 30 days"
                    )

            # Last 90 days
            with col4:
                with st.container(border=True):
                    st.metric(
                        "Last 90 Days",
                        job_trends['last_90_days'],
                        f"{job_trends.get('last_90_days_change', 0):.1f}%",
                        help="Jobs processed in the last 90 days compared to previous 90 days"
                    )

            # Initial Status Overview
            st.markdown("#### 📊 Initial Status Overview")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_jobs = init_status_dist_df['count'].sum()
                with st.container(border=True):
                    aborted_jobs = init_status_dist_df[init_status_dist_df['init_status'] == 'Aborted']['count'].sum()
                    aborted_rate = round((aborted_jobs / total_jobs * 100), 2) if total_jobs > 0 else 0
                    st.metric(
                        "Aborted Rate", 
                        f"{aborted_rate}%",
                        help="Percentage of jobs that started as Aborted"
                    )
            
            with col2:
                stoped_jobs = init_status_dist_df[init_status_dist_df['init_status'] == 'Stoped']['count'].sum()
                stoped_rate = round((stoped_jobs / total_jobs * 100), 2) if total_jobs > 0 else 0
                with st.container(border=True):
                    st.metric(
                        "Stoped Rate", 
                        f"{stoped_rate}%",
                        help="Percentage of jobs that started as stoped"
                    )
            
            with col3:
                exceeding_init = init_status_dist_df[init_status_dist_df['init_status'] == 'Exceeding']['count'].sum()
                exceeding_rate = round((exceeding_init / total_jobs * 100), 2) if total_jobs > 0 else 0
                with st.container(border=True):
                    st.metric(
                        "Initial Exceeding Rate", 
                        f"{exceeding_rate}%",
                        delta_color="inverse",
                        help="Percentage of jobs that started in Exceeding status"
                    )
            
            with col4:
                recovered_jobs = init_status_metrics_df[
                    (init_status_metrics_df['init_status'].isin(['Aborted', 'stoped', 'Exceeding'])) & 
                    (init_status_metrics_df['final_status'] == 'Finished')
                ]['count'].sum()
                recovery_rate = round((recovered_jobs / total_jobs * 100), 2) if total_jobs > 0 else 0
                with st.container(border=True):
                    st.metric(
                        "Recovery Rate", 
                        f"{recovery_rate}%",
                        help="Percentage of initially problematic jobs that were recovered"
                    )# Detailed Visualizations
            st.markdown("#### 📈 Detailed Analysis")        # Initial Status Distribution and Production Analysis
            col1, col2 = st.columns(2)
            with col1:
                # Initial Status Distribution Pie Chart
                init_status_chart = alt.Chart(init_status_dist_df).mark_arc(innerRadius=50).encode(
                    theta='count:Q',
                    color=alt.Color('init_status:N', scale=alt.Scale(scheme='category10')),
                    tooltip=[
                        alt.Tooltip('init_status:N', title='Initial Status'),
                        alt.Tooltip('count:Q', title='Count')
                    ]
                ).properties(
                    title='Initial Status Distribution'
                )
                st.altair_chart(init_status_chart, use_container_width=True)

            with col2:
                # Production Distribution by Initial Status
                init_prod_chart = alt.Chart(init_prod_status_df).mark_bar().encode(
                    x=alt.X('production:N', title='Production Environment'),
                    y=alt.Y('count:Q', stack='normalize', title='Percentage'),
                    color=alt.Color('init_status:N', scale=alt.Scale(scheme='category10')),
                    tooltip=[
                        alt.Tooltip('production:N', title='Production'),
                        alt.Tooltip('init_status:N', title='Initial Status'),
                        alt.Tooltip('count:Q', title='Count')
                    ]
                ).properties(
                    title='Initial Status by Production Environment'
                )
                st.altair_chart(init_prod_chart, use_container_width=True)

            # Time Series Analysis
            st.markdown("#### 📊 Initial Status Trends")
            init_trend_chart = alt.Chart(init_status_trend_df).mark_line(point=True).encode(
                x=alt.X('date:T', title='Date'),
                y=alt.Y('count:Q', title='Number of Jobs'),
                color='init_status:N',
                tooltip=[
                    alt.Tooltip('date:T', title='Date'),
                    alt.Tooltip('init_status:N', title='Initial Status'),
                    alt.Tooltip('count:Q', title='Count')
                ]
            ).properties(
                title='Initial Status Trends Over Time',
                height=300
            )
            st.altair_chart(init_trend_chart, use_container_width=True)

            # Error Analysis
            st.markdown("#### ❌ Error Analysis")
            error_chart = alt.Chart(error_dist_df).mark_bar().encode(
                y=alt.Y('error_type:N', sort='-x', title='Error Type'),
                x=alt.X('count:Q', title='Number of Occurrences'),
                tooltip=[
                    alt.Tooltip('error_type:N', title='Error'),
                    alt.Tooltip('count:Q', title='Occurrences')
                ]
            ).properties(
                title='Top Error Types',
                height=300
            )
            st.altair_chart(error_chart, use_container_width=True)


            # Production-wise Analysis
            st.markdown("#### 🔄 Most Frequent Jobs")
            
            # Display most repeated jobs in a clean table
            if not most_repeated_jobs_df.empty:
                col1, col2 = st.columns([2, 3])
                
                with col1:
                    # Show the top job as a big metric
                    top_job = most_repeated_jobs_df.iloc[0]
                    with st.container(border=True):
                        st.metric(
                            "Most Active Job",
                            top_job['job_name'],
                            f"{top_job['execution_count']} runs",
                            help=f"States: {top_job['init_states']}"
                        )
                
                with col2:
                    # Display all top jobs in a formatted table
                    st.dataframe(
                        most_repeated_jobs_df,
                        column_config={
                            "job_name": "Job Name",
                            "execution_count": st.column_config.NumberColumn(
                                "Total Runs",
                                help="Total number of executions"
                            ),
                            "init_states": st.column_config.TextColumn(
                                "Initial States",
                                help="All initial states this job has had"
                            ),
                            "state_count": st.column_config.NumberColumn(
                                "# States",
                                help="Number of different initial states"
                            ),
                            "percentage": st.column_config.NumberColumn(
                                "% of Total",
                                format="%.2f%%",
                                help="Percentage of total job executions"
                            )
                        },
                        use_container_width=True
                    )


            # Status Transition Analysis
            st.markdown("#### 🔄 Status Flow Analysis")
            
            # Create a simple status flow table
            st.write("Status Transition Summary")
            
            # Display the transition metrics in a clean table format
            transition_summary = init_status_metrics_df.copy()
            
            # Round the percentage to 2 decimal places
            transition_summary['percentage'] = transition_summary['percentage'].round(2)
            
            # Rename columns for better display
            transition_summary.columns = ['Initial Status', 'Current Status', 'Count', 'Percentage (%)']
            
            st.dataframe(
                transition_summary,
                use_container_width=True,
                column_config={
                    'Count': st.column_config.NumberColumn(format="%d"),
                    'Percentage (%)': st.column_config.NumberColumn(format="%.2f %%")
                }
            )

        except Exception as e:
            st.error(f"Error loading statistics: {str(e)}")

    





def main():

    # if st.checkbox("Show Filtering & Status"):
    #     st.markdown("#### Job History Filter & Status")
    #     st.write(filter_data(data_manager))
    #     return

    # state_manager.get("update_in_progress", False)

    show_notification()
    st.title("DataStage Job Status Tracker")

    add_job_form_section()
        

    show_data_editor()

    show_all_jobs()

    show_statistic()

    # if "pending_jobs" in st.session_state:
    #     for job in st.session_state.pending_jobs:
    #         st.write(f"### Processing Job: {job}")
    #         st.info(f"SQL ID Tool for: {job}")
    #         st.divider()

if __name__ == "__main__":
    main()