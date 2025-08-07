# Lite Research Main Application

import streamlit as st
import asyncio
import sys
import os

# Add project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import dependencies
from backend.literesearch.literesearcher import LiteResearcher
from backend.literesearch.research_enums import ReportType, Tone
from backend.literesearch.constants import (
    MIN_QUERY_LENGTH,
    MAX_ITERATIONS_LIMIT,
    MAX_SUBTOPICS_LIMIT,
    MAX_SEARCH_RESULTS_LIMIT,
    MIN_ITERATIONS,
    MIN_SUBTOPICS,
    MIN_SEARCH_RESULTS
)

from langchain_core.globals import set_llm_cache
from langchain_community.cache import SQLiteCache

# Set up cache directory
cache_dir = os.path.join(os.path.dirname(__file__), "..", "data", "llm_cache")
os.makedirs(cache_dir, exist_ok=True)
set_llm_cache(SQLiteCache(database_path=os.path.join(cache_dir, "langchain.db")))

from frontend.ui_components import (
    apply_styles, 
    display_header, 
    display_project_info,
    display_info_message, 
    display_workflow, 
    display_footer,
    get_report_type_display_map,
    show_success_message,
    show_error_message
)

# Set page configuration
st.set_page_config(
    page_title="Lite Research",
    page_icon="🔍",
    initial_sidebar_state="collapsed"
)


def main():
    """Main application entry point"""
    # Apply styles
    apply_styles()

    # Initialize session state
    initialize_session_state()

    # Page layout
    display_header()
    display_project_info()
    display_info_message()
    display_workflow()
    display_research_settings()
    display_report()
    display_footer()


def initialize_session_state():
    """Initialize session state"""
    if "generated_report" not in st.session_state:
        st.session_state.generated_report = ""
    if "verbose_output" not in st.session_state:
        st.session_state.verbose_output = ""


def display_research_settings():
    """Display research settings interface"""
    st.markdown("## Research Settings")
    with st.container(border=True):
        # Research topic input
        query = st.text_input(
            "Enter your research topic:",
            placeholder="e.g., Current applications of AI in education"
        )

        # Basic settings
        col1, col2 = st.columns(2)
        with col1:
            tone = st.selectbox(
                "Select report tone:",
                options=[tone.value for tone in Tone],
                help="Choose the writing style and tone for the report"
            )

        with col2:
            report_type = st.selectbox(
                "Select report type:",
                options=[type.value for type in ReportType],
                format_func=lambda x: get_report_type_display_map().get(x, x),
                help="Choose the report type that best fits your needs"
            )

        # Advanced settings
        max_iterations, max_subtopics, max_search_results_per_query = display_advanced_settings()

        # Start research button
        if st.button("🚀 Start Research", type="primary", use_container_width=True):
            handle_research_request(
                query,
                tone,
                report_type,
                max_iterations,
                max_subtopics,
                max_search_results_per_query
            )


def display_advanced_settings():
    """Display advanced settings and return parameter values"""
    with st.expander("⚙️ Advanced Settings"):
        st.markdown("**Adjust the following parameters to control research depth and breadth**")

        col1, col2, col3 = st.columns(3)
        with col1:
            max_iterations = st.slider(
                "Max Sub-queries",
                min_value=1,
                max_value=10,
                value=3,
                help="Control the maximum number of sub-queries, more queries provide broader coverage"
            )

        with col2:
            max_subtopics = st.slider(
                "Max Subtopics",
                min_value=1,
                max_value=10,
                value=3,
                help="Control the maximum number of subtopics in detailed reports"
            )

        with col3:
            max_search_results_per_query = st.slider(
                "Max Results per Query",
                min_value=1,
                max_value=20,
                value=5,
                help="Control the maximum search results per sub-query, more results provide richer information"
            )

    return max_iterations, max_subtopics, max_search_results_per_query


def handle_research_request(query, tone, report_type, max_iterations, max_subtopics, max_search_results_per_query):
    """Handle research request"""
    # Input validation
    if not query or not query.strip():
        show_error_message("Please enter a research topic before starting research")
        return

    if len(query.strip()) < MIN_QUERY_LENGTH:
        show_error_message(f"Research topic must be at least {MIN_QUERY_LENGTH} characters")
        return

    if max_iterations < MIN_ITERATIONS or max_iterations > MAX_ITERATIONS_LIMIT:
        show_error_message(f"Max sub-queries must be between {MIN_ITERATIONS}-{MAX_ITERATIONS_LIMIT}")
        return

    if max_subtopics < MIN_SUBTOPICS or max_subtopics > MAX_SUBTOPICS_LIMIT:
        show_error_message(f"Max subtopics must be between {MIN_SUBTOPICS}-{MAX_SUBTOPICS_LIMIT}")
        return

    if max_search_results_per_query < MIN_SEARCH_RESULTS or max_search_results_per_query > MAX_SEARCH_RESULTS_LIMIT:
        show_error_message(f"Max search results per query must be between {MIN_SEARCH_RESULTS}-{MAX_SEARCH_RESULTS_LIMIT}")
        return

    # Clear previous output
    st.session_state.verbose_output = ""

    with st.spinner("🔍 Conducting research, please wait..."):
        # Create research progress display area
        verbose_expander = st.expander("📊 Show Research Progress", expanded=True)

        with verbose_expander:
            verbose_container = st.empty()

        # Create callback function to update verbose information
        def update_verbose(message):
            st.session_state.verbose_output += message + "\n"
            verbose_container.text(st.session_state.verbose_output)

        # Execute research
        report = run_research(
            query.strip(),
            report_type,
            tone,
            update_verbose,
            max_iterations,
            max_subtopics,
            max_search_results_per_query
        )

        if report:
            st.session_state.generated_report = report
            show_success_message()


def run_research(query, report_type, tone, verbose_callback, max_iterations, max_subtopics, max_search_results_per_query):
    """Run AI research process"""
    try:
        # Create LiteResearcher instance
        researcher = LiteResearcher(
            query=query,
            report_type=report_type,
            tone=Tone(tone),
            verbose=True,
            verbose_callback=verbose_callback,
            max_iterations=max_iterations,
            max_subtopics=max_subtopics,
            max_search_results_per_query=max_search_results_per_query,
        )

        # Run research process
        report = asyncio.run(researcher.run())
        return report

    except ValueError as e:
        st.error(f"Parameter error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error occurred during research: {str(e)}")
        import traceback
        print(f"Detailed error information: {traceback.format_exc()}")
        return None


def display_report():
    """Display research report"""
    if st.session_state.generated_report:
        st.markdown("## 📄 Research Report")
        with st.container(border=True):
            st.markdown(st.session_state.generated_report)

        # Add download button
        display_download_button()


def display_download_button():
    """Display download button"""
    col1, col2 = st.columns([1, 3])
    with col1:
        st.download_button(
            label="📥 Download Report (Markdown)",
            data=st.session_state.generated_report,
            file_name="AI_Research_Report.md",
            mime="text/markdown",
            use_container_width=True,
        )


if __name__ == "__main__":
    main() 