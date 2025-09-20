from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import PredictionRequest, PredictionResponse
from ml_utils import predictor
import logging
import uvicorn

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Crop Yield Predictor",
    description="FastAPI backend for predicting crop yields using machine learning",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Load the ML model on startup"""
    logger.info("Starting up FastAPI server...")
    
    # Try to load existing model
    if not predictor.load_model():
        logger.info("No existing model found. Training new model...")
        try:
            # Import and run training
            from train_model import train_model
            train_model()
            
            # Load the newly trained model
            if predictor.load_model():
                logger.info("New model trained and loaded successfully")
            else:
                logger.error("Failed to load newly trained model")
        except Exception as e:
            logger.error(f"Error training model: {e}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "AI Crop Yield Predictor API",
        "status": "running",
        "model_loaded": predictor.is_fitted
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "model_loaded": predictor.is_fitted,
        "model_path": predictor.model_path
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict_yield(request: PredictionRequest):
    """
    Predict crop yield based on input parameters
    
    - **crop**: Type of crop (rice, wheat, maize, sugarcane, cotton)
    - **soil_type**: Soil type (loamy, clay, sandy, silt, peat)
    - **rainfall**: Rainfall in mm
    - **temperature**: Temperature in °C
    - **humidity**: Humidity percentage (0-100)
    """
    try:
        logger.info(f"Received prediction request: {request}")
        
        # Check if model is loaded
        if not predictor.is_fitted:
            raise HTTPException(
                status_code=503, 
                detail="ML model not loaded. Please check server logs."
            )
        
        # Make prediction
        yield_estimate, confidence = predictor.predict(
            crop=request.crop,
            soil_type=request.soil_type,
            rainfall=request.rainfall,
            temperature=request.temperature,
            humidity=request.humidity
        )
        
        # Prepare response
        response = PredictionResponse(
            yield_estimate=round(yield_estimate, 2),
            confidence=round(confidence, 2),
            inputs_used={
                "crop": request.crop,
                "soil_type": request.soil_type,
                "rainfall": request.rainfall,
                "temperature": request.temperature,
                "humidity": request.humidity
            }
        )
        
        logger.info(f"Prediction successful: {response}")
        return response
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during prediction")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
