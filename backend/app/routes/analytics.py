from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import os
import logging
from ..models import User
from ..auth import get_current_user
from ..analytics_providers import get_text_analytics_provider

router = APIRouter()
logger = logging.getLogger("analytics")

class TextAnalyticsRequest(BaseModel):
    text: str = Field(..., example="Analyze this text for sentiment.")
    task: str = Field("summarization", example="summarization")

class GraphAnalyticsRequest(BaseModel):
    data: List[Dict[str, Any]] = Field(..., example=[{"x": 1, "y": 2}])

@router.post("/analytics/text", summary="Text Analytics", response_description="Text analytics result")
async def text_analytics(request: TextAnalyticsRequest, current_user: User = Depends(get_current_user)):
    provider_name = os.getenv("TEXT_ANALYTICS_PROVIDER", "openai").lower()
    api_key = os.getenv("OPENAI_API_KEY", "")
    local_endpoint = os.getenv("LOCAL_LLM_ENDPOINT", "http://localhost:11434/api/generate")
    if provider_name == "local":
        provider = get_text_analytics_provider("local", endpoint=local_endpoint)
    elif provider_name == "openai":
        if not api_key:
            raise HTTPException(status_code=400, detail="API key for openai provider is not configured. Please set OPENAI_API_KEY environment variable.")
        provider = get_text_analytics_provider("openai", api_key=api_key)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider_name}")
    try:
        result = await provider.analyze(request.text, task=request.task)
        return result
    except Exception as e:
        logger.exception("Text analytics failed")
        raise HTTPException(status_code=500, detail=f"Text analytics failed: {str(e)}")

@router.post("/analytics/graph", summary="Graphical Analytics", response_description="Graphical analytics result")
def graph_analytics(request: GraphAnalyticsRequest, current_user: User = Depends(get_current_user)):
    return {"graph": "Graphical analytics result"}