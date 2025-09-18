# AI-Powered Crop Yield Prediction & Advisory Platform

A comprehensive platform that predicts crop yields using weather, soil, and historical data, providing farmer-friendly bilingual advisory in English and Odia.

## 🎯 Project Goals

- Predict crop yield (tons/ha) using weather, soil & historical production data
- Integrate real-time weather & satellite APIs
- Provide personalized advisory (irrigation, fertilizer, pest control)
- Farmer-friendly web app with GPS-enabled location services
- Bilingual support (English + Odia) with translation layer
- Demonstrate 10-15% yield improvement value proposition

## 🏗️ Architecture

\`\`\`
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js UI    │    │   FastAPI       │    │   PostgreSQL    │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │     MLflow      │              │
         └──────────────►│  (ML Tracking)  │◄─────────────┘
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │  External APIs  │
                        │ • NASA POWER    │
                        │ • SoilGrids     │
                        │ • Gemini API    │
                        └─────────────────┘
\`\`\`

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

### 1. Clone and Setup

\`\`\`bash
git clone <repository-url>
cd sih-ai-harvesters
\`\`\`

### 2. Environment Variables

Create a `.env` file:

\`\`\`env
# API Keys
GEMINI_API_KEY=your_gemini_api_key_here

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/crop_yield_db

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000
\`\`\`

### 3. Run with Docker Compose

\`\`\`bash
# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# API: http://localhost:8000
# MLflow: http://localhost:5000
\`\`\`

### 4. Manual Setup (Development)

\`\`\`bash
# Install Python dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Fetch sample data
python src/fetch_data.py --lat 20.508973 --lon 86.418039 --start 2018 --end 2023 --outdir data/raw

# Preprocess data
python src/preprocess.py --in_dir data/raw --out_file data/processed/dataset_clean.csv

# Train model
python src/train_model.py --in_csv data/processed/dataset_clean.csv --out_model models/xgb_baseline.json

# Start API server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (in another terminal)
cd frontend/nextjs-app
npm install
npm run dev
\`\`\`

## 📊 Data Sources

- **Historical Crop Data**: District-level production and area statistics
- **Weather Data**: NASA POWER API (temperature, precipitation, humidity, solar radiation)
- **Soil Data**: SoilGrids API (pH, organic carbon, texture, nutrients)
- **Remote Sensing**: Optional NDVI from Sentinel-2 (via Google Earth Engine)

## 🤖 ML Pipeline

### Features
- **Weather**: Seasonal aggregates (precipitation sum/mean, temperature stats, GDD)
- **Soil**: pH, organic carbon, clay/sand/silt content, CEC, nitrogen
- **Historical**: Lagged yields, rolling means, trend analysis
- **Remote Sensing**: NDVI statistics (optional)

### Models
- **Baseline**: XGBoost regression with hyperparameter tuning
- **Alternative**: LightGBM, PyTorch LSTM for time series
- **Evaluation**: RMSE, MAE, R², prediction intervals

## 🌐 API Endpoints

### POST /predict
Predict crop yield and get advisory recommendations.

**Request:**
\`\`\`json
{
  "latitude": 20.508973,
  "longitude": 86.418039,
  "state": "Odisha",
  "district": "Kendrapara",
  "crop": "rice",
  "year": 2024,
  "farmer_inputs": {
    "area_ha": 0.5,
    "sowing_date": "2024-06-12",
    "fertilizer_N_kg": 60
  },
  "use_satellite": true
}
\`\`\`

**Response:**
\`\`\`json
{
  "predicted_yield_t_ha": 3.42,
  "predicted_yield_range_t_ha": [3.1, 3.9],
  "confidence_score": 0.78,
  "advisory": {
    "irrigation": "Delay irrigation for 3 days; forecast shows 20mm rain.",
    "fertilizer": "Apply 20 kg N/ha now, remaining 40 kg/ha at tillering.",
    "pest": "Moderate blast risk; inspect leaves weekly."
  },
  "top_features": [
    {"feature": "precip_sum", "value": 450, "importance": 0.22}
  ]
}
\`\`\`

## 🌍 Bilingual Support

- **UI Translation**: English ↔ Odia using Gemini API
- **Advisory Translation**: Real-time translation of recommendations
- **Fallback**: Cached translations for common terms
- **Localization**: Agricultural terminology in local context

## 📱 Frontend Features

- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **GPS Integration**: Automatic location detection
- **Language Toggle**: Seamless English/Odia switching
- **Farmer Dashboard**: Simple input forms and clear results
- **History Tracking**: Past predictions and feedback
- **Offline Support**: Cached translations and core functionality

## 🧪 Testing

\`\`\`bash
# Run data pipeline test
python src/preprocess.py --in_dir data/raw --out_file data/processed/test_dataset.csv

# Run model training test
python src/train_model.py --in_csv data/processed/test_dataset.csv --out_model models/test_model.json

# API smoke test
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"latitude":20.508973,"longitude":86.418039,"crop":"rice","year":2024}'

# Frontend test
npm test  # In frontend/nextjs-app directory
\`\`\`

## 📦 SIH Deliverables

- ✅ **Working Demo**: Deployed application or local Docker setup
- ✅ **Dataset**: `dataset_clean.csv` with processed features
- ✅ **Trained Model**: `xgb_baseline.json` with feature importance
- ✅ **Documentation**: Complete setup and usage instructions
- ✅ **Demo Video**: 2-3 minute demonstration (link in `docs/demo_video_link.txt`)
- ✅ **Presentation**: Slides and poster in `docs/` directory

## 🔧 Development Commands

\`\`\`bash
# Data pipeline
python src/fetch_data.py --help
python src/preprocess.py --help
python src/train_model.py --help

# API development
uvicorn src.api.main:app --reload

# Frontend development
cd frontend/nextjs-app && npm run dev

# Docker operations
docker-compose up --build
docker-compose down
docker-compose logs api
\`\`\`

## 📈 Model Performance

Target metrics for Kendrapara Rice:
- **RMSE**: < 0.5 t/ha
- **MAE**: < 0.4 t/ha
- **R²**: > 0.75
- **Prediction Interval Coverage**: 90%+

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is developed for Smart India Hackathon 2024. See LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the documentation in `docs/`
2. Review common issues in GitHub Issues
3. Contact the development team

---

**Team**: AI Harvesters  
**Event**: Smart India Hackathon 2024  
**Category**: Agriculture & Rural Development
