"""
Pydantic models for API request/response schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# User models
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    location_lat: Optional[float] = Field(None, ge=-90, le=90)
    location_lon: Optional[float] = Field(None, ge=-180, le=180)
    preferred_lang: str = Field("en", regex="^(en|or)$")

class UserResponse(BaseModel):
    id: int
    name: str
    phone: Optional[str]
    location_lat: Optional[float]
    location_lon: Optional[float]
    preferred_lang: str
    created_at: Optional[datetime]

# Farm models
class FarmCreate(BaseModel):
    user_id: int
    name: str = Field(..., min_length=1, max_length=255)
    area_ha: float = Field(..., gt=0, le=1000)
    soil_inputs_json: Optional[Dict[str, Any]] = None
    crop_preferences: Optional[List[str]] = None

class FarmResponse(BaseModel):
    id: int
    user_id: int
    name: str
    area_ha: float
    soil_inputs_json: Optional[Dict[str, Any]]
    crop_preferences: Optional[List[str]]
    created_at: Optional[datetime]

# Feedback models
class FeedbackCreate(BaseModel):
    prediction_id: int
    actual_yield_t_ha: float = Field(..., gt=0, le=50)
    comment: Optional[str] = Field(None, max_length=1000)
    rating: Optional[int] = Field(None, ge=1, le=5)

class FeedbackResponse(BaseModel):
    id: int
    prediction_id: int
    actual_yield_t_ha: float
    comment: Optional[str]
    rating: Optional[int]
    timestamp: Optional[datetime]

# Metadata model
class MetadataResponse(BaseModel):
    model_version: str
    training_date: str
    metrics: Dict[str, Any]
    feature_count: int
    supported_crops: List[str]
    supported_languages: List[str]
    api_version: str
