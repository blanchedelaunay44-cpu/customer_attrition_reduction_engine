#!/usr/bin/env python3
"""
Simple API starter script that uses pre-trained models
"""
import os
import sys
import uvicorn

def main():
    """Start the FastAPI server with pre-trained models"""
    print("🚀 Starting C.A.R.E. API Server...")
    print("📍 Location: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    print("⏳ Loading pre-trained models...")
    
    # Start server with import string for proper reload/worker support
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload to prevent retraining
        log_level="info"
    )

if __name__ == "__main__":
    main()