#!/usr/bin/env python3
"""
Test Wave 3 pipeline integration in Polly.

This script tests:
1. Wave 3 pipeline initialization
2. Query decomposition
3. Split routing (local vs cloud)
4. Response synthesis
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.polly import Polly
from core.config import get_config
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_wave3_pipeline():
    """Test Wave 3 pipeline with a RAG-heavy query."""
    
    # Initialize Polly
    logger.info("Initializing Polly...")
    config = get_config()
    polly = Polly(config=config)
    
    # Wait for initialization
    await asyncio.sleep(2)
    
    # Check if Wave 3 is initialized
    wave3_status = {
        'decomposer': polly.query_decomposer is not None,
        'split_router': polly.split_router is not None,
        'synthesizer': polly.synthesizer is not None
    }
    
    logger.info(f"Wave 3 Status: {wave3_status}")
    
    if not all(wave3_status.values()):
        logger.error("Wave 3 pipeline not fully initialized!")
        return False
    
    logger.info("✓ Wave 3 pipeline fully initialized")
    
    # Test queries - complex ones should trigger decomposition
    test_queries = [
        # Complex query (should decompose)
        "What am I trying to learn lately and what are the key concepts in my notes?",
        # Simple query (should NOT decompose)
        "What am I trying to learn lately?"
    ]
    
    for i, test_query in enumerate(test_queries):
        logger.info(f"\n{'='*80}")
        logger.info(f"Test {i+1}/{len(test_queries)}: '{test_query}'")
    for i, test_query in enumerate(test_queries):
        logger.info(f"\n{'='*80}")
        logger.info(f"Test {i+1}/{len(test_queries)}: '{test_query}'")
        logger.info("=" * 80)
        
        # Process query
        response_chunks = []
        async for chunk in polly.query(test_query, stream=True):
            response_chunks.append(chunk)
            # print(chunk, end='', flush=True)
        
        full_response = ''.join(response_chunks)
        logger.info(f"\nResponse length: {len(full_response)} chars")
        
        # Check metadata
        if hasattr(polly, '_last_response_metadata'):
            metadata = polly._last_response_metadata
            logger.info("\nResponse Metadata:")
            logger.info(f"  Provider: {metadata.get('provider', 'unknown')}")
            logger.info(f"  Model: {metadata.get('model', 'unknown')}")
            logger.info(f"  Cost: ${metadata.get('cost', 0):.4f}")
            logger.info(f"  Routing Reason: {metadata.get('routing_reason', 'N/A')}")
            
            if 'wave3_metrics' in metadata:
                metrics = metadata['wave3_metrics']
                logger.info("\nWave 3 Metrics:")
                logger.info(f"  Sub-queries: {metrics.get('sub_queries', 0)}")
                logger.info(f"  Local queries: {metrics.get('local_count', 0)}")
                logger.info(f"  Cloud queries: {metrics.get('cloud_count', 0)}")
                logger.info(f"  Total cost: ${metrics.get('total_cost', 0):.4f}")
    
    # Check if at least one query used Wave 3
    success = False
    if hasattr(polly, '_last_response_metadata'):
        metadata = polly._last_response_metadata
        if 'wave3_metrics' in metadata and metadata['wave3_metrics'].get('local_count', 0) > 0:
            logger.info("\n✓ SUCCESS: Wave 3 routed some queries to local model!")
            success = True
        elif 'wave3_metrics' in metadata:
            logger.warning("\n⚠ Wave 3 ran but didn't route any queries to local")
        else:
            logger.warning("\n⚠ No queries used Wave 3 pipeline")
    else:
        logger.error("\nNo response metadata found")
        success = False
    
    return success


async def main():
    """Main test function."""
    try:
        success = await test_wave3_pipeline()
        if success:
            logger.info("\n" + "=" * 80)
            logger.info("TEST PASSED: Wave 3 pipeline working as expected!")
            logger.info("=" * 80)
            sys.exit(0)
        else:
            logger.error("\n" + "=" * 80)
            logger.error("TEST FAILED: Wave 3 pipeline issues detected")
            logger.error("=" * 80)
            sys.exit(1)
    except Exception as e:
        logger.error(f"\nTest failed with exception: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
