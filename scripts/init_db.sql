-- Initialize database schema for crop yield prediction platform

-- Create database for MLflow if it doesn't exist
CREATE DATABASE IF NOT EXISTS mlflow_db;

-- Use the main crop yield database
\c crop_yield_db;

-- Users table for farmer profiles
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) UNIQUE,
    location_lat DECIMAL(10, 8),
    location_lon DECIMAL(11, 8),
    preferred_lang VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Farms table for farm-specific information
CREATE TABLE IF NOT EXISTS farms (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255),
    area_ha DECIMAL(10, 4),
    soil_inputs_json JSONB,
    crop_preferences TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Predictions table to store all yield predictions
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    farm_id INTEGER REFERENCES farms(id) ON DELETE CASCADE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    input_json JSONB NOT NULL,
    result_json JSONB NOT NULL,
    model_version VARCHAR(50),
    confidence_score DECIMAL(5, 4),
    predicted_yield_t_ha DECIMAL(8, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Feedback table for farmers to provide actual yields
CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    prediction_id INTEGER REFERENCES predictions(id) ON DELETE CASCADE,
    actual_yield_t_ha DECIMAL(8, 4),
    comment TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ML artifacts table for model versioning
CREATE TABLE IF NOT EXISTS ml_artifacts (
    id SERIAL PRIMARY KEY,
    model_version VARCHAR(50) UNIQUE NOT NULL,
    metrics_json JSONB,
    artifact_path VARCHAR(500),
    training_data_hash VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT FALSE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_predictions_farm_id ON predictions(farm_id);
CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions(timestamp);
CREATE INDEX IF NOT EXISTS idx_feedback_prediction_id ON feedback(prediction_id);
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_farms_user_id ON farms(user_id);

-- Insert sample data for testing
INSERT INTO users (name, phone, location_lat, location_lon, preferred_lang) 
VALUES 
    ('Ravi Kumar', '+91-9876543210', 20.508973, 86.418039, 'en'),
    ('Sunita Devi', '+91-9876543211', 20.515000, 86.420000, 'or')
ON CONFLICT (phone) DO NOTHING;

INSERT INTO farms (user_id, name, area_ha, soil_inputs_json, crop_preferences)
VALUES 
    (1, 'Main Rice Field', 2.5, '{"soil_ph": 6.5, "organic_matter": "medium"}', ARRAY['Rice']),
    (2, 'Paddy Field 1', 1.8, '{"soil_ph": 6.8, "organic_matter": "high"}', ARRAY['Rice', 'Wheat'])
ON CONFLICT DO NOTHING;

-- Create a view for easy prediction analytics
CREATE OR REPLACE VIEW prediction_analytics AS
SELECT 
    p.id,
    u.name as farmer_name,
    f.name as farm_name,
    p.predicted_yield_t_ha,
    p.confidence_score,
    p.model_version,
    fb.actual_yield_t_ha,
    fb.rating,
    p.created_at as prediction_date,
    fb.timestamp as feedback_date,
    CASE 
        WHEN fb.actual_yield_t_ha IS NOT NULL 
        THEN ABS(p.predicted_yield_t_ha - fb.actual_yield_t_ha) 
        ELSE NULL 
    END as prediction_error
FROM predictions p
JOIN farms f ON p.farm_id = f.id
JOIN users u ON f.user_id = u.id
LEFT JOIN feedback fb ON p.id = fb.prediction_id;

-- Grant permissions (adjust as needed for production)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
