#!/usr/bin/env python3
"""
Multi-Agent Research Pipeline

A modular multi-agent research pipeline that decomposes user research queries,
executes structured, iterative research using subagents, and returns citation-backed,
verifiable reports.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.cli import app

if __name__ == "__main__":
    app() 