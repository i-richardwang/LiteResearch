#!/usr/bin/env python3
"""
Lite Research Launch Script
"""

import subprocess
import sys
import os

def main():
    """Launch Lite Research application"""
    
    # Ensure in project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Application file path
    app_file = os.path.join("frontend", "literesearch_app.py")
    
    if not os.path.exists(app_file):
        print(f"❌ Error: Cannot find application file {app_file}")
        return 1
    
    print("🚀 Starting Lite Research...")
    print(f"📂 Working directory: {script_dir}")
    print(f"📄 Application file: {app_file}")
    print("-" * 50)
    
    try:
        # Launch streamlit application
        cmd = [sys.executable, "-m", "streamlit", "run", app_file]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Launch failed: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Application closed")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 