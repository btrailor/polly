"""
Utilities for detecting and preventing blocking operations in async code.

Usage in server.py:

    from utils.async_guards import warn_if_blocking, BlockingDetector

    # Detect slow operations
    @warn_if_blocking(threshold_ms=100)
    @app.get("/endpoint")
    async def my_endpoint():
        ...

    # Profile initialization
    with BlockingDetector("Component initialization"):
        component = HeavyComponent()
"""

import time
import asyncio
import functools
import logging
from contextlib import contextmanager
from typing import Callable, Any

logger = logging.getLogger(__name__)


@contextmanager
def BlockingDetector(operation_name: str, threshold_ms: float = 100):
    """
    Context manager to detect blocking operations.
    
    Warns if the operation takes longer than threshold_ms.
    
    Example:
        with BlockingDetector("Database initialization", threshold_ms=500):
            db = Database()
    """
    start = time.time()
    try:
        yield
    finally:
        duration_ms = (time.time() - start) * 1000
        if duration_ms > threshold_ms:
            logger.warning(
                f"⚠️  BLOCKING OPERATION: {operation_name} took {duration_ms:.0f}ms "
                f"(threshold: {threshold_ms:.0f}ms)"
            )
        else:
            logger.debug(f"✓ {operation_name} took {duration_ms:.0f}ms")


def warn_if_blocking(threshold_ms: float = 100):
    """
    Decorator to warn if an async endpoint blocks for too long.
    
    Example:
        @warn_if_blocking(threshold_ms=50)
        @app.get("/health")
        async def health():
            return {"status": "ok"}
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.time() - start) * 1000
                if duration_ms > threshold_ms:
                    logger.warning(
                        f"⚠️  SLOW ENDPOINT: {func.__name__} took {duration_ms:.0f}ms "
                        f"(threshold: {threshold_ms:.0f}ms)"
                    )
        return wrapper
    return decorator


class InitializationProfiler:
    """
    Profile initialization steps and warn about slow operations.
    
    Example:
        profiler = InitializationProfiler("Polly")
        profiler.step("domains", lambda: self._init_domains())
        profiler.step("rag", lambda: self._init_rag())
        profiler.finish()
    """
    
    def __init__(self, component_name: str, threshold_ms: float = 1000):
        self.component_name = component_name
        self.threshold_ms = threshold_ms
        self.steps = []
        self.start_time = time.time()
    
    def step(self, name: str, func: Callable) -> Any:
        """Execute a step and profile it."""
        step_start = time.time()
        try:
            result = func()
            duration_ms = (time.time() - step_start) * 1000
            
            self.steps.append({
                'name': name,
                'duration_ms': duration_ms,
                'success': True
            })
            
            if duration_ms > self.threshold_ms:
                logger.warning(
                    f"⚠️  SLOW INIT: {self.component_name}.{name} "
                    f"took {duration_ms:.0f}ms (threshold: {self.threshold_ms:.0f}ms)"
                )
            else:
                logger.debug(
                    f"✓ {self.component_name}.{name} took {duration_ms:.0f}ms"
                )
            
            return result
            
        except Exception as e:
            duration_ms = (time.time() - step_start) * 1000
            self.steps.append({
                'name': name,
                'duration_ms': duration_ms,
                'success': False,
                'error': str(e)
            })
            logger.error(
                f"❌ {self.component_name}.{name} failed after {duration_ms:.0f}ms: {e}"
            )
            raise
    
    def finish(self):
        """Log summary of initialization."""
        total_ms = (time.time() - self.start_time) * 1000
        logger.info(
            f"📊 {self.component_name} initialization complete: {total_ms:.0f}ms total"
        )
        
        # Show breakdown if any step was slow
        slow_steps = [s for s in self.steps if s['duration_ms'] > self.threshold_ms]
        if slow_steps:
            logger.warning(f"Slow steps in {self.component_name}:")
            for step in slow_steps:
                logger.warning(f"  - {step['name']}: {step['duration_ms']:.0f}ms")


def make_async_safe(func: Callable) -> Callable:
    """
    Wrap a blocking function to run in a thread pool.
    
    Example:
        # Blocking function
        def read_file(path):
            return open(path).read()
        
        # Make it async-safe
        async_read_file = make_async_safe(read_file)
        
        # Use in async code
        content = await async_read_file('/path/to/file')
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper


# Example usage in Polly class:
"""
from utils.async_guards import InitializationProfiler

def __init__(self, config: Optional[PollyConfig] = None):
    profiler = InitializationProfiler("Polly", threshold_ms=1000)
    
    self.config = config or get_config()
    
    profiler.step("domains", self._init_domains)
    profiler.step("learners", self._init_learners)
    profiler.step("rag", self._init_rag)
    profiler.step("router", self._init_router)
    profiler.step("notes_sync", self._init_notes_sync)
    
    profiler.finish()
"""
