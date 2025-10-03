#!/usr/bin/env python3
"""
Main entry point for the Toyota Virtual Training application
This handles any command that Render tries to run
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
    
    # Start the Django application with gunicorn
    cmd = [
        sys.executable, '-m', 'gunicorn',
        'toyota_training.wsgi:application',
        '--bind', f'0.0.0.0:{port}',
        '--workers', '2',
        '--timeout', '30'
    ]
    
    print(f"🚀 Starting Toyota Virtual Training Application...")
    print(f"📡 Port: {port}")
    print(f"🔧 Command: {' '.join(cmd)}")
    
    # Execute the command
    os.execv(sys.executable, cmd)

if __name__ == "__main__":
    main()
