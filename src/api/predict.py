"""
Prediction service for crop yield prediction.
Handles ML model loading, feature preparation, and yield prediction.
"""

import pandas as pd
import numpy as np
import json
import pickle
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging
import asyncio
import aiohttp
from pydantic import BaseModel, Field

# Import custom modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from features import FeatureEngineer
from fetch_data import DataFetcher
from utils import (
    validate_coordinates, validate_crop_input, validate_year,
    calculate_confidence_score, create_prediction_intervals
)

logger = logging.getLogger(__name__)

class FarmerInputs(BaseModel):
    """Farmer input data model"""
    area_ha: Optional[float] = Field(None, ge=0.1, le=1000, description="Farm area in hectares")
    sowing_date: Optional[str] = Field(None, description="Sowing date (YYYY-MM-DD)")
    fertilizer_N_kg: Optional[float] = Field(None, ge=0, le=500, description="Nitrogen fertilizer in kg/ha")
    fertilizer_P_kg: Optional[float] = Field(None, ge=0, le=200, description="Phosphorus fertilizer in kg/ha")
    fertilizer_K_kg: Optional[float] = Field(None, ge=0, le=200, description="Potassium fertilizer in kg/ha")
    irrigation_events: Optional[int] = Field(None, ge=0, le=50, description="Number of irrigation events")
    cultivar: Optional[str] = Field(None, description="Crop variety/cultivar")

class PredictionRequest(BaseModel):
    """Prediction request model"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    state: str = Field(..., description="State name")
    district: str = Field(..., description="District name")
    crop: str = Field(..., description="Crop type")
    year: int = Field(..., ge=2000, le=2030, description="Prediction year")
    farmer_inputs: Optional[FarmerInputs] = Field(None, description="Optional farmer inputs")
    use_satellite: bool = Field(False, description="Use satellite data if available")
    language: Optional[str] = Field("en", description="Response language (en/or)")

class FeatureImportance(BaseModel):
    """Feature importance model"""
    feature: str
    value: float
    importance: float

class PredictionResponse(BaseModel):
    """Prediction response model"""
    predicted_yield_t_ha: float = Field(..., description="Predicted yield in tons per hectare")
    predicted_yield_range_t_ha: List[float] = Field(..., description="Prediction interval [lower, upper]")
    confidence_score: float = Field(..., ge=0, le=1, description="Prediction confidence score")
    advisory: Dict[str, str] = Field(..., description="Advisory recommendations")
    top_features: List[FeatureImportance] = Field(..., description="Top contributing features")
    explainability: Dict[str, Any] = Field(default_factory=dict, description="Model explainability data")
    model_version: str = Field(..., description="Model version used")
    timestamp: str = Field(..., description="Prediction timestamp")

class PredictionService:
    """Main prediction service class"""
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self.feature_engineer = None
        self.model_metadata = {}
        self.data_fetcher = DataFetcher()
        
    async def initialize(self):
        """Initialize the prediction service"""
        logger.info("Initializing prediction service...")
        
        try:
            # Load model
            await self.load_model()
            
            # Load feature engineer
            await self.load_feature_engineer()
            
            logger.info("Prediction service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize prediction service: {e}")
            raise
    
    async def load_model(self):
        """Load the trained ML model"""
        try:
            # Load model metadata
            metadata_path = self.model_path
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    self.model_metadata = json.load(f)
            
            # Load actual model
            model_file = None
            if os.path.exists(self.model_path.replace('.json', '.pkl')):
                model_file = self.model_path.replace('.json', '.pkl')
            elif os.path.exists(self.model_path.replace('.json', '.xgb')):
                model_file = self.model_path.replace('.json', '.xgb')
            
            if model_file:
                if model_file.endswith('.pkl'):
                    with open(model_file, 'rb') as f:
                        self.model = pickle.load(f)
                elif model_file.endswith('.xgb'):
                    import xgboost as xgb
                    self.model = xgb.XGBRegressor()
                    self.model.load_model(model_file)
                
                logger.info(f"Model loaded from {model_file}")
            else:
                raise FileNotFoundError(f"Model file not found for {self.model_path}")
                
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    async def load_feature_engineer(self):
        """Load the feature engineer"""
        try:
            fe_path = self.model_path.replace('.json', '_feature_engineer.pkl')
            if os.path.exists(fe_path):
                with open(fe_path, 'rb') as f:
                    self.feature_engineer = pickle.load(f)
                logger.info("Feature engineer loaded")
            else:
                # Create new feature engineer if not found
                self.feature_engineer = FeatureEngineer()
                logger.warning("Feature engineer not found, created new instance")
                
        except Exception as e:
            logger.error(f"Failed to load feature engineer: {e}")
            self.feature_engineer = FeatureEngineer()
    
    async def fetch_external_data(self, request: PredictionRequest) -> Dict[str, Any]:
        """Fetch weather and soil data from external APIs"""
        try:
            # Fetch weather data
            weather_data = {}
            try:
                weather_response = self.data_fetcher.fetch_weather_data(
                    request.latitude, request.longitude, 
                    request.year - 1, request.year
                )
                if weather_response:
                    weather_data = self.data_fetcher.process_weather_data(
                        weather_response, request.year
                    )
            except Exception as e:
                logger.warning(f"Failed to fetch weather data: {e}")
            
            # Fetch soil data
            soil_data = {}
            try:
                soil_response = self.data_fetcher.fetch_soil_data(
                    request.latitude, request.longitude
                )
                if soil_response:
                    soil_data = self.data_fetcher.process_soil_data(soil_response)
            except Exception as e:
                logger.warning(f"Failed to fetch soil data: {e}")
            
            return {
                'weather': weather_data,
                'soil': soil_data
            }
            
        except Exception as e:
            logger.error(f"Error fetching external data: {e}")
            return {'weather': {}, 'soil': {}}
    
    def create_input_dataframe(self, request: PredictionRequest, 
                              external_data: Dict[str, Any]) -> pd.DataFrame:
        """Create input dataframe for prediction"""
        # Base data
        data = {
            'year': request.year,
            'state': request.state,
            'district': request.district,
            'crop': request.crop,
            'area_ha': 1.0,  # Default area
            'production_tonnes': 0,  # Placeholder
        }
        
        # Add weather data
        data.update(external_data.get('weather', {}))
        
        # Add soil data
        data.update(external_data.get('soil', {}))
        
        # Add farmer inputs if provided
        if request.farmer_inputs:
            farmer_data = request.farmer_inputs.dict(exclude_none=True)
            
            # Map farmer inputs to feature names
            if 'area_ha' in farmer_data:
                data['area_ha'] = farmer_data['area_ha']
            if 'fertilizer_N_kg' in farmer_data:
                data['fertilizer_N'] = farmer_data['fertilizer_N_kg']
            if 'fertilizer_P_kg' in farmer_data:
                data['fertilizer_P'] = farmer_data['fertilizer_P_kg']
            if 'fertilizer_K_kg' in farmer_data:
                data['fertilizer_K'] = farmer_data['fertilizer_K_kg']
            if 'irrigation_events' in farmer_data:
                data['irrigation_freq'] = farmer_data['irrigation_events']
        
        # Create DataFrame
        df = pd.DataFrame([data])
        
        return df
    
    def add_default_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add default values for missing features"""
        # Default weather values (if not fetched)
        weather_defaults = {
            'precip_sum': 800,  # mm
            'precip_mean': 4.5,  # mm/day
            'temp_mean': 26,  # °C
            'temp_max': 32,  # °C
            'temp_min': 20,  # °C
            'humidity_mean': 75,  # %
            'solar_mean': 18,  # MJ/m²/day
            'gdd': 2500  # Growing degree days
        }
        
        # Default soil values (if not fetched)
        soil_defaults = {
            'soil_phh2o': 6.5,
            'soil_soc': 1.5,  # %
            'soil_clay': 25,  # %
            'soil_sand': 45,  # %
            'soil_silt': 30,  # %
            'soil_cec': 15,  # cmol/kg
            'soil_nitrogen': 0.15  # %
        }
        
        # Add missing weather features
        for feature, default_value in weather_defaults.items():
            if feature not in df.columns:
                df[feature] = default_value
        
        # Add missing soil features
        for feature, default_value in soil_defaults.items():
            if feature not in df.columns:
                df[feature] = default_value
        
        # Add lag features (use historical averages for the region)
        lag_defaults = {
            'yield_lag1': 3.0,  # t/ha
            'yield_lag2': 2.9,  # t/ha
            'yield_lag3': 3.1,  # t/ha
            'yield_lag3_mean': 3.0,  # t/ha
            'yield_trend': 0.05  # t/ha/year
        }
        
        for feature, default_value in lag_defaults.items():
            if feature not in df.columns:
                df[feature] = default_value
        
        return df
    
    async def predict(self, request: PredictionRequest) -> Dict[str, Any]:
        """Make yield prediction"""
        try:
            logger.info(f"Making prediction for {request.district}, {request.crop}, {request.year}")
            
            # Validate inputs
            if not validate_coordinates(request.latitude, request.longitude):
                raise ValueError("Invalid coordinates")
            
            if not validate_crop_input(request.crop):
                logger.warning(f"Unusual crop type: {request.crop}")
            
            if not validate_year(request.year):
                raise ValueError("Invalid year")
            
            # Fetch external data
            external_data = await self.fetch_external_data(request)
            
            # Create input dataframe
            input_df = self.create_input_dataframe(request, external_data)
            
            # Add default features for missing data
            input_df = self.add_default_features(input_df)
            
            # Prepare features using feature engineer
            X, _ = self.feature_engineer.prepare_features(
                input_df, fit=False, feature_selection=False
            )
            
            # Make prediction
            prediction = self.model.predict(X)[0]
            
            # Calculate prediction interval
            # Simple approach using model uncertainty
            prediction_std = 0.3  # Default uncertainty
            if hasattr(self.model, 'predict') and hasattr(self.model, 'feature_importances_'):
                # For tree-based models, use feature importance as uncertainty proxy
                feature_importance_sum = np.sum(self.model.feature_importances_)
                prediction_std = max(0.2, 1.0 - feature_importance_sum)
            
            prediction_interval = [
                max(0, prediction - 1.96 * prediction_std),
                prediction + 1.96 * prediction_std
            ]
            
            # Calculate confidence score
            data_quality = self.assess_data_quality(external_data)
            confidence = calculate_confidence_score(prediction, prediction_std, data_quality)
            
            # Get feature importance
            top_features = self.get_top_features(X)
            
            # Prepare response
            result = {
                'predicted_yield': round(prediction, 2),
                'prediction_interval': [round(x, 2) for x in prediction_interval],
                'confidence': round(confidence, 3),
                'top_features': top_features,
                'model_version': self.model_metadata.get('model_name', 'unknown'),
                'timestamp': self.get_current_timestamp(),
                'data_quality': data_quality
            }
            
            logger.info(f"Prediction completed: {result['predicted_yield']} t/ha")
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise
    
    def assess_data_quality(self, external_data: Dict[str, Any]) -> float:
        """Assess quality of input data"""
        quality_score = 1.0
        
        # Check weather data availability
        weather_data = external_data.get('weather', {})
        if not weather_data:
            quality_score -= 0.3
        else:
            # Check for key weather parameters
            key_params = ['precip_sum', 'temp_mean', 'gdd']
            missing_params = sum(1 for param in key_params if param not in weather_data)
            quality_score -= (missing_params / len(key_params)) * 0.2
        
        # Check soil data availability
        soil_data = external_data.get('soil', {})
        if not soil_data:
            quality_score -= 0.2
        else:
            # Check for key soil parameters
            key_params = ['soil_phh2o', 'soil_soc', 'soil_clay']
            missing_params = sum(1 for param in key_params if param not in soil_data)
            quality_score -= (missing_params / len(key_params)) * 0.1
        
        return max(0.1, quality_score)
    
    def get_top_features(self, X: pd.DataFrame, top_k: int = 5) -> List[Dict[str, Any]]:
        """Get top contributing features"""
        try:
            if hasattr(self.model, 'feature_importances_'):
                importances = self.model.feature_importances_
                feature_names = X.columns.tolist()
                
                # Create feature importance pairs
                feature_importance_pairs = list(zip(feature_names, importances))
                
                # Sort by importance
                feature_importance_pairs.sort(key=lambda x: x[1], reverse=True)
                
                # Get top features with their values
                top_features = []
                for i, (feature_name, importance) in enumerate(feature_importance_pairs[:top_k]):
                    if feature_name in X.columns:
                        feature_value = X[feature_name].iloc[0]
                        top_features.append({
                            'feature': feature_name,
                            'value': round(float(feature_value), 3),
                            'importance': round(float(importance), 4)
                        })
                
                return top_features
            else:
                # For models without feature importance, return top features by value
                return [
                    {
                        'feature': col,
                        'value': round(float(X[col].iloc[0]), 3),
                        'importance': 0.1
                    }
                    for col in X.columns[:top_k]
                ]
                
        except Exception as e:
            logger.warning(f"Failed to get feature importance: {e}")
            return []
    
    async def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata"""
        return {
            'model_version': self.model_metadata.get('model_name', 'unknown'),
            'training_date': self.model_metadata.get('training_date', 'unknown'),
            'metrics': self.model_metadata.get('metrics', {}),
            'feature_count': len(self.model_metadata.get('feature_names', [])),
            'supported_crops': ['rice', 'wheat', 'maize'],
            'supported_languages': ['en', 'or'],
            'api_version': '1.0.0'
        }
    
    def get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.now().isoformat()
