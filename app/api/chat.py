from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Union

from ..models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ErrorResponse
)
from ..services.g4f_service import g4f_service
from ..utils.logger import logger
from ..utils.middleware import create_error_response


router = APIRouter(prefix="/v1", tags=["Chat Completions"])


@router.post(
    "/chat/completions",
    response_model=Union[ChatCompletionResponse, ErrorResponse],
    summary="Create chat completion",
    description="Creates a model response for the given chat conversation. Compatible with OpenAI API."
)
async def create_chat_completion(
    request: ChatCompletionRequest
) -> Union[ChatCompletionResponse, StreamingResponse]:
    """Create a chat completion using G4F."""
    try:
        # Validate request
        if not request.messages:
            raise HTTPException(
                status_code=400,
                detail="Messages cannot be empty"
            )
        
        # Log request details
        logger.info(
            f"Chat completion request: model={request.model}, "
            f"messages={len(request.messages)}, stream={request.stream}, "
            f"provider={request.provider}"
        )
        
        # Handle streaming vs non-streaming
        if request.stream:
            # Return streaming response
            return StreamingResponse(
                g4f_service.create_chat_completion_stream(request),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream"
                }
            )
        else:
            # Return regular response
            response = await g4f_service.create_chat_completion(request)
            logger.info(f"Chat completion successful: {response.id}")
            return response
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error in chat completion: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in chat completion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while processing chat completion"
        )


@router.get(
    "/chat/completions/models",
    summary="List chat models",
    description="List available models for chat completions"
)
async def list_chat_models():
    """List available chat models."""
    try:
        models = await g4f_service.get_models()
        # Filter for chat models (exclude image generation models)
        chat_models = [
            model for model in models 
            if model.id not in ["flux", "dall-e-3", "dall-e-2", "midjourney"]
        ]
        return {
            "object": "list",
            "data": chat_models
        }
    except Exception as e:
        logger.error(f"Error listing chat models: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve chat models"
        )