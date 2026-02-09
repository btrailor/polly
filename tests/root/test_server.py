#!/usr/bin/env python3
"""Test server startup with better error handling"""
import sys
import logging
import traceback

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

try:
    logger.info("Starting test server...")
    
    import uvicorn
    from interfaces.server import create_app
    
    logger.info("Creating app...")
    app = create_app()
    
    logger.info("Running uvicorn...")
    uvicorn.run(app, host="0.0.0.0", port=11436, log_level="info")
    
except KeyboardInterrupt:
    logger.info("Keyboard interrupt received")
    sys.exit(0)
except Exception as e:
    logger.error(f"Fatal error: {e}")
    traceback.print_exc()
    sys.exit(1)
