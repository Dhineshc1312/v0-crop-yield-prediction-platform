# Demo Script - SIH AI Harvesters Platform

## Demo Overview

**Duration**: 3-4 minutes  
**Audience**: SIH Judges and Evaluators  
**Objective**: Showcase the complete crop yield prediction and advisory system

## Pre-Demo Setup Checklist

### Technical Setup
- [ ] All services running (docker-compose up)
- [ ] Database seeded with sample data
- [ ] API endpoints tested and responsive
- [ ] Frontend loading correctly
- [ ] Translation service working
- [ ] Sample prediction data ready

### Demo Environment
- [ ] Stable internet connection
- [ ] Browser with location permissions enabled
- [ ] Backup slides ready
- [ ] Screen recording as fallback
- [ ] Mobile device for responsive demo

## Demo Script

### Opening (30 seconds)

**Presenter**: "Good morning! I'm presenting the AI-Powered Crop Yield Prediction Platform by Team AI Harvesters. Our solution addresses the critical challenge of crop yield uncertainty faced by farmers in Odisha."

**Key Points to Mention**:
- Problem: Farmers struggle with unpredictable yields
- Solution: AI-powered predictions with bilingual advisory
- Impact: 10-15% yield improvement potential

### Main Demo Flow (2.5 minutes)

#### 1. Platform Introduction (20 seconds)
**Action**: Open the homepage
**Script**: "Our platform provides farmers with accurate crop yield predictions and personalized advisory in both English and Odia."

**Show**:
- Clean, farmer-friendly interface
- Language toggle (English/Odia)
- Mobile-responsive design

#### 2. Location & Crop Selection (30 seconds)
**Action**: Start a new prediction
**Script**: "Let me demonstrate with a rice farmer from Kendrapara district. The system can auto-detect location using GPS or allow manual entry."

**Show**:
- GPS location detection
- District selection (Kendrapara)
- Crop selection (Rice)
- Season selection (Kharif 2024)

#### 3. Farm Details Input (30 seconds)
**Action**: Fill in farm details
**Script**: "Farmers can provide additional details like farm size, sowing date, and fertilizer usage for more accurate predictions."

**Show**:
- Farm area: 2.5 hectares
- Sowing date: June 15, 2024
- Fertilizer inputs (N-P-K)
- Irrigation type: Canal

#### 4. Prediction Results (45 seconds)
**Action**: Submit prediction and show results
**Script**: "Our XGBoost model, trained on weather, soil, and historical data, predicts a yield of 3.4 tons per hectare with 78% confidence."

**Show**:
- Predicted yield: 3.4 t/ha
- Confidence range: 3.1-3.9 t/ha
- Confidence score: 78%
- Model features importance

#### 5. Advisory Recommendations (45 seconds)
**Action**: Scroll through advisory sections
**Script**: "The system provides actionable recommendations for irrigation, fertilizer application, and pest management based on current weather forecasts."

**Show**:
- **Irrigation**: "Delay irrigation for 3 days; forecast shows 20mm rain"
- **Fertilizer**: "Apply 20 kg N/ha now, remaining at tillering"
- **Pest Control**: "Moderate blast risk; inspect leaves weekly"
- Weather forecast integration

#### 6. Bilingual Support (30 seconds)
**Action**: Toggle to Odia language
**Script**: "A key feature is our bilingual support. All recommendations are automatically translated to Odia using Google's Gemini API."

**Show**:
- Language toggle to Odia
- Real-time translation of advisory
- Agricultural terminology in local language
- User-friendly Odia interface

### Technical Highlights (30 seconds)

**Script**: "Our technical architecture includes:"

**Show** (quickly):
- FastAPI backend with ML model integration
- Next.js frontend with responsive design
- PostgreSQL database with MLflow tracking
- Docker containerization for easy deployment
- Integration with NASA POWER and SoilGrids APIs

### Impact & Results (20 seconds)

**Script**: "Our solution demonstrates significant potential impact:"

**Key Metrics**:
- Model accuracy: 87% (RMSE < 0.5 t/ha)
- Response time: < 2 seconds
- Bilingual support: English + Odia
- Coverage: Odisha districts
- Scalable architecture for pan-India deployment

### Closing (10 seconds)

**Script**: "Thank you! Our AI-powered platform empowers farmers with data-driven decisions, potentially improving yields by 10-15% while being accessible in local languages."

## Backup Demo Scenarios

### Scenario A: Internet Issues
- Use pre-recorded screen capture
- Show static screenshots of key features
- Focus on technical architecture slides

### Scenario B: API Failures
- Use cached prediction results
- Demonstrate frontend functionality
- Explain backend architecture verbally

### Scenario C: Time Constraints
**Priority Features** (90 seconds):
1. Quick prediction demo (30s)
2. Advisory recommendations (30s)
3. Bilingual support (30s)

## Technical Demo Points

### For Technical Judges

#### Architecture Highlights
- **Microservices**: Containerized services with Docker
- **ML Pipeline**: XGBoost with MLflow tracking
- **Real-time APIs**: Weather and soil data integration
- **Scalability**: Kubernetes-ready deployment
- **Security**: JWT authentication, input validation

#### Code Quality
- **Type Safety**: TypeScript frontend, Pydantic backend
- **Testing**: Comprehensive test coverage
- **Documentation**: API docs, user guides
- **Best Practices**: Clean code, SOLID principles

#### Innovation Points
- **Bilingual AI**: Context-aware agricultural translation
- **Feature Engineering**: Weather-soil interaction features
- **Advisory Engine**: Rule-based recommendation system
- **Mobile-first**: Progressive Web App capabilities

## Q&A Preparation

### Expected Questions & Answers

**Q**: "How accurate are your predictions?"
**A**: "Our XGBoost model achieves 87% accuracy with RMSE < 0.5 t/ha on Kendrapara rice data. We use cross-validation and feature importance analysis for reliability."

**Q**: "What data sources do you use?"
**A**: "We integrate NASA POWER for weather data, SoilGrids for soil properties, and historical crop statistics. Real-time weather forecasts enhance advisory accuracy."

**Q**: "How do you handle different crops and regions?"
**A**: "Our modular architecture supports multiple crops. We've demonstrated with rice in Odisha and can extend to other crops and states with additional training data."

**Q**: "What about farmers without smartphones?"
**A**: "Our platform works on basic smartphones and has offline capabilities. We also plan SMS integration and partnership with extension services."

**Q**: "How do you ensure translation quality?"
**A**: "We use Google's Gemini API with agricultural context and maintain a cache of verified translations. Local agricultural experts validate terminology."

### Technical Deep-Dive Questions

**Q**: "Explain your ML model selection process."
**A**: "We compared XGBoost, LightGBM, and Random Forest. XGBoost performed best with 87% accuracy. We use MLflow for experiment tracking and model versioning."

**Q**: "How do you handle missing data?"
**A**: "We implement multiple imputation strategies: weather data interpolation, soil property estimation from nearby locations, and historical averages for missing values."

**Q**: "What's your deployment strategy?"
**A**: "We use Docker containers with Kubernetes orchestration. CI/CD pipeline with automated testing, staging environment, and blue-green deployments for zero downtime."

## Demo Success Metrics

### Engagement Indicators
- [ ] Judges asking follow-up questions
- [ ] Requests for technical details
- [ ] Interest in scalability and deployment
- [ ] Questions about farmer adoption

### Technical Validation
- [ ] All features working smoothly
- [ ] Fast response times (< 2 seconds)
- [ ] Accurate predictions displayed
- [ ] Translation working correctly
- [ ] Mobile responsiveness demonstrated

## Post-Demo Actions

### Immediate Follow-up
- [ ] Share GitHub repository link
- [ ] Provide API documentation
- [ ] Offer live demo access
- [ ] Exchange contact information

### Documentation Handover
- [ ] Technical architecture document
- [ ] User guide and API docs
- [ ] Deployment instructions
- [ ] Demo video recording

---

**Demo Version**: 1.0.0  
**Last Rehearsal**: [Date]  
**Backup Plan**: Screen recording + slides  
**Contact**: sih-ai-harvesters@example.com
