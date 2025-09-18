"""
FastAPI main application for crop yield prediction platform.
Provides REST API endpoints for yield prediction and advisory services.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
from typing import Dict, List, Optional
import logging

# Import API modules
from .predict import PredictionService, PredictionRequest, PredictionResponse
from .advisory import AdvisoryEngine
from .translation import TranslationService
from .database import DatabaseManager, get_db
from .models import (
    UserCreate, UserResponse, FarmCreate, FarmResponse,
    FeedbackCreate, FeedbackResponse, MetadataResponse
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
prediction_service = None
advisory_engine = None
translation_service = None
db_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global prediction_service, advisory_engine, translation_service, db_manager
    
    logger.info("Starting up Crop Yield Prediction API...")
    
    # Initialize services
    try:
        # Database
        db_manager = DatabaseManager()
        await db_manager.initialize()
        
        # ML Prediction Service
        model_path = os.getenv('MODEL_PATH', 'models/best_model.json')
        prediction_service = PredictionService(model_path)
        await prediction_service.initialize()
        
        # Advisory Engine
        advisory_engine = AdvisoryEngine()
        
        # Translation Service
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        translation_service = TranslationService(gemini_api_key)
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("Shutting down services...")
    if db_manager:
        await db_manager.close()

# Create FastAPI app
app = FastAPI(
    title="AI-Powered Crop Yield Prediction API",
    description="Predicts crop yields and provides farming advisory in English and Odia",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "prediction": prediction_service is not None,
            "advisory": advisory_engine is not None,
            "translation": translation_service is not None,
            "database": db_manager is not None
        }
    }

# Main prediction endpoint
@app.post("/predict", response_model=PredictionResponse)
async def predict_yield(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """
    Predict crop yield and provide advisory recommendations.
    
    This is the main endpoint that:
    1. Validates input parameters
    2. Fetches external data (weather, soil)
    3. Makes yield prediction using ML model
    4. Generates advisory recommendations
    5. Translates to requested language
    6. Stores prediction in database
    """
    try:
        logger.info(f"Prediction request for {request.district}, {request.crop}")
        
        # Validate coordinates
        if not (-90 <= request.latitude <= 90) or not (-180 <= request.longitude <= 180):
            raise HTTPException(status_code=400, detail="Invalid coordinates")
        
        # Make prediction
        prediction_result = await prediction_service.predict(request)
        
        # Generate advisory
        advisory_result = await advisory_engine.generate_advisory(
            prediction_result, request
        )
        
        # Translate if needed
        if request.language and request.language != 'en':
            advisory_result = await translation_service.translate_advisory(
                advisory_result, request.language
            )
        
        # Combine results
        response = PredictionResponse(
            predicted_yield_t_ha=prediction_result['predicted_yield'],
            predicted_yield_range_t_ha=prediction_result['prediction_interval'],
            confidence_score=prediction_result['confidence'],
            advisory=advisory_result['advisory'],
            top_features=prediction_result['top_features'],
            explainability=prediction_result.get('explainability', {}),
            model_version=prediction_result['model_version'],
            timestamp=prediction_result['timestamp']
        )
        
        # Store prediction in database (background task)
        background_tasks.add_task(
            store_prediction,
            request.dict(),
            response.dict(),
            db
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def store_prediction(request_data: dict, response_data: dict, db):
    """Background task to store prediction in database"""
    try:
        await db_manager.store_prediction(request_data, response_data, db)
    except Exception as e:
        logger.error(f"Failed to store prediction: {e}")

# Translation endpoint
@app.post("/translate")
async def translate_text(
    text: str,
    target_language: str,
    source_language: str = "en"
):
    """Translate text between English and Odia"""
    try:
        if target_language not in ['en', 'or']:
            raise HTTPException(status_code=400, detail="Unsupported language")
        
        translated_text = await translation_service.translate(
            text, source_language, target_language
        )
        
        return {
            "original_text": text,
            "translated_text": translated_text,
            "source_language": source_language,
            "target_language": target_language
        }
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# User management endpoints
@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db = Depends(get_db)):
    """Create a new user"""
    try:
        user_id = await db_manager.create_user(user, db)
        return UserResponse(id=user_id, **user.dict())
    except Exception as e:
        logger.error(f"User creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db = Depends(get_db)):
    """Get user by ID"""
    try:
        user = await db_manager.get_user(user_id, db)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Farm management endpoints
@app.post("/farms", response_model=FarmResponse)
async def create_farm(farm: FarmCreate, db = Depends(get_db)):
    """Create a new farm"""
    try:
        farm_id = await db_manager.create_farm(farm, db)
        return FarmResponse(id=farm_id, **farm.dict())
    except Exception as e:
        logger.error(f"Farm creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/farms/{farm_id}", response_model=FarmResponse)
async def get_farm(farm_id: int, db = Depends(get_db)):
    """Get farm by ID"""
    try:
        farm = await db_manager.get_farm(farm_id, db)
        if not farm:
            raise HTTPException(status_code=404, detail="Farm not found")
        return farm
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get farm error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/farms")
async def get_user_farms(user_id: int, db = Depends(get_db)):
    """Get all farms for a user"""
    try:
        farms = await db_manager.get_user_farms(user_id, db)
        return {"farms": farms}
    except Exception as e:
        logger.error(f"Get user farms error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Feedback endpoints
@app.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackCreate, db = Depends(get_db)):
    """Submit feedback for a prediction"""
    try:
        feedback_id = await db_manager.create_feedback(feedback, db)
        return FeedbackResponse(id=feedback_id, **feedback.dict())
    except Exception as e:
        logger.error(f"Feedback submission error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/predictions/{prediction_id}/feedback")
async def get_prediction_feedback(prediction_id: int, db = Depends(get_db)):
    """Get feedback for a prediction"""
    try:
        feedback = await db_manager.get_prediction_feedback(prediction_id, db)
        return {"feedback": feedback}
    except Exception as e:
        logger.error(f"Get feedback error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics endpoints
@app.get("/analytics/predictions")
async def get_prediction_analytics(
    user_id: Optional[int] = None,
    farm_id: Optional[int] = None,
    days: int = 30,
    db = Depends(get_db)
):
    """Get prediction analytics"""
    try:
        analytics = await db_manager.get_prediction_analytics(
            user_id=user_id, farm_id=farm_id, days=days, db=db
        )
        return analytics
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Model metadata endpoint
@app.get("/metadata", response_model=MetadataResponse)
async def get_metadata():
    """Get model metadata and system information"""
    try:
        metadata = await prediction_service.get_metadata()
        return MetadataResponse(**metadata)
    except Exception as e:
        logger.error(f"Metadata error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Batch prediction endpoint
@app.post("/predict/batch")
async def batch_predict(
    requests: List[PredictionRequest],
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Process multiple predictions in batch"""
    try:
        if len(requests) > 100:  # Limit batch size
            raise HTTPException(status_code=400, detail="Batch size too large (max 100)")
        
        results = []
        for request in requests:
            try:
                # Make prediction
                prediction_result = await prediction_service.predict(request)
                
                # Generate advisory
                advisory_result = await advisory_engine.generate_advisory(
                    prediction_result, request
                )
                
                # Translate if needed
                if request.language and request.language != 'en':
                    advisory_result = await translation_service.translate_advisory(
                        advisory_result, request.language
                    )
                
                response = PredictionResponse(
                    predicted_yield_t_ha=prediction_result['predicted_yield'],
                    predicted_yield_range_t_ha=prediction_result['prediction_interval'],
                    confidence_score=prediction_result['confidence'],
                    advisory=advisory_result['advisory'],
                    top_features=prediction_result['top_features'],
                    explainability=prediction_result.get('explainability', {}),
                    model_version=prediction_result['model_version'],
                    timestamp=prediction_result['timestamp']
                )
                
                results.append({
                    "status": "success",
                    "request_id": getattr(request, 'id', None),
                    "prediction": response.dict()
                })
                
                # Store prediction (background task)
                background_tasks.add_task(
                    store_prediction,
                    request.dict(),
                    response.dict(),
                    db
                )
                
            except Exception as e:
                results.append({
                    "status": "error",
                    "request_id": getattr(request, 'id', None),
                    "error": str(e)
                })
        
        return {
            "total_requests": len(requests),
            "successful": len([r for r in results if r["status"] == "success"]),
            "failed": len([r for r in results if r["status"] == "error"]),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": prediction_service.get_current_timestamp() if prediction_service else None
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": prediction_service.get_current_timestamp() if prediction_service else None
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
