#!/usr/bin/env python3
"""
Test script for the Smart Search CLI.
"""

import subprocess
import sys
import os

def test_cli_help():
    """Test that the CLI help works."""
    result = subprocess.run([
        sys.executable, '-m', 'cli.smart_search', '--help'
    ], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
    
    assert result.returncode == 0
    assert 'Smart Search' in result.stdout
    print("✅ CLI help test passed")

def test_cli_no_args():
    """Test that the CLI shows help when called without arguments."""
    result = subprocess.run([
        sys.executable, '-m', 'cli.smart_search'
    ], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
    
    assert result.returncode == 0
    assert 'Smart Search' in result.stdout
    print("✅ CLI no args test passed")

if __name__ == "__main__":
    print("Running CLI tests...")
    test_cli_help()
    test_cli_no_args()
    print("🎉 All CLI tests passed!")