import streamlit as st
from datetime import datetime
from logic.dashboard_manager import DashboardManager
from services.session_state import StateManager
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded"
)

logic_manager = DashboardManager()
state_manager = logic_manager.get_state_manager()
_OWNER = logic_manager.owner

def show_notification():
    if state_manager.get("show_notification"):
        st.toast(state_manager.get("notification_message"), icon=state_manager.get("notification_icon"))

def show_metric_card(title, value, key):
    """Helper function to show a metric card with consistent styling."""
    with st.container(border=True):
        st.metric(
            title,
            value,
            delta=None,
            help=None,
        )
        st.button(
            label="View Details",
            key=key,
            on_click=lambda: state_manager.set(f"show_{key}_section", True),
            help=f"Click to view detailed {title} section",
            use_container_width=True
            
        )

    
    

def show_advanced_trend_kpi():
    """Show Advanced Trend Analysis KPI card."""
    df = logic_manager.analyze_table_trends()
    abnormal_count = len(df[df['variance_flag'] == 'Y']['table_name'].unique())
    status = "Normal" if abnormal_count == 0 else f"{abnormal_count} Abnormal"
    show_metric_card("Advanced Trend Analysis", status, "advanced_trend")

def show_basic_trend_kpi():
    """Show Basic Trend Analysis KPI card."""
    df = logic_manager.get_basic_trends()
    table_count = len(df[df['load_data_flag'].isin(['Y', '-'])]['table_name'].unique())
    show_metric_card("Basic Trend Analysis", f"{table_count} Tables", "basic_trend")

def show_missing_runs_kpi():
    """Show Missing Runs KPI card."""
    df = logic_manager.get_missing_runs()
    missing_count = len(df)
    status = "Normal" if missing_count == 0 else f"{missing_count} Missing"
    show_metric_card("Missing Runs", status, "missing_runs")

def show_not_handled_kpi():
    """Show Not Handled Jobs KPI card."""
    df = logic_manager.get_not_handled_jobs()
    not_handled_count = len(df)
    status = "Normal" if not_handled_count == 0 else f"{not_handled_count} Not Handled"
    show_metric_card("Not Handled Jobs", status, "not_handled")

def show_golden_gates_kpi():
    """Show Golden Gates KPI card."""
    df = logic_manager.get_golden_gates_status()
    issues = df[df['status'] != 'OK']
    status = "Normal" if len(issues) == 0 else f"{len(issues)} Issues"
    show_metric_card("Golden Gates", status, "golden_gates")

def show_online_jobs_kpi():
    """Show Online Jobs KPI card."""
    df = logic_manager.get_online_jobs_status()
    long_running = len(df)
    status = "Normal" if long_running == 0 else f"{long_running} Long Running"
    show_metric_card("Online Jobs", status, "online_jobs")

def show_dumps_kpi():
    """Show Dumps KPI card."""
    df = logic_manager.get_dumps_status()
    issues = df[df['status'] != 'Normal']
    status = "Normal" if len(issues) == 0 else f"{len(issues)} Issues"
    show_metric_card("Dumps", status, "dumps")

def show_extraction_kpi():
    """Show Extraction KPI card."""
    df = logic_manager.get_extraction_status()
    issues = df[df['status'] != 'Normal']
    status = "Normal" if len(issues) == 0 else f"{len(issues)} Issues"
    show_metric_card("Extraction", status, "extraction")

def show_daily_kpi():
    """Show Daily Jobs KPI card."""
    df = logic_manager.get_daily_jobs_status()
    issues = df[df['status'] != 'Normal']
    status = "Normal" if len(issues) == 0 else f"{len(issues)} Issues"
    show_metric_card("Daily Jobs", status, "daily")

# Detailed section display functions
def show_advanced_trend_section():
    """Display the advanced trend analysis section."""
    st.markdown("### 📈 Advanced Trend Analysis")
    
    # Get trend data
    df = logic_manager.analyze_table_trends()
    if df.empty:
        st.warning("No trend data available")
        return
    
    # Calculate metrics
    abnormal_tables = df[df['variance_flag'] == 'Y']
    total_tables = len(df['table_name'].unique())
    abnormal_count = len(abnormal_tables['table_name'].unique())
    
    col1, col2 = st.columns(2)
    with col1:
        view_option = st.selectbox(
            "View",
            ["All Tables", "Abnormal Only"],
            key="trend_view"
        )
    with col2:
        date_range = st.selectbox(
            "Date Range",
            ["Last 7 Days", "Last 4 Weeks"],
            key="date_range"
        )
    
    # Filter data
    display_df = abnormal_tables if view_option == "Abnormal Only" else df
    
    # Create trend chart
    chart = alt.Chart(display_df).mark_line(point=True).encode(
        x=alt.X('date_of_run:T', title='Date'),
        y=alt.Y('today_rows_count:Q', title='Row Count'),
        color='table_name:N',
        tooltip=['date_of_run:T', 'table_name:N', 'today_rows_count:Q', 'variance_flag:N']
    ).properties(height=400).interactive()
    
    st.altair_chart(chart, use_container_width=True)
    
    # Table view
    st.dataframe(
        display_df,
        use_container_width=True,
        column_config={
            "variance_flag": st.column_config.SelectboxColumn(
                "Status", options=["N", "Y", "-"], width="small"
            )
        }
    )

def show_basic_trend_section():
    """Display the basic trend analysis section."""
    st.markdown("### 📊 Basic Trend Analysis")
    df = logic_manager.get_basic_trends()
    if df.empty:
        st.warning("No trend data available")
        return
    
    # Similar to advanced trend but simpler visualization
    chart = alt.Chart(df).mark_bar().encode(
        x='table_name:N',
        y='today_rows_count:Q',
        color='load_data_flag:N'
    ).properties(height=400)
    
    st.altair_chart(chart, use_container_width=True)
    st.dataframe(df, use_container_width=True)

def show_missing_runs_section():
    """Display missing runs section."""
    st.markdown("### 🔍 Missing Runs")
    df = logic_manager.get_missing_runs()
    if df.empty:
        st.success("No missing runs found")
        return
    st.dataframe(df, use_container_width=True)

def show_not_handled_section():
    """Display not handled jobs section."""
    st.markdown("### ⚠️ Not Handled Jobs")
    df = logic_manager.get_not_handled_jobs()
    if df.empty:
        st.success("No unhandled jobs found")
        return
    st.dataframe(df, use_container_width=True)

def show_golden_gates_section():
    """Display Golden Gates section."""
    st.markdown("### 🌟 Golden Gates Status")
    df = logic_manager.get_golden_gates_status()
    
    # Show nodes with large delays
    delayed_nodes = df[df['delay_seconds'] > 300]  # 5 minutes threshold
    if not delayed_nodes.empty:
        st.warning("Nodes with Large Delays")
        st.dataframe(delayed_nodes, use_container_width=True)
    
    # Show all nodes status
    st.markdown("#### All Nodes Status")
    st.dataframe(df, use_container_width=True)

def show_online_jobs_section():
    """Display online jobs section."""
    st.markdown("### 🔄 Online Jobs")
    df = logic_manager.get_online_jobs_status()
    if df.empty:
        st.success("No long-running jobs found")
        return
    st.dataframe(df, use_container_width=True)

def show_dumps_section():
    """Display dumps section."""
    st.markdown("### 💾 Dumps Status")
    df = logic_manager.get_dumps_status()
    if df.empty:
        st.warning("No dumps data available")
        return
    st.dataframe(df, use_container_width=True)

def show_extraction_section():
    """Display extraction section."""
    st.markdown("### 📤 Extraction Status")
    df = logic_manager.get_extraction_status()
    if df.empty:
        st.warning("No extraction data available")
        return
    st.dataframe(df, use_container_width=True)

def show_daily_section():
    """Display daily jobs section."""
    st.markdown("### 📅 Daily Jobs Status")
    df = logic_manager.get_daily_jobs_status()
    if df.empty:
        st.warning("No daily jobs data available")
        return
    st.dataframe(df, use_container_width=True)

def show_dashboard():
    """Main function to display the dashboard."""
    show_notification()
    st.title("DWH Monitoring Dashboard")
    
    # Display KPI cards in a grid
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        show_advanced_trend_kpi()
        show_basic_trend_kpi()
    
    with col2:
        show_missing_runs_kpi()
        show_not_handled_kpi()
    
    with col3:
        show_golden_gates_kpi()
        show_online_jobs_kpi()
    
    with col4:
        show_dumps_kpi()
        show_daily_kpi()

    with col5:
        show_extraction_kpi()
    
    # Show detailed sections if enabled
    if state_manager.get("show_advanced_trend_section"):
        with st.container(border=True):
            show_advanced_trend_section()
    
    if state_manager.get("show_basic_trend_section"):
        with st.container(border=True):
            show_basic_trend_section()
    
    if state_manager.get("show_missing_runs_section"):
        with st.container(border=True):
            show_missing_runs_section()
    
    if state_manager.get("show_not_handled_section"):
        with st.container(border=True):
            show_not_handled_section()
    
    if state_manager.get("show_golden_gates_section"):
        with st.container(border=True):
            show_golden_gates_section()
    
    if state_manager.get("show_online_jobs_section"):
        with st.container(border=True):
            show_online_jobs_section()
    
    if state_manager.get("show_dumps_section"):
        with st.container(border=True):
            show_dumps_section()
    
    if state_manager.get("show_extraction_section"):
        with st.container(border=True):
            show_extraction_section()
    
    if state_manager.get("show_daily_section"):
        with st.container(border=True):
            show_daily_section()

if __name__ == "__main__":
    show_dashboard()