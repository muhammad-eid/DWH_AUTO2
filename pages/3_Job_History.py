import streamlit as st
from states.state_manager import create_state, set_state, get_state, toggle_state
from services.s2_Job_hist import generate_query, run

def render():
    # Initial state setup
    create_state('job_hist', 'job_hist_query', '')
    create_state('job_hist', 'job_hist_df', '')
    create_state('job_hist', 'loading', False)
    create_state('job_hist', 'loaded', False)
    create_state('job_hist', 'show_query', False)
    

    st.header('Job History')
    col1, col2 = st.columns([3, 1])

    # Input fields
    with col1:
        jobs_name = st.text_input('Job/Seq Name', key='job_input')
    with col2:
        period = st.text_input('Num Days', value='10', key='period_input')

    # Input validation
    job_provided = bool(jobs_name.strip())
    period_valid = period.strip().isdigit()

    if not job_provided:
        st.warning('⚠️ Please enter a Job/Seq Name.')

    if not period_valid:
        st.warning('⚠️ Num Days must be a valid number.')

    if job_provided and period_valid:
        col1, col2 = st.columns([2, 2])
        with col1:
            st.button(
                "Search", 
                use_container_width=True, 
                key="search_btn", 
                on_click=run, 
                args=(jobs_name.strip(), int(period.strip()))
            )
        with col2:
            st.button(
                "Show Query" if not get_state('job_hist', 'show_query') else "Hide Query", 
                use_container_width=True, 
                on_click=generate_query, 
                args=(jobs_name.strip(), int(period.strip()))
            )

    # Output display
    if get_state('job_hist', 'loaded'):
        st.data_editor(get_state('job_hist', 'job_hist_df'))
    if get_state('job_hist', 'show_query'):
        st.text_area('SQL Query', get_state('job_hist', 'job_hist_query'))

if __name__ == '__main__':
    render()