-- Seed data for SIH AI Harvesters Platform
-- This script populates the database with sample data for testing and demo

-- Insert sample districts and crops data
INSERT INTO districts (name, state, latitude, longitude) VALUES
('Kendrapara', 'Odisha', 20.5014, 86.4222),
('Cuttack', 'Odisha', 20.4625, 85.8828),
('Puri', 'Odisha', 19.8135, 85.8312),
('Khordha', 'Odisha', 20.1809, 85.6094),
('Jagatsinghpur', 'Odisha', 20.2543, 86.1711)
ON CONFLICT (name, state) DO NOTHING;

-- Insert sample crop types
INSERT INTO crop_types (name, scientific_name, growing_season, typical_yield_per_hectare) VALUES
('Rice', 'Oryza sativa', 'Kharif', 2500.0),
('Wheat', 'Triticum aestivum', 'Rabi', 3000.0),
('Maize', 'Zea mays', 'Kharif', 4000.0),
('Sugarcane', 'Saccharum officinarum', 'Annual', 70000.0),
('Cotton', 'Gossypium', 'Kharif', 500.0)
ON CONFLICT (name) DO NOTHING;

-- Insert sample users (farmers)
INSERT INTO users (name, email, phone, district_id, language_preference, created_at) VALUES
('Ramesh Kumar', 'ramesh.kumar@example.com', '+91-9876543210', 1, 'odia', NOW()),
('Sunita Patel', 'sunita.patel@example.com', '+91-9876543211', 1, 'english', NOW()),
('Prakash Jena', 'prakash.jena@example.com', '+91-9876543212', 2, 'odia', NOW()),
('Meera Singh', 'meera.singh@example.com', '+91-9876543213', 3, 'english', NOW()),
('Bijay Mohanty', 'bijay.mohanty@example.com', '+91-9876543214', 1, 'odia', NOW())
ON CONFLICT (email) DO NOTHING;

-- Insert sample farms
INSERT INTO farms (user_id, name, area_hectares, soil_type, irrigation_type, latitude, longitude, created_at) VALUES
(1, 'Kumar Rice Farm', 2.5, 'Clay Loam', 'Canal', 20.5100, 86.4300, NOW()),
(2, 'Patel Organic Farm', 1.8, 'Sandy Loam', 'Tube Well', 20.5200, 86.4400, NOW()),
(3, 'Jena Multi-Crop Farm', 3.2, 'Alluvial', 'River', 20.4700, 85.8900, NOW()),
(4, 'Singh Sustainable Farm', 2.0, 'Red Soil', 'Drip', 19.8200, 85.8400, NOW()),
(5, 'Mohanty Traditional Farm', 4.1, 'Clay', 'Flood', 20.5300, 86.4500, NOW());

-- Insert sample historical yield data
INSERT INTO historical_yields (farm_id, crop_type_id, year, season, yield_kg_per_hectare, rainfall_mm, temperature_avg, created_at) VALUES
(1, 1, 2023, 'Kharif', 2800, 1200, 28.5, NOW()),
(1, 1, 2022, 'Kharif', 2650, 1150, 29.2, NOW()),
(1, 1, 2021, 'Kharif', 2900, 1300, 27.8, NOW()),
(2, 1, 2023, 'Kharif', 2400, 1180, 28.8, NOW()),
(2, 1, 2022, 'Kharif', 2550, 1220, 28.1, NOW()),
(3, 1, 2023, 'Kharif', 3100, 1350, 27.5, NOW()),
(3, 2, 2023, 'Rabi', 3200, 200, 22.3, NOW()),
(4, 1, 2023, 'Kharif', 2750, 1100, 29.5, NOW()),
(5, 1, 2023, 'Kharif', 2950, 1400, 27.2, NOW());

-- Insert sample weather stations
INSERT INTO weather_stations (name, latitude, longitude, district_id, is_active) VALUES
('Kendrapara AWS', 20.5014, 86.4222, 1, true),
('Cuttack Met Station', 20.4625, 85.8828, 2, true),
('Puri Coastal Station', 19.8135, 85.8312, 3, true),
('Khordha Regional Station', 20.1809, 85.6094, 4, true),
('Jagatsinghpur Station', 20.2543, 86.1711, 5, true);

-- Insert sample soil test data
INSERT INTO soil_tests (farm_id, ph_level, organic_carbon, nitrogen, phosphorus, potassium, test_date, created_at) VALUES
(1, 6.8, 0.65, 280, 45, 320, '2024-01-15', NOW()),
(2, 7.2, 0.72, 310, 52, 285, '2024-01-20', NOW()),
(3, 6.5, 0.58, 265, 38, 295, '2024-01-25', NOW()),
(4, 7.0, 0.68, 295, 48, 310, '2024-02-01', NOW()),
(5, 6.9, 0.61, 275, 42, 305, '2024-02-05', NOW());

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_historical_yields_farm_crop ON historical_yields(farm_id, crop_type_id);
CREATE INDEX IF NOT EXISTS idx_historical_yields_year ON historical_yields(year, season);
CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions(created_at);
CREATE INDEX IF NOT EXISTS idx_farms_location ON farms(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_users_district ON users(district_id);

-- Insert sample ML model metadata
INSERT INTO ml_artifacts (model_name, version, algorithm, accuracy_score, created_at, is_active) VALUES
('rice_yield_predictor', '1.0.0', 'XGBoost', 0.87, NOW(), true),
('multi_crop_predictor', '1.0.0', 'LightGBM', 0.84, NOW(), false),
('weather_yield_model', '1.0.0', 'Random Forest', 0.82, NOW(), false);

COMMIT;
