#!/usr/bin/env python3
"""
This script handles the appgunicorn command that Render is trying to run
"""

import os
import sys
import subprocess

def main():
    # Install gunicorn if needed
    try:
        import gunicorn
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'gunicorn==21.2.0'])
    
    # Get port from environment
    port = os.environ.get('PORT', '8000')
    
    # Start gunicorn with the arguments
    cmd = [
        sys.executable, '-m', 'gunicorn',
        'toyota_training.wsgi:application',
        '--bind', f'0.0.0.0:{port}',
        '--workers', '2',
        '--timeout', '30'
    ]
    
    print(f"🚀 Starting Toyota Virtual Training Application...")
    os.execv(sys.executable, cmd)

if __name__ == "__main__":
    main()
