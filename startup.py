#!/usr/bin/env python3
"""
Startup script for Render deployment
This ensures gunicorn is available and starts the application
"""

import os
import sys
import subprocess

def main():
    # Check if gunicorn is available
    try:
        import gunicorn
        print(f"✅ Gunicorn found: {gunicorn.__version__}")
    except ImportError:
        print("❌ Gunicorn not found, installing...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'gunicorn==21.2.0'])
        print("✅ Gunicorn installed")
    
    # Get the port from environment
    port = os.environ.get('PORT', '8000')
    
    # Start the application
    cmd = [
        sys.executable, '-m', 'gunicorn',
        'toyota_training.wsgi:application',
        '--bind', f'0.0.0.0:{port}',
        '--workers', '2',
        '--timeout', '30'
    ]
    
    print(f"🚀 Starting application with: {' '.join(cmd)}")
    
    # Execute the command
    os.execv(sys.executable, cmd)

if __name__ == "__main__":
    main()
