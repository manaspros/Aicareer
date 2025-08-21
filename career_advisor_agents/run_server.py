#!/usr/bin/env python3
"""
Run script for Career Advisor Agent System
This script properly sets up the Python path and runs the FastAPI server.
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Main entry point"""
    import uvicorn
    
    # Run the FastAPI application
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(current_dir)],
        log_level="info"
    )

if __name__ == "__main__":
    main()