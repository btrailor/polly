"""
API Gateway
Phase 23.5: Security Hardening

Wrapper for external API calls that routes through capability broker
for rate limiting and audit logging.
"""

from typing import Optional, Dict, Any, List
import logging
import aiohttp
from datetime import datetime, timedelta
from collections import defaultdict

from core.capability_broker import get_capability_broker
from core.capabilities.types import CapabilityType
from core.audit_logger import get_audit_logger
from core.security_policy import get_security_policy

logger = logging.getLogger(__name__)


class APIGateway:
    """
    Secure API gateway with rate limiting and audit logging.
    
    All external API calls should route through this gateway
    for rate limiting and audit trail.
    """
    
    def __init__(self):
        self.broker = get_capability_broker()
        self.audit_logger = get_audit_logger()
        self.security_policy = get_security_policy()
        
        # Rate limiting: track requests per endpoint
        self.rate_limits: Dict[str, List[datetime]] = defaultdict(list)
        
        # Get rate limit config
        api_config = self.security_policy.get_api_call_config()
        self.rate_limit_per_minute = api_config.get("rate_limit_per_minute", 60)
        self.log_all_requests = api_config.get("log_all_requests", True)
    
    async def request(
        self,
        method: str,
        url: str,
        requestor: str = "polly-core",
        **kwargs
    ) -> aiohttp.ClientResponse:
        """
        Make an HTTP request with rate limiting and audit logging.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            requestor: Who is making the request
            **kwargs: Additional aiohttp request arguments
            
        Returns:
            aiohttp.ClientResponse object
            
        Raises:
            RateLimitError: If rate limit exceeded
        """
        # Extract endpoint for rate limiting (domain + path)
        endpoint = self._extract_endpoint(url)
        
        # Check rate limit
        if not self._check_rate_limit(endpoint):
            logger.warning(f"Rate limit exceeded for {endpoint}")
            raise RateLimitError(f"Rate limit exceeded: {self.rate_limit_per_minute} requests/minute")
        
        # Request capability (for audit logging, not blocking)
        response = self.broker.request_capability(
            capability_type=CapabilityType.API_CALL,
            requestor=requestor,
            resource=endpoint,
            metadata={
                "method": method,
                "url": url
            }
        )
        
        # Log request if enabled
        if self.log_all_requests:
            self.audit_logger.log_capability_request(
                response.request,
                response
            )
            self.audit_logger.log_security_event(
                event_type="api_call",
                metadata={
                    "method": method,
                    "url": url,
                    "endpoint": endpoint,
                    "requestor": requestor
                },
                requestor=requestor,
                resource=endpoint
            )
        
        # Record request for rate limiting
        self.rate_limits[endpoint].append(datetime.now())
        
        # Make actual request
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, **kwargs) as resp:
                return resp
    
    def _extract_endpoint(self, url: str) -> str:
        """Extract endpoint identifier from URL for rate limiting."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            # Use domain + first path segment
            path_parts = parsed.path.strip('/').split('/')
            first_segment = path_parts[0] if path_parts else ''
            return f"{parsed.netloc}/{first_segment}"
        except Exception:
            # Fallback to full URL
            return url
    
    def _check_rate_limit(self, endpoint: str) -> bool:
        """Check if endpoint is within rate limit."""
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        
        # Clean old requests
        self.rate_limits[endpoint] = [
            req_time for req_time in self.rate_limits[endpoint]
            if req_time > one_minute_ago
        ]
        
        # Check limit
        return len(self.rate_limits[endpoint]) < self.rate_limit_per_minute
    
    def get_rate_limit_status(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Get current rate limit status."""
        if endpoint:
            requests_count = len([
                req_time for req_time in self.rate_limits[endpoint]
                if req_time > datetime.now() - timedelta(minutes=1)
            ])
            return {
                "endpoint": endpoint,
                "requests_last_minute": requests_count,
                "limit": self.rate_limit_per_minute,
                "remaining": max(0, self.rate_limit_per_minute - requests_count)
            }
        else:
            # Return all endpoints
            return {
                ep: {
                    "requests_last_minute": len([
                        req_time for req_time in self.rate_limits[ep]
                        if req_time > datetime.now() - timedelta(minutes=1)
                    ]),
                    "limit": self.rate_limit_per_minute
                }
                for ep in self.rate_limits.keys()
            }


class RateLimitError(Exception):
    """Raised when rate limit is exceeded."""
    pass


# Global API gateway instance
_api_gateway: Optional[APIGateway] = None


def get_api_gateway() -> APIGateway:
    """Get global API gateway instance."""
    global _api_gateway
    if _api_gateway is None:
        _api_gateway = APIGateway()
    return _api_gateway
