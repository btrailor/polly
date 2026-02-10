"""
Google Gemini provider adapter for Phase 11
"""

from typing import AsyncIterator, Optional
import logging

try:
    import google.generativeai as genai
    from google.generativeai.types import GenerationConfig
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None
    GenerationConfig = None

from ..base import (
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


class GeminiAdapter(ProviderAdapter):
    """
    Google Gemini provider adapter
    
    Supports:
    - Gemini 1.5 Flash (fastest, cost-effective)
    - Gemini 1.5 Pro (balanced quality)
    - Gemini 2.0 Flash Exp (experimental, highest performance)
    """
    
    # Model pricing (per 1M tokens)
    # Source: https://ai.google.dev/pricing (as of Feb 2026)
    PRICING = {
        "gemini-1.5-flash": {"in": 0.075, "out": 0.30},
        "gemini-1.5-flash-8b": {"in": 0.0375, "out": 0.15},
        "gemini-1.5-pro": {"in": 1.25, "out": 5.00},
        "gemini-2.0-flash-exp": {"in": 0.00, "out": 0.00},  # Free tier during preview
    }
    
    # Model context windows
    CONTEXT_WINDOWS = {
        "gemini-1.5-flash": 1_000_000,
        "gemini-1.5-flash-8b": 1_000_000,
        "gemini-1.5-pro": 2_000_000,
        "gemini-2.0-flash-exp": 1_000_000,
    }
    
    def __init__(self, api_key: str):
        super().__init__(name="gemini", api_key=api_key)
        
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "Google Generative AI library not installed. "
                "Install with: pip install google-generativeai>=0.3.0"
            )
        
        # Configure API key
        genai.configure(api_key=api_key)
        
        self.default_model = "gemini-1.5-flash"
        self._model_cache = {}
    
    def _get_model(self, model_name: str):
        """Get or cache a Gemini model instance"""
        if model_name not in self._model_cache:
            self._model_cache[model_name] = genai.GenerativeModel(model_name)
        return self._model_cache[model_name]
    
    def _convert_messages_to_gemini_format(self, messages: list[dict]) -> tuple[Optional[str], list[dict]]:
        """
        Convert OpenAI-style messages to Gemini format
        
        Gemini uses:
        - System instruction (separate parameter)
        - Contents list with 'role' and 'parts'
        
        Returns:
            Tuple of (system_instruction, gemini_messages)
        """
        system_instruction = None
        gemini_messages = []
        
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            
            if role == "system":
                # Gemini handles system messages separately
                system_instruction = content
            elif role == "user":
                gemini_messages.append({
                    "role": "user",
                    "parts": [content]
                })
            elif role == "assistant":
                gemini_messages.append({
                    "role": "model",  # Gemini uses "model" instead of "assistant"
                    "parts": [content]
                })
        
        return system_instruction, gemini_messages
    
    async def complete(
        self,
        messages: list[dict],
        model: str = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        **kwargs
    ) -> CompletionResponse:
        """
        Complete a chat conversation using Gemini
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Gemini model identifier (default: gemini-1.5-flash)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)
            **kwargs: Additional Gemini-specific options
        
        Returns:
            CompletionResponse with content, tokens, cost
        """
        model = model or self.default_model
        self.current_model = model
        
        try:
            # Get model instance
            gemini_model = self._get_model(model)
            
            # Convert messages to Gemini format
            system_instruction, gemini_messages = self._convert_messages_to_gemini_format(messages)
            
            # Update model with system instruction if provided
            if system_instruction:
                gemini_model = genai.GenerativeModel(
                    model,
                    system_instruction=system_instruction
                )
            
            # Configure generation parameters
            generation_config = GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Start chat session
            chat = gemini_model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])
            
            # Send last message
            last_message = gemini_messages[-1]["parts"][0] if gemini_messages else "Hello"
            response = await chat.send_message_async(
                last_message,
                generation_config=generation_config
            )
            
            # Extract content
            content = response.text
            
            # Get token usage (Gemini provides this in usage_metadata)
            tokens_in = getattr(response.usage_metadata, 'prompt_token_count', 0)
            tokens_out = getattr(response.usage_metadata, 'candidates_token_count', 0)
            
            # Calculate cost
            cost = self._calculate_cost(
                model,
                tokens_in,
                tokens_out,
                self.PRICING
            )
            
            return CompletionResponse(
                content=content,
                model=model,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost=cost,
                provider=self.name,
                finish_reason=response.candidates[0].finish_reason.name if response.candidates else "stop",
                metadata={
                    "safety_ratings": [
                        {
                            "category": rating.category.name,
                            "probability": rating.probability.name
                        }
                        for rating in response.candidates[0].safety_ratings
                    ] if response.candidates else []
                }
            )
        
        except Exception as e:
            error_msg = str(e).lower()
            
            # Rate limit errors
            if "quota" in error_msg or "rate limit" in error_msg or "429" in error_msg:
                logger.warning(f"Gemini rate limit: {e}")
                raise ProviderRateLimitError(
                    f"Gemini rate limit exceeded: {e}",
                    retry_after=60
                )
            
            # Authentication errors
            elif "api key" in error_msg or "authentication" in error_msg or "401" in error_msg or "403" in error_msg:
                logger.error(f"Gemini auth error: {e}")
                raise ProviderAuthError(f"Invalid Gemini API key: {e}")
            
            # Connection errors
            elif "connection" in error_msg or "network" in error_msg:
                logger.error(f"Gemini connection error: {e}")
                raise ProviderConnectionError(f"Failed to connect to Gemini: {e}")
            
            # Timeout errors
            elif "timeout" in error_msg or "timed out" in error_msg:
                logger.error(f"Gemini timeout: {e}")
                raise ProviderTimeoutError(f"Gemini request timed out: {e}")
            
            # Generic API errors
            else:
                logger.error(f"Gemini API error: {e}")
                raise ProviderAPIError(f"Gemini API error: {e}")
    
    async def stream(
        self,
        messages: list[dict],
        model: str = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream completion tokens from Gemini
        
        Args:
            messages: List of message dicts
            model: Gemini model identifier
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional options
        
        Yields:
            Content tokens as strings
        """
        model = model or self.default_model
        self.current_model = model
        
        try:
            # Get model instance
            gemini_model = self._get_model(model)
            
            # Convert messages to Gemini format
            system_instruction, gemini_messages = self._convert_messages_to_gemini_format(messages)
            
            # Update model with system instruction if provided
            if system_instruction:
                gemini_model = genai.GenerativeModel(
                    model,
                    system_instruction=system_instruction
                )
            
            # Configure generation parameters
            generation_config = GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Start chat session
            chat = gemini_model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])
            
            # Send last message with streaming
            last_message = gemini_messages[-1]["parts"][0] if gemini_messages else "Hello"
            response = await chat.send_message_async(
                last_message,
                generation_config=generation_config,
                stream=True
            )
            
            # Stream response chunks
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
        
        except Exception as e:
            error_msg = str(e).lower()
            
            if "quota" in error_msg or "rate limit" in error_msg:
                raise ProviderRateLimitError(f"Gemini rate limit: {e}")
            elif "api key" in error_msg or "authentication" in error_msg:
                raise ProviderAuthError(f"Invalid Gemini API key: {e}")
            elif "connection" in error_msg or "network" in error_msg:
                raise ProviderConnectionError(f"Connection failed: {e}")
            else:
                raise ProviderAPIError(f"Gemini API error: {e}")
    
    def estimate_cost(self, tokens: int, model: str = None) -> float:
        """
        Estimate cost for given token count
        
        Args:
            tokens: Estimated total tokens (input + output)
            model: Gemini model identifier
        
        Returns:
            Estimated cost in USD
        """
        model = model or self.default_model
        
        if model not in self.PRICING:
            logger.warning(f"Unknown model {model}, using default pricing")
            model = self.default_model
        
        pricing = self.PRICING[model]
        
        # Assume 50/50 split for estimation
        avg_cost_per_1m = (pricing["in"] + pricing["out"]) / 2
        return (tokens / 1_000_000) * avg_cost_per_1m
    
    async def validate_credentials(self) -> bool:
        """
        Validate API credentials by making a minimal API call
        
        Returns:
            True if credentials are valid
        
        Raises:
            ProviderAuthError: Invalid credentials
        """
        try:
            # Make minimal API call to test credentials
            model = self._get_model(self.default_model)
            chat = model.start_chat(history=[])
            response = await chat.send_message_async(
                "test",
                generation_config=GenerationConfig(max_output_tokens=10)
            )
            logger.info("Gemini credentials validated successfully")
            return True
        
        except Exception as e:
            error_msg = str(e).lower()
            
            if "api key" in error_msg or "authentication" in error_msg or "401" in error_msg or "403" in error_msg:
                logger.error(f"Gemini credential validation failed: {e}")
                raise ProviderAuthError(f"Invalid Gemini API key: {e}")
            else:
                logger.warning(f"Gemini validation error (may still be valid): {e}")
                # Non-auth errors don't necessarily mean invalid credentials
                return True
    
    def get_models(self) -> list[ModelInfo]:
        """
        Get available Gemini models
        
        Returns:
            List of ModelInfo objects
        """
        return [
            ModelInfo(
                id="gemini-1.5-flash-8b",
                name="Gemini 1.5 Flash 8B",
                context_length=self.CONTEXT_WINDOWS["gemini-1.5-flash-8b"],
                pricing=self.PRICING["gemini-1.5-flash-8b"],
                capabilities=["chat", "code", "fast"],
                provider=self.name
            ),
            ModelInfo(
                id="gemini-1.5-flash",
                name="Gemini 1.5 Flash",
                context_length=self.CONTEXT_WINDOWS["gemini-1.5-flash"],
                pricing=self.PRICING["gemini-1.5-flash"],
                capabilities=["chat", "code", "vision", "fast"],
                provider=self.name
            ),
            ModelInfo(
                id="gemini-1.5-pro",
                name="Gemini 1.5 Pro",
                context_length=self.CONTEXT_WINDOWS["gemini-1.5-pro"],
                pricing=self.PRICING["gemini-1.5-pro"],
                capabilities=["chat", "code", "vision", "analysis", "reasoning"],
                provider=self.name
            ),
            ModelInfo(
                id="gemini-2.0-flash-exp",
                name="Gemini 2.0 Flash (Experimental)",
                context_length=self.CONTEXT_WINDOWS["gemini-2.0-flash-exp"],
                pricing=self.PRICING["gemini-2.0-flash-exp"],
                capabilities=["chat", "code", "vision", "fast", "multimodal"],
                provider=self.name
            ),
        ]
    
    def supports_streaming(self) -> bool:
        """Gemini supports streaming"""
        return True
    
    def get_default_model(self) -> str:
        """Get default Gemini model"""
        return self.default_model
