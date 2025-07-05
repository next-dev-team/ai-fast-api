from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict, Any
from enum import Enum


class MessageRole(str, Enum):
    """Message roles for chat completions."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"


class ChatMessage(BaseModel):
    """Chat message model."""
    role: MessageRole
    content: str
    name: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    """Chat completion request model."""
    model: str = Field(default="gpt-4o-mini", description="Model to use for completion")
    messages: List[ChatMessage] = Field(description="List of messages")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    top_p: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)
    frequency_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    stop: Optional[Union[str, List[str]]] = None
    stream: bool = Field(default=False, description="Whether to stream responses")
    user: Optional[str] = None
    provider: Optional[str] = Field(default=None, description="G4F provider to use")
    web_search: bool = Field(default=False, description="Enable web search")


class ChatCompletionChoice(BaseModel):
    """Chat completion choice model."""
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None


class ChatCompletionUsage(BaseModel):
    """Token usage information."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    """Chat completion response model."""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Optional[ChatCompletionUsage] = None
    system_fingerprint: Optional[str] = None


class ChatCompletionStreamChoice(BaseModel):
    """Streaming chat completion choice."""
    index: int
    delta: Dict[str, Any]
    finish_reason: Optional[str] = None


class ChatCompletionStreamResponse(BaseModel):
    """Streaming chat completion response."""
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[ChatCompletionStreamChoice]
    system_fingerprint: Optional[str] = None


class ImageGenerationRequest(BaseModel):
    """Image generation request model."""
    prompt: str = Field(description="Text description of the desired image")
    model: str = Field(default="flux", description="Model to use for image generation")
    n: int = Field(default=1, ge=1, le=10, description="Number of images to generate")
    size: str = Field(default="1024x1024", description="Size of the generated images")
    quality: str = Field(default="standard", description="Quality of the generated images")
    response_format: str = Field(default="url", description="Format of the response (url or b64_json)")
    style: Optional[str] = Field(default=None, description="Style of the generated images")
    user: Optional[str] = None
    provider: Optional[str] = Field(default=None, description="G4F provider to use")


class ImageData(BaseModel):
    """Image data model."""
    url: Optional[str] = None
    b64_json: Optional[str] = None
    revised_prompt: Optional[str] = None


class ImageGenerationResponse(BaseModel):
    """Image generation response model."""
    created: int
    data: List[ImageData]


class ModelInfo(BaseModel):
    """Model information."""
    id: str
    object: str = "model"
    created: int
    owned_by: str
    permission: List[Dict[str, Any]] = []
    root: Optional[str] = None
    parent: Optional[str] = None


class ModelsResponse(BaseModel):
    """Models list response."""
    object: str = "list"
    data: List[ModelInfo]


class ProviderInfo(BaseModel):
    """Provider information."""
    id: str
    url: Optional[str] = None
    models: List[str] = []
    params: Dict[str, Any] = {}


class ProvidersResponse(BaseModel):
    """Providers list response."""
    object: str = "list"
    data: List[ProviderInfo]


class ErrorResponse(BaseModel):
    """Error response model."""
    error: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: int