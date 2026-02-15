"""
LiteLLM unified provider adapter for Phase 11

Wraps LiteLLM's unified API to support 100+ providers through a single adapter,
while maintaining compatibility with Polly's ProviderAdapter interface.
"""

import os
import logging
from pathlib import Path
from typing import AsyncIterator, Optional, Dict, Any
import yaml

try:
    import litellm
    from litellm import acompletion, completion_cost
    from litellm.exceptions import (
        AuthenticationError,
        RateLimitError,
        Timeout,
        APIConnectionError,
        APIError,
        ServiceUnavailableError,
        BadRequestError
    )
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    litellm = None

from .base import (
    ProviderAdapter,
    CompletionResponse,
    ModelInfo,
    ProviderAPIError,
    ProviderRateLimitError,
    ProviderAuthError,
    ProviderConnectionError,
    ProviderTimeoutError,
)

logger = logging.getLogger(__name__)


class LiteLLMAdapter(ProviderAdapter):
    """
    Unified provider adapter using LiteLLM
    
    Supports 100+ providers through LiteLLM's unified API:
    - Anthropic (Claude)
    - OpenAI (GPT)
    - GitHub Models
    - Google (Gemini)
    - Mistral
    - xAI (Grok)
    - Perplexity
    - And many more...
    
    Maintains full compatibility with Polly's ProviderAdapter interface
    and IntelligentRouterV2 routing logic.
    """
    
    def __init__(
        self,
        name: str = "litellm",
        config_path: str = "config/litellm_config.yaml",
        api_keys: Optional[Dict[str, str]] = None
    ):
        """
        Initialize LiteLLM adapter
        
        Args:
            name: Adapter name (default: "litellm")
            config_path: Path to litellm_config.yaml
            api_keys: Optional dict of provider API keys
                     Keys: provider names (anthropic, openai, etc.)
                     Values: API keys
                     Falls back to environment variables if not provided
        """
        super().__init__(name=name)
        
        if not LITELLM_AVAILABLE:
            raise ImportError(
                "LiteLLM library not installed. "
                "Install with: pip install litellm>=1.30.0"
            )
        
        # Load configuration
        self.config = self._load_config(config_path)
        self.config_path = config_path
        
        # Set up API keys
        self._setup_api_keys(api_keys)
        
        # Model mappings (Polly format → LiteLLM format)
        self.model_mappings = self.config.get('model_mappings', {})
        
        # Reverse mappings (LiteLLM format → Polly format)
        self.reverse_model_mappings = {v: k for k, v in self.model_mappings.items()}
        
        # Get default model from first enabled provider
        self.default_model = self._get_default_model()
        
        # LiteLLM settings
        settings = self.config.get('settings', {})
        if settings.get('debug', False):
            litellm.set_verbose = True
        
        logger.info(f"Initialized LiteLLM adapter with {len(self._get_enabled_providers())} providers")
    
    def _load_config(self, config_path: str) -> dict:
        """
        Load litellm_config.yaml
        
        Args:
            config_path: Path to config file
        
        Returns:
            Config dictionary
        """
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"LiteLLM config not found: {config_path}")
        
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        
        logger.info(f"Loaded LiteLLM config from {config_path}")
        return config
    
    def _setup_api_keys(self, api_keys: Optional[Dict[str, str]] = None):
        """
        Set up API keys for enabled providers
        
        Args:
            api_keys: Optional dict of provider API keys
        
        Sets environment variables that LiteLLM will read
        """
        providers = self.config.get('providers', {})
        
        for provider_name, provider_config in providers.items():
            if not provider_config.get('enabled', False):
                continue
            
            env_var = provider_config.get('api_key_env')
            if not env_var:
                continue
            
            # Check if API key provided explicitly
            if api_keys and provider_name in api_keys:
                os.environ[env_var] = api_keys[provider_name]
                logger.debug(f"Set API key for {provider_name} from explicit keys")
            # Otherwise check if already in environment
            elif env_var in os.environ:
                logger.debug(f"Using API key for {provider_name} from environment")
            else:
                logger.warning(f"No API key found for {provider_name} (expected {env_var})")
    
    def _get_enabled_providers(self) -> list[str]:
        """Get list of enabled provider names"""
        providers = self.config.get('providers', {})
        return [
            name for name, config in providers.items()
            if config.get('enabled', False)
        ]
    
    def _get_default_model(self) -> str:
        """Get default model from first enabled provider"""
        providers = self.config.get('providers', {})
        
        # Try to find Anthropic Sonnet as default (best balance)
        for provider_name, provider_config in providers.items():
            if not provider_config.get('enabled', False):
                continue
            
            models = provider_config.get('models', [])
            for model in models:
                model_id = model.get('id', '')
                if 'sonnet' in model_id.lower():
                    return model_id
        
        # Fall back to first available model
        for provider_name, provider_config in providers.items():
            if not provider_config.get('enabled', False):
                continue
            
            models = provider_config.get('models', [])
            if models:
                return models[0].get('id', '')
        
        return "gpt-4o"  # Final fallback
    
    def _map_model_name(self, model: str) -> str:
        """
        Map Polly model name to LiteLLM format
        
        Args:
            model: Polly model identifier
        
        Returns:
            LiteLLM model identifier (with provider prefix)
        """
        # Try direct mapping FIRST (before checking for '/')
        # This allows us to remap "openai/gpt-4o" -> "github/gpt-4o"
        if model in self.model_mappings:
            return self.model_mappings[model]
        
        # If already in LiteLLM format (has provider prefix), return as-is
        if '/' in model:
            return model
        
        # Try to infer provider from model name
        model_lower = model.lower()
        
        if 'claude' in model_lower:
            return f"anthropic/{model}"
        elif 'gpt' in model_lower:
            return f"openai/{model}"
        elif 'gemini' in model_lower:
            return f"gemini/{model}"
        elif 'mistral' in model_lower:
            return f"mistral/{model}"
        elif 'grok' in model_lower:
            return f"xai/{model}"
        elif 'sonar' in model_lower or 'llama' in model_lower:
            return f"perplexity/{model}"
        
        # No mapping found - log warning and try as-is
        logger.warning(f"No mapping found for model {model}, using as-is")
        return model
    
    def _reverse_map_model_name(self, litellm_model: str) -> str:
        """
        Map LiteLLM model name back to Polly format
        
        Args:
            litellm_model: LiteLLM model identifier
        
        Returns:
            Polly model identifier
        """
        if litellm_model in self.reverse_model_mappings:
            return self.reverse_model_mappings[litellm_model]
        
        # If no reverse mapping, strip provider prefix
        if '/' in litellm_model:
            return litellm_model.split('/', 1)[1]
        
        return litellm_model
    
    def _map_error(self, error: Exception) -> Exception:
        """
        Map LiteLLM exception to Polly error type
        
        Args:
            error: LiteLLM exception
        
        Returns:
            Polly ProviderError exception
        """
        error_msg = str(error)
        
        if isinstance(error, AuthenticationError):
            return ProviderAuthError(f"Authentication failed: {error_msg}")
        
        elif isinstance(error, RateLimitError):
            # Try to extract retry_after from error
            retry_after = getattr(error, 'retry_after', 60)
            return ProviderRateLimitError(
                f"Rate limit exceeded: {error_msg}",
                retry_after=retry_after
            )
        
        elif isinstance(error, Timeout):
            return ProviderTimeoutError(f"Request timed out: {error_msg}")
        
        elif isinstance(error, (APIConnectionError, ServiceUnavailableError)):
            return ProviderConnectionError(f"Connection failed: {error_msg}")
        
        elif isinstance(error, BadRequestError):
            return ProviderAPIError(
                f"Bad request: {error_msg}",
                status_code=400
            )
        
        elif isinstance(error, APIError):
            status_code = getattr(error, 'status_code', None)
            return ProviderAPIError(
                f"API error: {error_msg}",
                status_code=status_code
            )
        
        else:
            # Unknown error type - wrap as generic API error
            return ProviderAPIError(f"Unexpected error: {error_msg}")
    
    def _prepare_kwargs(self, model: str, kwargs: dict) -> dict:
        """
        Prepare kwargs for LiteLLM
        
        Args:
            model: LiteLLM model identifier
            kwargs: Original kwargs
        
        Returns:
            Prepared kwargs dict with correct api_base and model name
        """
        prepared = kwargs.copy()
        
        # Extract provider from model
        provider = model.split('/')[0] if '/' in model else None
        
        # Add provider-specific kwargs if needed
        if provider == 'github':
            # GitHub Models uses Azure OpenAI endpoint
            providers_config = self.config.get('providers', {})
            if 'github' in providers_config:
                base_url = providers_config['github'].get('base_url')
                if base_url:
                    prepared['api_base'] = base_url
                    # For GitHub provider, we also need to ensure the API key is set
                    api_key_env = providers_config['github'].get('api_key_env', 'GITHUB_TOKEN')
                    import os
                    api_key = os.environ.get(api_key_env)
                    if api_key:
                        prepared['api_key'] = api_key
        
        # Set timeout from config
        settings = self.config.get('settings', {})
        if 'timeout' not in prepared:
            prepared['timeout'] = settings.get('timeout', 60)
        
        return prepared
    
    async def complete(
        self,
        messages: list[dict],
        model: str = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        **kwargs
    ) -> CompletionResponse:
        """
        Complete a chat conversation via LiteLLM
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model identifier (uses default if None)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)
            **kwargs: Provider-specific options
        
        Returns:
            CompletionResponse with content, tokens, cost
        
        Raises:
            ProviderAPIError: API error
            ProviderRateLimitError: Rate limit exceeded
            ProviderAuthError: Authentication failed
            ProviderConnectionError: Network error
            ProviderTimeoutError: Request timeout
        """
        model = model or self.default_model
        self.current_model = model
        
        # Map model name to LiteLLM format
        litellm_model = self._map_model_name(model)
        
        # Prepare kwargs (adds api_base for GitHub, etc.)
        prepared_kwargs = self._prepare_kwargs(litellm_model, kwargs)
        
        # For GitHub provider, strip the github/ prefix before calling LiteLLM
        # LiteLLM will use the api_base to route to GitHub's Azure endpoint
        provider_prefix = litellm_model.split('/')[0] if '/' in litellm_model else None
        if provider_prefix == 'github':
            # Strip github/ prefix - keep only the model name (e.g., "gpt-4o-mini")
            # LiteLLM will route to GitHub via api_base
            litellm_call_model = litellm_model.split('/', 1)[1] if '/' in litellm_model else litellm_model
        else:
            litellm_call_model = litellm_model
        
        try:
            # Call LiteLLM
            response = await acompletion(
                model=litellm_call_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **prepared_kwargs
            )
            
            # Extract content
            content = response.choices[0].message.content or ""
            
            # Extract tokens
            usage = response.usage
            tokens_in = usage.prompt_tokens if usage else 0
            tokens_out = usage.completion_tokens if usage else 0
            
            # Calculate cost
            cost = self._calculate_cost_from_response(response, litellm_model)
            
            # Get finish reason
            finish_reason = response.choices[0].finish_reason or "stop"
            
            # Build metadata
            metadata = {
                'litellm_model': litellm_model,
                'provider': litellm_model.split('/')[0] if '/' in litellm_model else 'unknown',
            }
            
            if hasattr(response, 'id'):
                metadata['response_id'] = response.id
            
            # Map model name back to Polly format for response
            response_model = self._reverse_map_model_name(litellm_model)
            
            return CompletionResponse(
                content=content,
                model=response_model,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost=cost,
                provider=self.name,
                finish_reason=finish_reason,
                metadata=metadata
            )
        
        except Exception as e:
            logger.error(f"LiteLLM completion error: {e}")
            raise self._map_error(e)
    
    async def stream(
        self,
        messages: list[dict],
        model: str = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream completion tokens via LiteLLM
        
        Args:
            messages: List of message dicts
            model: Model identifier
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Provider-specific options
        
        Yields:
            Content tokens as strings
        
        Raises:
            Same exceptions as complete()
        """
        model = model or self.default_model
        self.current_model = model
        
        # Map model name to LiteLLM format
        litellm_model = self._map_model_name(model)
        
        # Prepare kwargs (adds api_base for GitHub, etc.)
        prepared_kwargs = self._prepare_kwargs(litellm_model, kwargs)
        
        # For GitHub provider, strip the github/ prefix before calling LiteLLM
        # LiteLLM will use the api_base to route to GitHub's Azure endpoint
        provider_prefix = litellm_model.split('/')[0] if '/' in litellm_model else None
        if provider_prefix == 'github':
            # Strip github/ prefix - keep only the model name (e.g., "gpt-4o-mini")
            litellm_call_model = litellm_model.split('/', 1)[1] if '/' in litellm_model else litellm_model
        else:
            litellm_call_model = litellm_model
        
        try:
            # Call LiteLLM with streaming
            response = await acompletion(
                model=litellm_call_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                **prepared_kwargs
            )
            
            # Stream chunks
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
        
        except Exception as e:
            logger.error(f"LiteLLM streaming error: {e}")
            raise self._map_error(e)
    
    def _calculate_cost_from_response(self, response, model: str) -> float:
        """
        Calculate cost from LiteLLM response
        
        Args:
            response: LiteLLM response object
            model: Model identifier
        
        Returns:
            Cost in USD
        """
        try:
            # Try to use LiteLLM's built-in cost calculation
            cost = completion_cost(completion_response=response)
            return cost if cost else 0.0
        except Exception as e:
            logger.warning(f"Could not calculate cost via LiteLLM: {e}")
            
            # Fall back to manual calculation if possible
            if hasattr(response, 'usage') and response.usage:
                tokens_in = response.usage.prompt_tokens
                tokens_out = response.usage.completion_tokens
                
                # Use base estimate (rough average)
                avg_cost_per_1m = 5.0  # $5 per 1M tokens (rough average)
                total_tokens = tokens_in + tokens_out
                return (total_tokens / 1_000_000) * avg_cost_per_1m
            
            return 0.0
    
    def estimate_cost(self, tokens: int, model: str = None) -> float:
        """
        Estimate cost for given token count
        
        Args:
            tokens: Estimated total tokens (input + output)
            model: Model identifier (uses default if None)
        
        Returns:
            Estimated cost in USD
        """
        model = model or self.default_model
        litellm_model = self._map_model_name(model)
        
        try:
            # Use LiteLLM's cost estimation
            # Assume 50/50 split for input/output
            tokens_in = tokens // 2
            tokens_out = tokens - tokens_in
            
            # Create a mock response for cost calculation
            mock_usage = {
                'prompt_tokens': tokens_in,
                'completion_tokens': tokens_out,
                'total_tokens': tokens
            }
            
            # Try to get cost from LiteLLM's pricing database
            from litellm import model_cost
            
            if litellm_model in model_cost:
                pricing = model_cost[litellm_model]
                input_cost = (tokens_in / 1_000_000) * pricing.get('input_cost_per_token', 0) * 1_000_000
                output_cost = (tokens_out / 1_000_000) * pricing.get('output_cost_per_token', 0) * 1_000_000
                return input_cost + output_cost
            
        except Exception as e:
            logger.debug(f"Could not use LiteLLM pricing for {litellm_model}: {e}")
        
        # Fallback to rough average
        avg_cost_per_1m = 5.0  # $5 per 1M tokens
        return (tokens / 1_000_000) * avg_cost_per_1m
    
    async def validate_credentials(self) -> bool:
        """
        Validate API credentials for enabled providers
        
        Returns:
            True if at least one provider's credentials are valid
        
        Raises:
            ProviderAuthError: If all credentials are invalid
        """
        enabled_providers = self._get_enabled_providers()
        
        if not enabled_providers:
            raise ProviderAuthError("No providers enabled in config")
        
        valid_count = 0
        errors = []
        
        # Try each enabled provider
        for provider_name in enabled_providers:
            provider_config = self.config['providers'][provider_name]
            models = provider_config.get('models', [])
            
            if not models:
                continue
            
            # Get first model for this provider
            test_model = models[0]['id']
            litellm_model = self._map_model_name(test_model)
            
            try:
                # Make minimal test call
                response = await acompletion(
                    model=litellm_model,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5,
                    temperature=0
                )
                
                logger.info(f"✓ Provider {provider_name} credentials validated")
                valid_count += 1
            
            except AuthenticationError as e:
                error_msg = f"✗ Provider {provider_name} auth failed: {e}"
                logger.warning(error_msg)
                errors.append(error_msg)
            
            except Exception as e:
                # Other errors don't necessarily mean invalid credentials
                logger.debug(f"Provider {provider_name} validation error (may still be valid): {e}")
                valid_count += 1  # Give benefit of the doubt
        
        if valid_count == 0:
            raise ProviderAuthError(
                f"All provider credentials invalid. Errors: {'; '.join(errors)}"
            )
        
        logger.info(f"Validated {valid_count}/{len(enabled_providers)} providers")
        return True
    
    def get_models(self) -> list[ModelInfo]:
        """
        Get available models from config
        
        Returns:
            List of ModelInfo objects
        """
        models = []
        providers = self.config.get('providers', {})
        
        for provider_name, provider_config in providers.items():
            if not provider_config.get('enabled', False):
                continue
            
            provider_models = provider_config.get('models', [])
            
            for model_config in provider_models:
                model_id = model_config.get('id', '')
                
                # Try to get pricing from LiteLLM
                litellm_model = self._map_model_name(model_id)
                pricing = {'input': 0, 'output': 0}
                
                try:
                    from litellm import model_cost
                    if litellm_model in model_cost:
                        cost_info = model_cost[litellm_model]
                        # Convert per-token to per-1M tokens
                        pricing = {
                            'input': cost_info.get('input_cost_per_token', 0) * 1_000_000,
                            'output': cost_info.get('output_cost_per_token', 0) * 1_000_000
                        }
                except Exception as e:
                    logger.debug(f"Could not load pricing for {litellm_model}: {e}")
                
                model_info = ModelInfo(
                    id=model_id,
                    name=model_config.get('name', model_id),
                    context_length=model_config.get('context_length', 4096),
                    pricing=pricing,
                    capabilities=model_config.get('capabilities', []),
                    provider=provider_name
                )
                
                models.append(model_info)
        
        return models
    
    def supports_streaming(self) -> bool:
        """LiteLLM supports streaming"""
        return True
    
    def get_default_model(self) -> str:
        """Get default model identifier"""
        return self.default_model
