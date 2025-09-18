# Technical Architecture - SIH AI Harvesters Platform

## System Overview

The SIH AI Harvesters Platform is a comprehensive full-stack application designed for crop yield prediction and agricultural advisory services. The architecture follows modern microservices principles with containerized deployment and scalable infrastructure.

## Architecture Diagram

\`\`\`
┌─────────────────────────────────────────────────────────────────┐
│                        Load Balancer (Nginx)                    │
└─────────────────────┬───────────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
┌───────▼────────┐         ┌────────▼────────┐
│   Frontend      │         │   Backend       │
│   (Next.js)     │◄────────┤   (FastAPI)     │
│   Port: 3000    │         │   Port: 8000    │
└─────────────────┘         └─────────┬───────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
            ┌───────▼────────┐ ┌──────▼──────┐ ┌───────▼────────┐
            │   PostgreSQL    │ │   MLflow    │ │     Redis      │
            │   Port: 5432    │ │  Port: 5000 │ │   Port: 6379   │
            └─────────────────┘ └─────────────┘ └────────────────┘
                    │
            ┌───────▼────────┐
            │ External APIs   │
            │ • NASA POWER   │
            │ • SoilGrids    │
            │ • Gemini API   │
            └────────────────┘
\`\`\`

## Technology Stack

### Frontend Layer
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **UI Components**: shadcn/ui
- **State Management**: React Hooks + SWR
- **Maps**: Leaflet.js
- **Charts**: Recharts
- **PWA**: Service Workers for offline capability

### Backend Layer
- **Framework**: FastAPI (Python 3.11)
- **API Documentation**: OpenAPI/Swagger
- **Authentication**: JWT (future implementation)
- **Validation**: Pydantic models
- **Async Support**: asyncio, asyncpg
- **Background Tasks**: Celery (future implementation)

### Machine Learning Stack
- **Training**: XGBoost, LightGBM, scikit-learn
- **Experiment Tracking**: MLflow
- **Feature Engineering**: pandas, numpy
- **Model Serving**: FastAPI integration
- **Model Storage**: MLflow Model Registry

### Database Layer
- **Primary Database**: PostgreSQL 15
- **ML Tracking**: MLflow backend store
- **Caching**: Redis 7
- **Connection Pooling**: asyncpg pool
- **Migrations**: Custom migration system

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Orchestration**: Kubernetes (production)
- **Reverse Proxy**: Nginx
- **SSL/TLS**: Let's Encrypt certificates
- **Monitoring**: Prometheus + Grafana (future)
- **Logging**: Structured JSON logging

## Data Flow Architecture

### 1. Prediction Request Flow
\`\`\`
User Input → Frontend Validation → API Request → Data Enrichment → 
ML Model → Prediction → Advisory Generation → Translation → Response
\`\`\`

### 2. Data Pipeline Flow
\`\`\`
External APIs → Data Fetching → Preprocessing → Feature Engineering → 
Model Training → Model Validation → Model Deployment → MLflow Registry
\`\`\`

### 3. Real-time Data Flow
\`\`\`
Weather APIs → Cache (Redis) → Background Updates → Database → 
Real-time Predictions → WebSocket Updates (future)
\`\`\`

## Component Architecture

### Frontend Components

#### Core Components
\`\`\`typescript
src/
├── app/                    # Next.js App Router
│   ├── page.tsx           # Main prediction interface
│   ├── layout.tsx         # Root layout with providers
│   └── globals.css        # Global styles
├── components/
│   ├── prediction-form.tsx    # Main prediction form
│   ├── prediction-results.tsx # Results display
│   ├── language-toggle.tsx    # Language switcher
│   └── ui/                    # shadcn/ui components
├── hooks/
│   ├── use-translation.ts     # Translation hook
│   ├── use-geolocation.ts     # GPS integration
│   └── use-prediction.ts      # Prediction API calls
└── lib/
    ├── api.ts                 # API client
    ├── utils.ts               # Utility functions
    └── translations.ts        # Translation cache
\`\`\`

#### State Management
- **Local State**: React useState for component state
- **Server State**: SWR for API data caching
- **Global State**: React Context for language preferences
- **Persistent State**: localStorage for user preferences

### Backend Components

#### API Structure
\`\`\`python
src/api/
├── main.py              # FastAPI application
├── models.py            # Pydantic data models
├── predict.py           # Prediction endpoints
├── advisory.py          # Advisory generation
├── translation.py       # Translation services
├── database.py          # Database operations
└── utils.py             # Utility functions
\`\`\`

#### Service Layer
- **Prediction Service**: ML model integration and inference
- **Advisory Service**: Rule-based recommendation engine
- **Translation Service**: Gemini API integration with caching
- **Weather Service**: NASA POWER API integration
- **Soil Service**: SoilGrids API integration

### Database Schema

#### Core Tables
\`\`\`sql
-- User management
users (id, name, email, phone, district_id, language_preference)
farms (id, user_id, name, area_hectares, soil_type, coordinates)

-- Prediction data
predictions (id, user_id, farm_id, crop_type, predicted_yield, confidence)
feedback (id, prediction_id, actual_yield, satisfaction_rating)

-- Reference data
districts (id, name, state, coordinates)
crop_types (id, name, scientific_name, growing_season)
weather_stations (id, name, coordinates, district_id)

-- ML artifacts
ml_artifacts (id, model_name, version, accuracy_score, created_at)
\`\`\`

#### Indexing Strategy
- **Spatial Indexes**: PostGIS for location-based queries
- **Time-series Indexes**: B-tree indexes on date columns
- **Composite Indexes**: Multi-column indexes for common queries
- **Partial Indexes**: Filtered indexes for active records

## Security Architecture

### Authentication & Authorization
- **API Keys**: For external service integration
- **JWT Tokens**: For user session management (future)
- **Role-based Access**: Admin, Farmer, Extension Officer roles
- **Rate Limiting**: Nginx-based request throttling

### Data Security
- **Encryption at Rest**: PostgreSQL encryption
- **Encryption in Transit**: TLS 1.3 for all communications
- **Input Validation**: Pydantic models for API validation
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: Content Security Policy headers

### Infrastructure Security
- **Container Security**: Non-root users, minimal base images
- **Network Security**: Private networks, firewall rules
- **Secrets Management**: Environment variables, Docker secrets
- **Regular Updates**: Automated security patches

## Scalability Design

### Horizontal Scaling
- **Stateless Services**: All services designed to be stateless
- **Load Balancing**: Nginx upstream configuration
- **Database Replication**: Master-slave PostgreSQL setup
- **Caching Strategy**: Redis for frequently accessed data

### Performance Optimization
- **Connection Pooling**: Database connection management
- **Query Optimization**: Indexed queries, query analysis
- **Caching Layers**: Multiple levels of caching
- **CDN Integration**: Static asset delivery (future)

### Monitoring & Observability
- **Health Checks**: Kubernetes liveness/readiness probes
- **Metrics Collection**: Prometheus metrics
- **Log Aggregation**: Centralized logging system
- **Error Tracking**: Sentry integration (future)

## Deployment Architecture

### Development Environment
\`\`\`yaml
# docker-compose.override.yml
services:
  - postgres (development database)
  - mlflow (experiment tracking)
  - fastapi (hot reload enabled)
  - nextjs (development server)
  - redis (caching)
\`\`\`

### Production Environment
\`\`\`yaml
# docker-compose.prod.yml
services:
  - nginx (load balancer, SSL termination)
  - fastapi (multiple replicas)
  - nextjs (optimized build)
  - postgres (production configuration)
  - mlflow (persistent storage)
  - redis (persistent cache)
\`\`\`

### Kubernetes Deployment
- **Namespaces**: Separate environments (dev, staging, prod)
- **Deployments**: Scalable service replicas
- **Services**: Internal service discovery
- **Ingress**: External traffic routing
- **ConfigMaps**: Environment configuration
- **Secrets**: Sensitive data management
- **PersistentVolumes**: Database storage

## API Design Principles

### RESTful Design
- **Resource-based URLs**: `/api/predictions`, `/api/users`
- **HTTP Methods**: GET, POST, PUT, DELETE
- **Status Codes**: Proper HTTP status code usage
- **Content Negotiation**: JSON primary, XML support

### Error Handling
- **Consistent Format**: Standardized error response structure
- **Error Codes**: Application-specific error codes
- **Validation Errors**: Detailed field-level error messages
- **Logging**: Comprehensive error logging

### Versioning Strategy
- **URL Versioning**: `/api/v1/predictions`
- **Backward Compatibility**: Support for previous versions
- **Deprecation Policy**: Gradual phase-out of old versions

## Machine Learning Architecture

### Model Pipeline
\`\`\`python
# Training Pipeline
Data Ingestion → Feature Engineering → Model Training → 
Validation → Hyperparameter Tuning → Model Registration → Deployment
\`\`\`

### Model Serving
- **Model Loading**: Lazy loading of ML models
- **Prediction Caching**: Cache predictions for identical inputs
- **Model Versioning**: A/B testing of model versions
- **Fallback Strategy**: Default predictions if model fails

### Feature Store (Future)
- **Feature Engineering**: Centralized feature computation
- **Feature Serving**: Real-time feature serving
- **Feature Monitoring**: Data drift detection
- **Feature Lineage**: Track feature dependencies

## Integration Architecture

### External APIs
- **NASA POWER**: Weather data integration
- **SoilGrids**: Soil property data
- **Gemini API**: Translation services
- **Satellite APIs**: NDVI data (future)

### Integration Patterns
- **Circuit Breaker**: Fault tolerance for external APIs
- **Retry Logic**: Exponential backoff for failed requests
- **Timeout Handling**: Prevent hanging requests
- **Fallback Data**: Cached data when APIs are unavailable

## Future Enhancements

### Planned Features
- **Real-time Notifications**: WebSocket integration
- **Mobile App**: React Native application
- **IoT Integration**: Sensor data integration
- **Blockchain**: Supply chain traceability
- **AI Chatbot**: Conversational interface

### Scalability Improvements
- **Microservices**: Service decomposition
- **Event-driven Architecture**: Async message processing
- **CQRS**: Command Query Responsibility Segregation
- **GraphQL**: Flexible API queries

---

**Architecture Version**: 1.0.0  
**Last Updated**: January 2024  
**Review Cycle**: Quarterly architecture reviews
