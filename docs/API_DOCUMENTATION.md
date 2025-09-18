# API Documentation - SIH AI Harvesters Platform

## Overview

The SIH AI Harvesters Platform provides a comprehensive REST API for crop yield prediction and agricultural advisory services. The API is built with FastAPI and provides bilingual support (English/Odia) for farmer-friendly interactions.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com/api`

## Authentication

Currently, the API uses simple API key authentication for external integrations. For production deployment, implement JWT-based authentication.

\`\`\`bash
# Include API key in headers (if configured)
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/endpoint
\`\`\`

## Core Endpoints

### 1. Health Check

**GET** `/health`

Check API service health and database connectivity.

**Response:**
\`\`\`json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "database": "connected",
  "services": {
    "mlflow": "connected",
    "external_apis": "available"
  }
}
\`\`\`

### 2. Crop Yield Prediction

**POST** `/predict`

Predict crop yield based on location, crop type, and environmental factors.

**Request Body:**
\`\`\`json
{
  "latitude": 20.508973,
  "longitude": 86.418039,
  "state": "Odisha",
  "district": "Kendrapara",
  "crop": "rice",
  "year": 2024,
  "season": "kharif",
  "farmer_inputs": {
    "area_ha": 0.5,
    "sowing_date": "2024-06-12",
    "fertilizer_N_kg": 60,
    "fertilizer_P_kg": 30,
    "fertilizer_K_kg": 40,
    "irrigation_type": "canal",
    "soil_type": "clay_loam"
  },
  "use_satellite": true,
  "language": "english"
}
\`\`\`

**Response:**
\`\`\`json
{
  "prediction_id": "pred_20240115_001",
  "predicted_yield_t_ha": 3.42,
  "predicted_yield_range_t_ha": [3.1, 3.9],
  "confidence_score": 0.78,
  "model_version": "xgb_v1.0.0",
  "prediction_date": "2024-01-15T10:30:00Z",
  "advisory": {
    "irrigation": {
      "recommendation": "Delay irrigation for 3 days; forecast shows 20mm rain.",
      "priority": "medium",
      "timing": "next_3_days"
    },
    "fertilizer": {
      "recommendation": "Apply 20 kg N/ha now, remaining 40 kg/ha at tillering.",
      "priority": "high",
      "timing": "immediate"
    },
    "pest_control": {
      "recommendation": "Moderate blast risk; inspect leaves weekly.",
      "priority": "medium",
      "timing": "weekly"
    }
  },
  "weather_forecast": {
    "next_7_days": {
      "temperature_avg": 28.5,
      "precipitation_mm": 25.0,
      "humidity_percent": 78
    }
  },
  "top_features": [
    {
      "feature": "precipitation_sum_kharif",
      "value": 450.2,
      "importance": 0.22,
      "description": "Total rainfall during kharif season"
    },
    {
      "feature": "temperature_mean_kharif",
      "value": 28.1,
      "importance": 0.18,
      "description": "Average temperature during kharif season"
    }
  ]
}
\`\`\`

### 3. Translation Service

**POST** `/translate`

Translate text between English and Odia for agricultural content.

**Request Body:**
\`\`\`json
{
  "text": "Apply fertilizer after 3 days of rainfall",
  "source_language": "english",
  "target_language": "odia",
  "context": "agricultural_advisory"
}
\`\`\`

**Response:**
\`\`\`json
{
  "translated_text": "ବର୍ଷା ହେବାର ୩ ଦିନ ପରେ ସାର ପ୍ରୟୋଗ କରନ୍ତୁ",
  "source_language": "english",
  "target_language": "odia",
  "confidence": 0.95,
  "cached": false
}
\`\`\`

### 4. Weather Data

**GET** `/weather`

Get current and forecast weather data for a location.

**Query Parameters:**
- `lat` (float): Latitude
- `lon` (float): Longitude
- `days` (int): Number of forecast days (default: 7)

**Response:**
\`\`\`json
{
  "location": {
    "latitude": 20.508973,
    "longitude": 86.418039,
    "district": "Kendrapara",
    "state": "Odisha"
  },
  "current": {
    "temperature": 29.5,
    "humidity": 75,
    "precipitation": 0,
    "wind_speed": 12.5,
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "forecast": [
    {
      "date": "2024-01-16",
      "temperature_min": 22.0,
      "temperature_max": 32.0,
      "precipitation": 5.2,
      "humidity": 78,
      "wind_speed": 15.0
    }
  ]
}
\`\`\`

### 5. Soil Data

**GET** `/soil`

Get soil characteristics for a specific location.

**Query Parameters:**
- `lat` (float): Latitude
- `lon` (float): Longitude

**Response:**
\`\`\`json
{
  "location": {
    "latitude": 20.508973,
    "longitude": 86.418039
  },
  "soil_properties": {
    "ph": 6.8,
    "organic_carbon_percent": 0.65,
    "nitrogen_mg_kg": 280,
    "phosphorus_mg_kg": 45,
    "potassium_mg_kg": 320,
    "clay_percent": 35,
    "sand_percent": 40,
    "silt_percent": 25,
    "cec_cmol_kg": 18.5
  },
  "soil_type": "clay_loam",
  "fertility_rating": "medium",
  "recommendations": {
    "lime_requirement": "none",
    "organic_matter": "increase",
    "drainage": "good"
  }
}
\`\`\`

### 6. Historical Data

**GET** `/historical`

Get historical crop yield data for analysis and comparison.

**Query Parameters:**
- `district` (string): District name
- `crop` (string): Crop type
- `start_year` (int): Start year
- `end_year` (int): End year

**Response:**
\`\`\`json
{
  "district": "Kendrapara",
  "crop": "rice",
  "period": "2018-2023",
  "data": [
    {
      "year": 2023,
      "yield_t_ha": 3.2,
      "area_ha": 125000,
      "production_t": 400000,
      "season": "kharif"
    }
  ],
  "statistics": {
    "mean_yield": 3.1,
    "std_yield": 0.4,
    "trend": "increasing",
    "growth_rate_percent": 2.5
  }
}
\`\`\`

### 7. User Management

**POST** `/users/register`

Register a new farmer user.

**Request Body:**
\`\`\`json
{
  "name": "Ramesh Kumar",
  "email": "ramesh.kumar@example.com",
  "phone": "+91-9876543210",
  "district": "Kendrapara",
  "state": "Odisha",
  "language_preference": "odia",
  "farm_details": {
    "area_ha": 2.5,
    "crops": ["rice", "wheat"],
    "irrigation_type": "canal"
  }
}
\`\`\`

**Response:**
\`\`\`json
{
  "user_id": "user_001",
  "message": "User registered successfully",
  "verification_required": false
}
\`\`\`

### 8. Feedback Collection

**POST** `/feedback`

Submit actual yield data for model improvement.

**Request Body:**
\`\`\`json
{
  "prediction_id": "pred_20240115_001",
  "actual_yield_t_ha": 3.5,
  "harvest_date": "2024-11-15",
  "farmer_notes": "Good season, followed irrigation advice",
  "satisfaction_rating": 4
}
\`\`\`

## Error Handling

The API uses standard HTTP status codes and provides detailed error messages.

**Error Response Format:**
\`\`\`json
{
  "error": {
    "code": "INVALID_LOCATION",
    "message": "The provided coordinates are outside the supported region",
    "details": {
      "latitude": 20.508973,
      "longitude": 86.418039,
      "supported_region": "Odisha, India"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_20240115_001"
}
\`\`\`

**Common Error Codes:**
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (missing/invalid API key)
- `404` - Not Found (resource doesn't exist)
- `422` - Validation Error (invalid data format)
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error
- `503` - Service Unavailable (external API issues)

## Rate Limiting

- **General API**: 100 requests per minute per IP
- **Prediction Endpoint**: 20 requests per minute per IP
- **Translation Endpoint**: 50 requests per minute per IP

## Data Models

### Prediction Request
\`\`\`python
class PredictionRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    state: str
    district: str
    crop: str
    year: int = Field(..., ge=2020, le=2030)
    season: Optional[str] = "kharif"
    farmer_inputs: Optional[FarmerInputs] = None
    use_satellite: bool = False
    language: str = "english"
\`\`\`

### Farmer Inputs
\`\`\`python
class FarmerInputs(BaseModel):
    area_ha: float = Field(..., gt=0)
    sowing_date: Optional[str] = None
    fertilizer_N_kg: Optional[float] = 0
    fertilizer_P_kg: Optional[float] = 0
    fertilizer_K_kg: Optional[float] = 0
    irrigation_type: Optional[str] = "rainfed"
    soil_type: Optional[str] = None
\`\`\`

## SDK Examples

### Python SDK
\`\`\`python
import requests

class SIHHarvestersAPI:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def predict_yield(self, **kwargs):
        response = requests.post(f"{self.base_url}/predict", json=kwargs)
        return response.json()
    
    def get_weather(self, lat, lon, days=7):
        params = {"lat": lat, "lon": lon, "days": days}
        response = requests.get(f"{self.base_url}/weather", params=params)
        return response.json()

# Usage
api = SIHHarvestersAPI()
result = api.predict_yield(
    latitude=20.508973,
    longitude=86.418039,
    crop="rice",
    year=2024
)
\`\`\`

### JavaScript SDK
\`\`\`javascript
class SIHHarvestersAPI {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async predictYield(data) {
        const response = await fetch(`${this.baseUrl}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    }
    
    async getWeather(lat, lon, days = 7) {
        const params = new URLSearchParams({ lat, lon, days });
        const response = await fetch(`${this.baseUrl}/weather?${params}`);
        return response.json();
    }
}

// Usage
const api = new SIHHarvestersAPI();
const result = await api.predictYield({
    latitude: 20.508973,
    longitude: 86.418039,
    crop: 'rice',
    year: 2024
});
\`\`\`

## Testing

Use the provided test scripts to validate API functionality:

\`\`\`bash
# Run API tests
python tests/test_api.py

# Test specific endpoints
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d @tests/sample_prediction_request.json
\`\`\`

## Support

For API support and questions:
- Documentation: `/docs` (Swagger UI)
- Health Check: `/health`
- Contact: sih-ai-harvesters@example.com
