#!/usr/bin/env python3
"""
Polly - Edge-Native Personal AI System

Usage:
    python -m polly "Your query"
    python -m polly index
    python -m polly chat
    python -m polly serve
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from interfaces.cli import cli_main

if __name__ == '__main__':
    cli_main()
