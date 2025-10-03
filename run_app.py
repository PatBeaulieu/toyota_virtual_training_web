#!/usr/bin/env python3
"""
Application runner for Render deployment
This script handles the appgunicorn command issue by providing a Python entry point
"""

import os
import sys
import subprocess

def main():
    # Get the port from environment
    port = os.environ.get('PORT', '8000')
    
    # Check if gunicorn is available
    try:
        import gunicorn
        print(f"✅ Gunicorn found: {gunicorn.__version__}")
    except ImportError:
        print("❌ Gunicorn not found, installing...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'gunicorn==21.2.0'])
        print("✅ Gunicorn installed")
    
    # Parse command line arguments (simulate appgunicorn behavior)
    if len(sys.argv) > 1:
        # If called with arguments, use them
        args = sys.argv[1:]
    else:
        # Default arguments for Django app
        args = [
            'toyota_training.wsgi:application',
            '--bind', f'0.0.0.0:{port}',
            '--workers', '2',
            '--timeout', '30'
        ]
    
    # Start the application with gunicorn
    cmd = [sys.executable, '-m', 'gunicorn'] + args
    
    print(f"🚀 Starting application with: {' '.join(cmd)}")
    
    # Execute the command
    os.execv(sys.executable, cmd)

if __name__ == "__main__":
    main()
