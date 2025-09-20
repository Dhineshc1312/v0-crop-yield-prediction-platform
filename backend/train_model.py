import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_dummy_dataset(n_samples: int = 1000) -> pd.DataFrame:
    """Generate dummy crop yield dataset for training"""
    np.random.seed(42)  # For reproducibility
    
    # Define possible values
    crops = ['rice', 'wheat', 'maize', 'sugarcane', 'cotton']
    soil_types = ['loamy', 'clay', 'sandy', 'silt', 'peat']
    
    # Generate random data
    data = {
        'crop': np.random.choice(crops, n_samples),
        'soil_type': np.random.choice(soil_types, n_samples),
        'rainfall': np.random.uniform(200, 2000, n_samples),  # mm
        'temperature': np.random.uniform(15, 40, n_samples),  # °C
        'humidity': np.random.uniform(30, 90, n_samples),     # %
    }
    
    df = pd.DataFrame(data)
    
    # Generate realistic yield based on features (simplified model)
    # This is a dummy formula - in reality, you'd use real agricultural data
    yield_base = {
        'rice': 4.5, 'wheat': 3.2, 'maize': 5.8, 'sugarcane': 70, 'cotton': 1.8
    }
    
    soil_multiplier = {
        'loamy': 1.2, 'clay': 1.0, 'sandy': 0.8, 'silt': 1.1, 'peat': 0.9
    }
    
    yields = []
    for _, row in df.iterrows():
        base_yield = yield_base[row['crop']]
        soil_mult = soil_multiplier[row['soil_type']]
        
        # Rainfall effect (optimal around 800-1200mm for most crops)
        rainfall_effect = 1.0
        if row['rainfall'] < 400:
            rainfall_effect = 0.6
        elif row['rainfall'] > 1500:
            rainfall_effect = 0.8
        else:
            rainfall_effect = 1.0 + (row['rainfall'] - 800) / 2000
        
        # Temperature effect (optimal around 25-30°C)
        temp_effect = 1.0 - abs(row['temperature'] - 27.5) / 50
        
        # Humidity effect (optimal around 60-70%)
        humidity_effect = 1.0 - abs(row['humidity'] - 65) / 100
        
        # Calculate final yield with some random noise
        final_yield = (base_yield * soil_mult * rainfall_effect * 
                      temp_effect * humidity_effect * np.random.uniform(0.8, 1.2))
        
        yields.append(max(0.1, final_yield))  # Ensure positive yield
    
    df['yield'] = yields
    
    logger.info(f"Generated dataset with {n_samples} samples")
    logger.info(f"Yield statistics: mean={np.mean(yields):.2f}, std={np.std(yields):.2f}")
    
    return df

def train_model():
    """Train the crop yield prediction model"""
    logger.info("Starting model training...")
    
    # Generate dummy dataset
    df = generate_dummy_dataset(1000)
    
    # Prepare features and target
    X = df[['crop', 'soil_type', 'rainfall', 'temperature', 'humidity']].copy()
    y = df['yield'].values
    
    # Encode categorical variables
    crop_encoder = LabelEncoder()
    soil_encoder = LabelEncoder()
    
    X['crop_encoded'] = crop_encoder.fit_transform(X['crop'])
    X['soil_encoded'] = soil_encoder.fit_transform(X['soil_type'])
    
    # Select features for training
    feature_columns = ['crop_encoded', 'soil_encoded', 'rainfall', 'temperature', 'humidity']
    X_encoded = X[feature_columns].values
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_encoded, y, test_size=0.2, random_state=42
    )
    
    # Train model
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    
    logger.info("Training RandomForestRegressor...")
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    logger.info(f"Model performance - MSE: {mse:.2f}, R²: {r2:.2f}")
    
    # Save model and encoders
    model_data = {
        'model': model,
        'crop_encoder': crop_encoder,
        'soil_encoder': soil_encoder,
        'feature_columns': feature_columns,
        'performance': {'mse': mse, 'r2': r2}
    }
    
    joblib.dump(model_data, 'model.pkl')
    logger.info("Model saved to model.pkl")
    
    return model, crop_encoder, soil_encoder

if __name__ == "__main__":
    train_model()
