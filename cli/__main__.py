#!/usr/bin/env python3
"""
Entry point for the Smart Search CLI.
"""

import sys
import os

# Add the parent directory to the path so we can import the cli module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli.smart_search import main

if __name__ == "__main__":
    main()