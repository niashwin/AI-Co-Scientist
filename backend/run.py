#!/usr/bin/env python3
"""
Main runner script for the AI Co-Scientist MVP Backend
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Configuration
    host = os.getenv("BACKEND_HOST", "127.0.0.1")
    port = int(os.getenv("BACKEND_PORT", 8000))
    environment = os.getenv("ENVIRONMENT", "development")
    
    # Determine if we should reload based on environment
    reload = environment == "development"
    
    print(f"Starting AI Co-Scientist MVP Backend...")
    print(f"Environment: {environment}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Reload: {reload}")
    print(f"API Documentation: http://{host}:{port}/docs")
    print(f"WebSocket: ws://{host}:{port}/ws")
    
    # Run the server
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info" if environment == "development" else "warning",
        access_log=True
    ) 