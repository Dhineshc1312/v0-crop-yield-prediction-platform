# AI Crop Yield Predictor Backend

FastAPI backend for predicting crop yields using machine learning.

## Setup

1. Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

2. Train the model (optional - will auto-train on first run):
\`\`\`bash
python train_model.py
\`\`\`

3. Run the server:
\`\`\`bash
python main.py
\`\`\`

The API will be available at `http://localhost:8000`

## API Documentation

- Interactive docs: `http://localhost:8000/docs`
- OpenAPI schema: `http://localhost:8000/openapi.json`

## Endpoints

- `GET /` - Health check
- `GET /health` - Detailed health check
- `POST /predict` - Crop yield prediction

## Model Details

The current implementation uses a RandomForestRegressor trained on dummy data. To replace with a real model:

1. Replace the dummy data generation in `train_model.py` with real agricultural data
2. Adjust preprocessing in `ml_utils.py` as needed
3. Update the prediction logic if required

## Example Request

\`\`\`json
{
  "crop": "rice",
  "soil_type": "loamy",
  "rainfall": 1200.0,
  "temperature": 28.5,
  "humidity": 75.0
}
\`\`\`

## Example Response

\`\`\`json
{
  "yield_estimate": 4.85,
  "confidence": 0.87,
  "inputs_used": {
    "crop": "rice",
    "soil_type": "loamy",
    "rainfall": 1200.0,
    "temperature": 28.5,
    "humidity": 75.0
  }
}
