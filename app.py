#!/usr/bin/env python3
"""
Application entry point for Render deployment
This handles the appgunicorn command issue
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
