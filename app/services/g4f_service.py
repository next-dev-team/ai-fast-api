import asyncio
import json
import time
import uuid
from typing import AsyncGenerator, List, Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
import g4f
from g4f.Provider import RetryProvider
try:
    from g4f.Provider import Bing, OpenaiChat, ChatGpt
except ImportError:
    # Try alternative import names
    try:
        from g4f.Provider import bing as Bing, openai as OpenaiChat, chatgpt as ChatGpt
    except ImportError:
        # Fallback to basic providers
        Bing = None
        OpenaiChat = None
        ChatGpt = None

from ..models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionChoice,
    ChatCompletionStreamResponse,
    ChatCompletionStreamChoice,
    ChatMessage,
    MessageRole,
    ImageGenerationRequest,
    ImageGenerationResponse,
    ImageData,
    ModelInfo,
    ProviderInfo,
    ChatCompletionUsage
)
from ..config import settings
from ..utils.logger import logger


class G4FService:
    """Service for handling G4F operations directly."""
    
    def __init__(self):
        self._models_cache: Optional[List[ModelInfo]] = None
        self._providers_cache: Optional[List[ProviderInfo]] = None
        self._cache_timestamp = 0
        self._cache_ttl = 300  # 5 minutes
        self._initialized = False
        # Set up default provider with available providers
        available_providers = [p for p in [Bing, OpenaiChat, ChatGpt] if p is not None]
        if available_providers:
            self._default_provider = RetryProvider(available_providers)
        else:
            self._default_provider = None
    
    async def initialize(self):
        """Initialize the G4F service."""
        try:
            logger.info("Initializing G4F service...")
            # Pre-load models and providers
            await self.get_models()
            await self.get_providers()
            self._initialized = True
            logger.info("G4F service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize G4F service: {str(e)}")
            # Don't raise, just log the error and continue with defaults
            self._initialized = True
    
    async def cleanup(self):
        """Cleanup G4F service resources."""
        try:
            logger.info("Cleaning up G4F service...")
            self._models_cache = None
            self._providers_cache = None
            self._initialized = False
            logger.info("G4F service cleanup completed")
        except Exception as e:
            logger.error(f"Error during G4F service cleanup: {str(e)}")
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if self._cache_timestamp == 0:
            return False
        return time.time() - self._cache_timestamp < self._cache_ttl
    
    @retry(
        stop=stop_after_attempt(settings.g4f_retries),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def create_chat_completion(
        self, 
        request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """Create a chat completion using G4F directly."""
        try:
            logger.info(f"Creating chat completion with model: {request.model}")
            
            # Convert messages to G4F format
            messages = [{
                "role": msg.role,
                "content": msg.content
            } for msg in request.messages]
            
            # Get provider if specified
            provider = self._get_provider(request.provider)
            
            # Create completion using G4F
            response_text = await asyncio.to_thread(
                g4f.ChatCompletion.create,
                model=request.model,
                messages=messages,
                provider=provider,
                stream=False,
                web_search=request.web_search
            )
            
            # Create response in OpenAI format
            completion_id = f"chatcmpl-{uuid.uuid4().hex[:29]}"
            
            return ChatCompletionResponse(
                id=completion_id,
                object="chat.completion",
                created=int(time.time()),
                model=request.model,
                choices=[
                    ChatCompletionChoice(
                        index=0,
                        message=ChatMessage(
                            role=MessageRole.ASSISTANT,
                            content=response_text
                        ),
                        finish_reason="stop"
                    )
                ],
                usage=ChatCompletionUsage(
                    prompt_tokens=0,  # G4F doesn't provide token counts
                    completion_tokens=0,
                    total_tokens=0
                )
            )
            
        except Exception as e:
            logger.error(f"Error in chat completion: {str(e)}")
            raise
    
    async def create_chat_completion_stream(
        self, 
        request: ChatCompletionRequest
    ) -> AsyncGenerator[str, None]:
        """Create a streaming chat completion using G4F directly."""
        try:
            logger.info(f"Creating streaming chat completion with model: {request.model}")
            
            # Convert messages to G4F format
            messages = [{
                "role": msg.role,
                "content": msg.content
            } for msg in request.messages]
            
            # Get provider if specified
            provider = self._get_provider(request.provider)
            
            completion_id = f"chatcmpl-{uuid.uuid4().hex[:29]}"
            
            # Create streaming completion using G4F
            stream = await asyncio.to_thread(
                g4f.ChatCompletion.create,
                model=request.model,
                messages=messages,
                provider=provider,
                stream=True,
                web_search=request.web_search
            )
            
            # Stream the response
            for chunk in stream:
                if chunk:
                    stream_response = ChatCompletionStreamResponse(
                        id=completion_id,
                        object="chat.completion.chunk",
                        created=int(time.time()),
                        model=request.model,
                        choices=[
                            ChatCompletionStreamChoice(
                                index=0,
                                delta=ChatMessage(
                                    role=MessageRole.ASSISTANT,
                                    content=chunk
                                ),
                                finish_reason=None
                            )
                        ]
                    )
                    yield f"data: {stream_response.model_dump_json()}\n\n"
            
            # Send final chunk
            final_response = ChatCompletionStreamResponse(
                id=completion_id,
                object="chat.completion.chunk",
                created=int(time.time()),
                model=request.model,
                choices=[
                    ChatCompletionStreamChoice(
                        index=0,
                        delta=ChatMessage(role=None, content=None),
                        finish_reason="stop"
                    )
                ]
            )
            yield f"data: {final_response.model_dump_json()}\n\n"
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"Error in streaming chat completion: {str(e)}")
            error_response = {
                "error": {
                    "message": str(e),
                    "type": "server_error",
                    "code": "internal_error"
                }
            }
            yield f"data: {json.dumps(error_response)}\n\n"
    
    @retry(
        stop=stop_after_attempt(settings.g4f_retries),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def create_image_generation(
        self, 
        request: ImageGenerationRequest
    ) -> ImageGenerationResponse:
        """Create an image generation using G4F directly."""
        try:
            logger.info(f"Creating image generation with model: {request.model}")
            
            # Get provider if specified
            provider = self._get_provider(request.provider)
            
            # Create image using G4F
            image_url = await asyncio.to_thread(
                g4f.ChatCompletion.create,
                model=request.model,
                messages=[{"role": "user", "content": request.prompt}],
                provider=provider
            )
            
            return ImageGenerationResponse(
                created=int(time.time()),
                data=[
                    ImageData(
                        url=image_url if isinstance(image_url, str) else str(image_url),
                        b64_json=None
                    )
                ]
            )
            
        except Exception as e:
            logger.error(f"Error in image generation: {str(e)}")
            raise
    
    def _get_provider(self, provider_name: Optional[str]):
        """Get G4F provider instance by name."""
        if not provider_name or provider_name.lower() == "auto":
            return self._default_provider
        
        provider_map = {}
        if Bing:
            provider_map["bing"] = Bing
        if OpenaiChat:
            provider_map["openai"] = OpenaiChat
        if ChatGpt:
            provider_map["chatgpt"] = ChatGpt
        
        return provider_map.get(provider_name.lower(), self._default_provider)
    
    async def get_models(self) -> List[ModelInfo]:
        """Get available models from G4F."""
        if self._is_cache_valid() and self._models_cache:
            return self._models_cache
        
        try:
            logger.info("Fetching models from G4F")
            # G4F doesn't have a direct API for models, so we return a static list
            models = self._get_default_models()
            
            self._models_cache = models
            self._cache_timestamp = time.time()
            
            return models
            
        except Exception as e:
            logger.error(f"Error fetching models: {str(e)}")
            return self._get_default_models()
    
    async def get_providers(self) -> List[ProviderInfo]:
        """Get available providers from the G4F API."""
        # This endpoint is not standard in OpenAI, so we might need a custom endpoint
        # or fetch it from a different source. For now, returning a static list.
        if self._is_cache_valid() and self._providers_cache:
            return self._providers_cache
        
        try:
            logger.info("Fetching G4F providers (static list)")
            # In a real scenario, you might have a custom endpoint like /v1/providers
            # For now, we'll keep a static list as the g4f API doesn't expose this.
            providers_list = [
                ProviderInfo(
                    id="OpenAI",
                    url="https://api.openai.com",
                    models=["gpt-3.5-turbo", "gpt-4"],
                    params={"supports_stream": True}
                ),
                ProviderInfo(
                    id="Bing",
                    url="https://www.bing.com",
                    models=["gpt-4"],
                    params={"supports_stream": True}
                ),
                ProviderInfo(
                    id="ChatGPT",
                    url="https://chat.openai.com",
                    models=["gpt-3.5-turbo", "gpt-4"],
                    params={"supports_stream": True}
                )
            ]
            
            self._providers_cache = providers_list
            self._cache_timestamp = time.time()
            
            logger.info(f"Retrieved {len(providers_list)} providers")
            return providers_list
            
        except Exception as e:
            logger.error(f"Error fetching providers: {str(e)}")
            # Return default providers if fetch fails
            return self._get_default_providers()
    
    def _get_default_models(self) -> List[ModelInfo]:
        """Get default models when API fetch fails."""
        return [
            ModelInfo(
                id="gpt-3.5-turbo",
                object="model",
                created=int(time.time()),
                owned_by="g4f"
            ),
            ModelInfo(
                id="gpt-4",
                object="model",
                created=int(time.time()),
                owned_by="g4f"
            )
        ]
    
    def _get_default_providers(self) -> List[ProviderInfo]:
        """Get default providers when API fetch fails."""
        return [
            ProviderInfo(
                id="OpenAI",
                url="https://api.openai.com",
                models=["gpt-3.5-turbo", "gpt-4"],
                params={"supports_stream": True}
            ),
            ProviderInfo(
                id="Bing",
                url="https://www.bing.com",
                models=["gpt-4"],
                params={"supports_stream": True}
            )
        ]
    



# Global service instance
g4f_service = G4FService()