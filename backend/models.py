from pydantic import BaseModel, Field
from typing import Dict, Any

class PredictionRequest(BaseModel):
    """Request model for crop yield prediction"""
    crop: str = Field(..., description="Type of crop (e.g., 'rice', 'wheat', 'maize')")
    soil_type: str = Field(..., description="Soil type (e.g., 'loamy', 'clay', 'sandy')")
    rainfall: float = Field(..., ge=0, description="Rainfall in mm")
    temperature: float = Field(..., ge=-50, le=60, description="Temperature in °C")
    humidity: float = Field(..., ge=0, le=100, description="Humidity in %")

class PredictionResponse(BaseModel):
    """Response model for crop yield prediction"""
    yield_estimate: float = Field(..., description="Predicted yield in tons/hectare")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score (0-1)")
    inputs_used: Dict[str, Any] = Field(..., description="Input parameters used for prediction")
