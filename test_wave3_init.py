#!/usr/bin/env python3
"""Test Wave 3 pipeline initialization."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.config import get_config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load config
config = get_config()

# Check Wave 3 configuration
routing_config = config.get('routing', {})
decomp_config = routing_config.get('decomposition', {})
split_config = routing_config.get('split_routing', {})
synthesis_config = routing_config.get('synthesis', {})

print("\n=== Wave 3 Configuration ===")
print(f"routing config exists: {bool(routing_config)}")
print(f"decomposition: {decomp_config}")
print(f"split_routing: {split_config}")
print(f"synthesis: {synthesis_config}")

decomp_enabled = decomp_config.get('enabled', False)
split_enabled = split_config.get('enabled', False)
synthesis_enabled = synthesis_config.get('enabled', False)

print(f"\nWave 3 Status:")
print(f"  Decomposition enabled: {decomp_enabled}")
print(f"  Split routing enabled: {split_enabled}")
print(f"  Synthesis enabled: {synthesis_enabled}")
print(f"  All enabled: {decomp_enabled and split_enabled and synthesis_enabled}")
