#!/usr/bin/env python3
"""
Quick Test Runner for AlphaAgent Backend

This script simplifies the testing process by:
1. Checking if the server is running
2. Running the API test suite
3. Collecting and reporting results

Usage:
    python run_quick_test.py
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_step(step_num, text):
    """Print formatted step"""
    print(f"\n[STEP {step_num}] {text}")

def check_server():
    """Check if FastAPI server is running"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 8000))
    sock.close()
    return result == 0

def test_api():
    """Run API test script"""
    test_script = Path(__file__).parent / "data" / "test_portfolios" / "test_api_requests.py"
    
    if not test_script.exists():
        print(f"ERROR: Test script not found at {test_script}")
        return False
    
    try:
        result = subprocess.run([sys.executable, str(test_script)], 
                              capture_output=True, 
                              text=True, 
                              timeout=30)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("ERROR: Test script timed out")
        return False
    except Exception as e:
        print(f"ERROR: Failed to run test script: {e}")
        return False

def main():
    """Main test execution"""
    print_header("AlphaAgent - Quick Test Runner")
    
    # Step 1: Check if server is running
    print_step(1, "Checking if FastAPI server is running...")
    if not check_server():
        print("WARNING: Server is not running on http://127.0.0.1:8000")
        print("\nTo start the server, run:")
        print("  python quickstart.py")
        print("\nThen run this test again in another terminal.")
        print("\n" + "=" * 70)
        sys.exit(1)
    print("SUCCESS: Server is running on http://127.0.0.1:8000")
    
    # Step 2: Run API tests
    print_step(2, "Running API test suite...")
    success = test_api()
    
    # Step 3: Summary
    print_header("Test Summary")
    if success:
        print("SUCCESS: All API tests completed")
        print("\nNext Steps:")
        print("1. Review the API responses above")
        print("2. Check for any errors or warnings")
        print("3. Verify all endpoints are responding correctly")
    else:
        print("WARNING: Some tests may have failed")
        print("Check the output above for details")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
