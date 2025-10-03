#!/usr/bin/env python3
"""
Test script to verify gunicorn is available
"""

import subprocess
import sys

def test_gunicorn():
    try:
        result = subprocess.run([sys.executable, '-m', 'gunicorn', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Gunicorn is available: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Gunicorn test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error testing gunicorn: {e}")
        return False

if __name__ == "__main__":
    test_gunicorn()
