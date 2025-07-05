from fastapi import APIRouter, HTTPException
from typing import Union

from ..models import (
    ImageGenerationRequest,
    ImageGenerationResponse,
    ErrorResponse
)
from ..services.g4f_service import g4f_service
from ..utils.logger import logger


router = APIRouter(prefix="/v1", tags=["Images"])


@router.post(
    "/images/generate",
    response_model=Union[ImageGenerationResponse, ErrorResponse],
    summary="Generate images",
    description="Creates an image given a text prompt. Compatible with OpenAI API."
)
async def create_image_generation(
    request: ImageGenerationRequest
) -> ImageGenerationResponse:
    """Generate images using G4F."""
    try:
        # Validate request
        if not request.prompt or not request.prompt.strip():
            raise HTTPException(
                status_code=400,
                detail="Prompt cannot be empty"
            )
        
        # Validate response format
        if request.response_format not in ["url", "b64_json"]:
            raise HTTPException(
                status_code=400,
                detail="Response format must be 'url' or 'b64_json'"
            )
        
        # Validate size format
        valid_sizes = [
            "256x256", "512x512", "1024x1024", 
            "1792x1024", "1024x1792"
        ]
        if request.size not in valid_sizes:
            logger.warning(f"Non-standard size requested: {request.size}")
        
        # Log request details
        logger.info(
            f"Image generation request: model={request.model}, "
            f"prompt='{request.prompt[:50]}...', "
            f"size={request.size}, format={request.response_format}, "
            f"provider={request.provider}"
        )
        
        # Generate image
        response = await g4f_service.create_image_generation(request)
        
        logger.info(
            f"Image generation successful: {len(response.data)} image(s) generated"
        )
        
        return response
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error in image generation: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in image generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while generating image"
        )


@router.get(
    "/images/models",
    summary="List image models",
    description="List available models for image generation"
)
async def list_image_models():
    """List available image generation models."""
    try:
        models = await g4f_service.get_models()
        # Filter for image generation models
        image_models = [
            model for model in models 
            if model.id in ["flux", "dall-e-3", "dall-e-2", "midjourney", "stable-diffusion"]
        ]
        
        # Add default image models if none found
        if not image_models:
            from ..models import ModelInfo
            import time
            
            default_image_models = ["flux", "dall-e-3", "dall-e-2"]
            created = int(time.time())
            
            image_models = [
                ModelInfo(
                    id=model_name,
                    created=created,
                    owned_by="g4f"
                )
                for model_name in default_image_models
            ]
        
        return {
            "object": "list",
            "data": image_models
        }
    except Exception as e:
        logger.error(f"Error listing image models: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve image models"
        )