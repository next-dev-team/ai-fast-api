from fastapi import APIRouter, HTTPException
from typing import Union

from ..models import (
    ModelsResponse,
    ModelInfo,
    ProvidersResponse,
    ErrorResponse
)
from ..services.g4f_service import g4f_service
from ..utils.logger import logger


router = APIRouter(prefix="/v1", tags=["Models & Providers"])


@router.get(
    "/models",
    response_model=Union[ModelsResponse, ErrorResponse],
    summary="List models",
    description="Lists the currently available models, and provides basic information about each one such as the owner and availability. Compatible with OpenAI API."
)
async def list_models() -> ModelsResponse:
    """List all available models."""
    try:
        logger.info("Fetching available models")
        models = await g4f_service.get_models()
        
        response = ModelsResponse(data=models)
        logger.info(f"Retrieved {len(models)} models")
        
        return response
    
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve models"
        )


@router.get(
    "/models/{model_id}",
    response_model=Union[ModelInfo, ErrorResponse],
    summary="Retrieve model",
    description="Retrieves a model instance, providing basic information about the model such as the owner and permissioning. Compatible with OpenAI API."
)
async def retrieve_model(model_id: str) -> ModelInfo:
    """Retrieve information about a specific model."""
    try:
        logger.info(f"Fetching model: {model_id}")
        models = await g4f_service.get_models()
        
        # Find the requested model
        for model in models:
            if model.id == model_id:
                logger.info(f"Model found: {model_id}")
                return model
        
        # Model not found
        logger.warning(f"Model not found: {model_id}")
        raise HTTPException(
            status_code=404,
            detail=f"Model '{model_id}' not found"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving model {model_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve model '{model_id}'"
        )


@router.get(
    "/providers",
    response_model=Union[ProvidersResponse, ErrorResponse],
    summary="List providers",
    description="Lists the currently available G4F providers, and provides basic information about each one."
)
async def list_providers() -> ProvidersResponse:
    """List all available G4F providers."""
    try:
        logger.info("Fetching available providers")
        providers = await g4f_service.get_providers()
        
        response = ProvidersResponse(data=providers)
        logger.info(f"Retrieved {len(providers)} providers")
        
        return response
    
    except Exception as e:
        logger.error(f"Error listing providers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve providers"
        )


@router.get(
    "/providers/{provider_id}",
    response_model=Union[dict, ErrorResponse],
    summary="Retrieve provider",
    description="Retrieves detailed information about a specific G4F provider."
)
async def retrieve_provider(provider_id: str) -> dict:
    """Retrieve information about a specific provider."""
    try:
        logger.info(f"Fetching provider: {provider_id}")
        providers = await g4f_service.get_providers()
        
        # Find the requested provider
        for provider in providers:
            if provider.id == provider_id:
                logger.info(f"Provider found: {provider_id}")
                return {
                    "id": provider.id,
                    "url": provider.url,
                    "models": provider.models,
                    "params": provider.params,
                    "object": "provider"
                }
        
        # Provider not found
        logger.warning(f"Provider not found: {provider_id}")
        raise HTTPException(
            status_code=404,
            detail=f"Provider '{provider_id}' not found"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving provider {provider_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve provider '{provider_id}'"
        )