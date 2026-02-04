#!/usr/bin/env python3
"""Test Polly initialization"""
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Starting test...")

try:
    logger.info("Importing Polly...")
    from core.polly import Polly
    
    logger.info("Creating Polly instance...")
    polly = Polly()
    
    logger.info("SUCCESS! Polly initialized")
    logger.info(f"User: {polly.user_name}")
    
except Exception as e:
    logger.error(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
