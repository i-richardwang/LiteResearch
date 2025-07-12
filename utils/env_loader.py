import os
from dotenv import load_dotenv


def load_env():
    """
    Load environment variables and set them to os.environ
    """
    # Get project root directory path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Build .env file path
    dotenv_path = os.path.join(project_root, '.env')

    # Load .env file
    load_dotenv(dotenv_path)

    print("Environment variables loaded")