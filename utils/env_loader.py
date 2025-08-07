import os
from dotenv import load_dotenv

def load_env():
    """
    Load environment variables from .env file or Streamlit secrets
    Compatible with both local development and Streamlit Cloud deployment
    """
    try:
        # Try to import streamlit for cloud deployment
        import streamlit as st
        
        # If running on Streamlit Cloud, use st.secrets
        if hasattr(st, 'secrets') and st.secrets:
            # Copy Streamlit secrets to os.environ for compatibility
            for key, value in st.secrets.items():
                if isinstance(value, str):
                    os.environ[key] = value
            print("✅ Environment variables loaded from Streamlit secrets")
            return
    except (ImportError, AttributeError):
        pass
    
    try:
        # For local development, use .env file
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        dotenv_path = os.path.join(project_root, '.env')
        
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
            print("✅ Environment variables loaded from .env file")
        else:
            print("⚠️  No .env file found, using system environment variables")
    except Exception as e:
        print(f"❌ Error loading environment variables: {e}")
        print("⚠️  Using system environment variables as fallback")