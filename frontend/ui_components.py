"""
Lite Research UI Components Module
Contains style definitions and static UI components
"""

import streamlit as st

# Version number
VERSION = "1.0.0"


def apply_styles():
    """Apply page styles"""
    st.markdown("""
    <style>
    .stTextInput>div>div>input {
        border-color: #E0E0E0;
    }
    .stProgress > div > div > div > div {
        background-color: #4F8BF9;
    }
    h2, h3, h4 {
        border-bottom: 2px solid !important;
        padding-bottom: 0.5rem !important;
        margin-bottom: 1rem !important;
    }
    h2 {
        color: #1E90FF !important;
        border-bottom-color: #1E90FF !important;
        font-size: 1.8rem !important;
        margin-top: 1.5rem !important;
    }
    h3 {
        color: #16A085 !important;
        border-bottom-color: #16A085 !important;
        font-size: 1.5rem !important;
        margin-top: 1rem !important;
    }
    h4 {
        color: #E67E22 !important;
        border-bottom-color: #E67E22 !important;
        font-size: 1.2rem !important;
        margin-top: 0.5rem !important;
    }
    .workflow-container {
        background-color: rgba(248, 249, 250, 0.8);
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(0, 0, 0, 0.125);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .workflow-step {
        margin-bottom: 1rem;
        padding: 0.8rem;
        background: white;
        border-radius: 0.3rem;
        border-left: 4px solid #4F8BF9;
    }
    .footer {
        margin-top: 3rem;
        padding: 2rem 0;
        text-align: center;
        color: #666;
        border-top: 1px solid #E0E0E0;
    }
    .footer a {
        color: #4F8BF9;
        text-decoration: none;
    }
    .footer a:hover {
        text-decoration: underline;
    }
    @media (prefers-color-scheme: dark) {
        .workflow-container {
            background-color: rgba(33, 37, 41, 0.8);
            border-color: rgba(255, 255, 255, 0.125);
        }
        .workflow-step {
            background: rgba(255, 255, 255, 0.05);
        }
        h1, h2 {
            color: #3498DB;
            border-bottom-color: #3498DB;
        }
        h3 {
            color: #2ECC71;
            border-bottom-color: #2ECC71;
        }
        h4 {
            color: #F39C12;
            border-bottom-color: #F39C12;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def display_header():
    """Display page title"""
    st.title("🔍 Lite Research")
    st.markdown("---")


def display_project_info():
    """Display project information including author and repository links."""
    st.markdown(
        """
        <style>
        .project-info {
            background-color: rgba(240, 242, 246, 0.5);
            border-left: 4px solid #1E90FF;
            padding: 0.75rem 1rem;
            margin: 1rem 0;
            border-radius: 0 0.25rem 0.25rem 0;
            font-size: 0.9rem;
        }
        .project-info a {
            text-decoration: none;
            color: #1E90FF;
        }
        .project-info a:hover {
            text-decoration: underline;
        }
        .project-separator {
            color: #666;
        }
        @media (prefers-color-scheme: dark) {
            .project-info {
                background-color: rgba(33, 37, 41, 0.3);
                border-left-color: #3498DB;
            }
            .project-info a {
                color: #3498DB;
            }
            .project-separator {
                color: #999;
            }
        }
        </style>
        <div class="project-info">
            <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
                <span>
                    <strong>🚀 Open Source Project</strong> by
                    <a href="https://github.com/i-richardwang" target="_blank">
                        <strong>Richard Wang</strong>
                    </a>
                </span>
                <span class="project-separator">•</span>
                <a href="https://github.com/i-richardwang/literesearch" target="_blank"
                   style="display: flex; align-items: center; gap: 0.3rem;">
                    <span>📂</span> <strong>GitHub Repository</strong>
                </a>
                <span class="project-separator">•</span>
                <span class="project-separator">⭐ Star if you find it useful!</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def display_info_message():
    """Display Lite Research functionality introduction"""
    st.info(
        """
    **Lite Research** is an intelligent research tool based on large language models, designed to assist users in conducting in-depth topic research.

    This tool can automatically generate relevant sub-queries based on user-provided topics, collect information from multiple sources, and analyze and organize it.
    The system supports multiple report types and tones, and can generate customized research reports according to user needs.

    ✨ **Use Cases**: Academic research, market research, technical analysis, industry reports, and other scenarios that require rapid acquisition and organization of specific topic information.
    """
    )


def display_workflow():
    """Display Lite Research architecture diagram"""
    import os
    
    with st.expander("🏗️ View System Architecture", expanded=False):
        # Path to the architecture diagram
        diagram_path = os.path.join(os.path.dirname(__file__), "assets", "architecture_diagram.png")
        
        if os.path.exists(diagram_path):
            st.image(
                diagram_path,
                caption="Lite Research System Architecture - Complete workflow from user input to final report generation",
                use_container_width=True
            )
            st.markdown(
                """
                **Architecture Overview:**
                - **🎯 Agent Selection**: Intelligent selection of appropriate AI agents based on research topics
                - **🔍 Query Generation**: Automatic generation of comprehensive sub-queries  
                - **⚡ Parallel Processing**: Concurrent web search and information retrieval
                - **🧠 Content Compression**: Vector-based extraction of most relevant information
                - **📄 Report Generation**: Structured output with customizable types and tones
                """,
                unsafe_allow_html=True,
            )
        else:
            # Fallback to text description if image not found
            st.warning("⚠️ Architecture diagram not found. Run `python scripts/generate_architecture_diagram.py` to generate it.")
            st.markdown(
                """
                **System Architecture Components:**
                1. 🎯 **Intelligent Agent Selection** - Topic-based AI agent matching
                2. 🔍 **Sub-query Generation** - Comprehensive research scope coverage
                3. ⚡ **Parallel Information Retrieval** - Concurrent web search processing
                4. 🧠 **Context Compression** - Vector-based relevance filtering
                5. 📄 **Report Generation** - Structured output with custom formatting
                """
            )


def display_footer():
    """Display footer information"""
    st.markdown(
        f"""
        <div class="footer">
            <p>© 2024 Lite Research |
            <a href="https://github.com/i-richardwang/literesearch" target="_blank">GitHub Project</a> |
            Author: Richard Wang</p>
            <p><small>Intelligent research tool built with large language model technology | Version {VERSION}</small></p>
        </div>
        """,
        unsafe_allow_html=True
    )


def get_report_type_display_map():
    """Get report type display mapping"""
    return {
        "research_report": "📊 Comprehensive Research Report (Complete analysis and summary)",
        "resource_report": "📚 Resource Summary Report (Related materials and reference list)",
        "outline_report": "📝 Research Outline (Main points and structural framework)",
        "detailed_report": "📋 Detailed In-depth Report (Comprehensive and thorough analysis)",
        "custom_report": "⚙️ Custom Report (Customized according to specific requirements)",
        "subtopic_report": "🔬 Subtopic Report (In-depth analysis of specific sub-topics)",
    }


def show_success_message():
    """Display research completion success message"""
    st.success("✅ Research completed!")
    st.balloons()  # Add celebration effect


def show_error_message(message):
    """Display error message"""
    st.error(f"⚠️ {message}")