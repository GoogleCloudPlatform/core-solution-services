from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class ModelDetails(BaseModel):
    """Model for LLM details"""
    name: str
    description: str
    capabilities: List[str]
    date_added: str
    is_multi: Optional[bool] = False

class LLMGetTypesResponse(BaseModel):
    """LLM Get types model"""
    success: Optional[bool] = True
    message: Optional[str] = "Successfully retrieved llm types"
    data: Optional[List[ModelDetails]] = []
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "success": True,
            "message": "Successfully retrieved chat llm types",
            "data": [{
                "name": "VertexAI-Chat",
                "description": "Latest Gemini model optimized for fast responses",
                "capabilities": ["Chat", "Text Generation"],
                "date_added": "2024-03-15",
                "is_multi": True
            }]
        }
    }) 