"""
LiteLLM unified provider adapter.

Wraps LiteLLM's unified API to support 100+ providers through a single adapter,
while maintaining compatibility with the ProviderAdapter interface.
"""

import os
import logging
from pathlib import Path
from typing import AsyncIterator, Optional, Dict, Any

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
    Unified provider adapter using LiteLLM.
    Supports 100+ providers; maintains compatibility with ProviderAdapter interface.
    """

    def __init__(
        self,
        name: str = "litellm",
        config_path: str = "config/litellm_config.yaml",
        api_keys: Optional[Dict[str, str]] = None
    ):
        super().__init__(name=name)

        if not LITELLM_AVAILABLE:
            raise ImportError(
                "LiteLLM library not installed. "
                "Install with: pip install litellm>=1.30.0"
            )

        self.config = self._load_config(config_path)
        self.config_path = config_path
        self._setup_api_keys(api_keys)
        self.model_mappings = self.config.get('model_mappings', {})
        self.reverse_model_mappings = {v: k for k, v in self.model_mappings.items()}
        self.default_model = self._get_default_model()

        settings = self.config.get('settings', {})
        if settings.get('debug', False):
            litellm.set_verbose = True

        logger.info(f"Initialized LiteLLM adapter with {len(self._get_enabled_providers())} providers")

    def _load_config(self, config_path: str) -> dict:
        import yaml
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"LiteLLM config not found: {config_path}")
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded LiteLLM config from {config_path}")
        return config

    def _setup_api_keys(self, api_keys: Optional[Dict[str, str]] = None):
        providers = self.config.get('providers', {})
        for provider_name, provider_config in providers.items():
            if not provider_config.get('enabled', False):
                continue
            env_var = provider_config.get('api_key_env')
            if not env_var:
                continue
            if api_keys and provider_name in api_keys:
                os.environ[env_var] = api_keys[provider_name]
                logger.debug(f"Set API key for {provider_name} from explicit keys")
            elif env_var in os.environ:
                logger.debug(f"Using API key for {provider_name} from environment")
            else:
                logger.warning(f"No API key found for {provider_name} (expected {env_var})")

    def _get_enabled_providers(self) -> list:
        providers = self.config.get('providers', {})
        return [name for name, config in providers.items() if config.get('enabled', False)]

    def _get_default_model(self) -> str:
        providers = self.config.get('providers', {})
        for provider_name, provider_config in providers.items():
            if not provider_config.get('enabled', False):
                continue
            models = provider_config.get('models', [])
            for model in models:
                model_id = model.get('id', '')
                if 'sonnet' in model_id.lower():
                    return model_id
        for provider_name, provider_config in providers.items():
            if not provider_config.get('enabled', False):
                continue
            models = provider_config.get('models', [])
            if models:
                return models[0].get('id', '')
        return "gpt-4o"

    def _map_model_name(self, model: str) -> str:
        if '/' in model:
            return model
        if model in self.model_mappings:
            return self.model_mappings[model]
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
        logger.warning(f"No mapping found for model {model}, using as-is")
        return model

    def _reverse_map_model_name(self, litellm_model: str) -> str:
        if litellm_model in self.reverse_model_mappings:
            return self.reverse_model_mappings[litellm_model]
        if '/' in litellm_model:
            return litellm_model.split('/', 1)[1]
        return litellm_model

    def _map_error(self, error: Exception) -> Exception:
        error_msg = str(error)
        if isinstance(error, AuthenticationError):
            return ProviderAuthError(f"Authentication failed: {error_msg}")
        elif isinstance(error, RateLimitError):
            retry_after = getattr(error, 'retry_after', 60)
            return ProviderRateLimitError(f"Rate limit exceeded: {error_msg}", retry_after=retry_after)
        elif isinstance(error, Timeout):
            return ProviderTimeoutError(f"Request timed out: {error_msg}")
        elif isinstance(error, (APIConnectionError, ServiceUnavailableError)):
            return ProviderConnectionError(f"Connection failed: {error_msg}")
        elif isinstance(error, BadRequestError):
            return ProviderAPIError(f"Bad request: {error_msg}", status_code=400)
        elif isinstance(error, APIError):
            status_code = getattr(error, 'status_code', None)
            return ProviderAPIError(f"API error: {error_msg}", status_code=status_code)
        return ProviderAPIError(f"Unexpected error: {error_msg}")

    def _prepare_kwargs(self, model: str, kwargs: dict) -> dict:
        prepared = kwargs.copy()
        provider = model.split('/')[0] if '/' in model else None
        if provider == 'github':
            providers_config = self.config.get('providers', {})
            if 'github' in providers_config:
                base_url = providers_config['github'].get('base_url')
                if base_url:
                    prepared['api_base'] = base_url
        settings = self.config.get('settings', {})
        if 'timeout' not in prepared:
            prepared['timeout'] = settings.get('timeout', 60)
        return prepared

    async def complete(
        self,
        messages: list,
        model: str = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        **kwargs
    ) -> CompletionResponse:
        model = model or self.default_model
        self.current_model = model
        litellm_model = self._map_model_name(model)
        prepared_kwargs = self._prepare_kwargs(litellm_model, kwargs)
        try:
            response = await acompletion(
                model=litellm_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **prepared_kwargs
            )
            content = response.choices[0].message.content or ""
            usage = response.usage
            tokens_in = usage.prompt_tokens if usage else 0
            tokens_out = usage.completion_tokens if usage else 0
            cost = self._calculate_cost_from_response(response, litellm_model)
            finish_reason = response.choices[0].finish_reason or "stop"
            metadata = {
                'litellm_model': litellm_model,
                'provider': litellm_model.split('/')[0] if '/' in litellm_model else 'unknown',
            }
            if hasattr(response, 'id'):
                metadata['response_id'] = response.id
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
        messages: list,
        model: str = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        **kwargs
    ) -> AsyncIterator[str]:
        model = model or self.default_model
        self.current_model = model
        litellm_model = self._map_model_name(model)
        prepared_kwargs = self._prepare_kwargs(litellm_model, kwargs)
        try:
            response = await acompletion(
                model=litellm_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                **prepared_kwargs
            )
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
        except Exception as e:
            logger.error(f"LiteLLM streaming error: {e}")
            raise self._map_error(e)

    def _calculate_cost_from_response(self, response, model: str) -> float:
        try:
            cost = completion_cost(completion_response=response)
            return cost if cost else 0.0
        except Exception as e:
            logger.warning(f"Could not calculate cost via LiteLLM: {e}")
            if hasattr(response, 'usage') and response.usage:
                tokens_in = response.usage.prompt_tokens
                tokens_out = response.usage.completion_tokens
                total_tokens = tokens_in + tokens_out
                return (total_tokens / 1_000_000) * 5.0
            return 0.0

    def estimate_cost(self, tokens: int, model: str = None) -> float:
        model = model or self.default_model
        litellm_model = self._map_model_name(model)
        try:
            from litellm import model_cost
            tokens_in = tokens // 2
            tokens_out = tokens - tokens_in
            if litellm_model in model_cost:
                pricing = model_cost[litellm_model]
                input_cost = (tokens_in / 1_000_000) * pricing.get('input_cost_per_token', 0) * 1_000_000
                output_cost = (tokens_out / 1_000_000) * pricing.get('output_cost_per_token', 0) * 1_000_000
                return input_cost + output_cost
        except Exception as e:
            logger.debug(f"Could not use LiteLLM pricing for {litellm_model}: {e}")
        return (tokens / 1_000_000) * 5.0

    async def validate_credentials(self) -> bool:
        enabled_providers = self._get_enabled_providers()
        if not enabled_providers:
            raise ProviderAuthError("No providers enabled in config")
        valid_count = 0
        errors = []
        for provider_name in enabled_providers:
            provider_config = self.config['providers'][provider_name]
            models = provider_config.get('models', [])
            if not models:
                continue
            test_model = models[0]['id']
            litellm_model = self._map_model_name(test_model)
            try:
                await acompletion(
                    model=litellm_model,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5,
                    temperature=0
                )
                logger.info(f"✓ Provider {provider_name} credentials validated")
                valid_count += 1
            except AuthenticationError as e:
                errors.append(f"✗ Provider {provider_name} auth failed: {e}")
            except Exception as e:
                logger.debug(f"Provider {provider_name} validation error: {e}")
                valid_count += 1
        if valid_count == 0:
            raise ProviderAuthError(f"All provider credentials invalid. Errors: {'; '.join(errors)}")
        return True

    def get_models(self) -> list:
        models = []
        providers = self.config.get('providers', {})
        for provider_name, provider_config in providers.items():
            if not provider_config.get('enabled', False):
                continue
            for model_config in provider_config.get('models', []):
                model_id = model_config.get('id', '')
                litellm_model = self._map_model_name(model_id)
                pricing = {'input': 0, 'output': 0}
                try:
                    from litellm import model_cost
                    if litellm_model in model_cost:
                        cost_info = model_cost[litellm_model]
                        pricing = {
                            'input': cost_info.get('input_cost_per_token', 0) * 1_000_000,
                            'output': cost_info.get('output_cost_per_token', 0) * 1_000_000
                        }
                except Exception:
                    pass
                models.append(ModelInfo(
                    id=model_id,
                    name=model_config.get('name', model_id),
                    context_length=model_config.get('context_length', 4096),
                    pricing=pricing,
                    capabilities=model_config.get('capabilities', []),
                    provider=provider_name
                ))
        return models

    def supports_streaming(self) -> bool:
        return True

    def get_default_model(self) -> str:
        return self.default_model
