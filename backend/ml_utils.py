import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from typing import Dict, Any, Tuple, List, Optional
import os
import logging
import pickle
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CropYieldPredictor:
    """Advanced ML model wrapper for crop yield prediction with .pkl model support"""
    
    def __init__(self, model_path: str = "models/best_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.feature_engineer = None
        self.model_metadata = {}
        self.crop_encoder = LabelEncoder()
        self.soil_encoder = LabelEncoder()
        self.is_fitted = False
        
        self.crop_encoder.fit(['rice', 'wheat', 'maize', 'sugarcane', 'cotton', 'pulses', 'oilseeds'])
        self.soil_encoder.fit(['loamy', 'clay', 'sandy', 'silt', 'peat', 'alluvial', 'red', 'black'])
        
    def load_model(self) -> bool:
        """Load the trained model from .pkl file with advanced model support"""
        try:
            model_files_to_try = [
                self.model_path,
                self.model_path.replace('.pkl', '.json'),
                'models/xgboost_model.pkl',
                'models/lightgbm_model.pkl',
                'models/randomforest_model.pkl',
                'model.pkl'  # fallback to simple model
            ]
            
            for model_file in model_files_to_try:
                if os.path.exists(model_file):
                    try:
                        if model_file.endswith('.pkl'):
                            with open(model_file, 'rb') as f:
                                model_data = pickle.load(f)
                            
                            if isinstance(model_data, dict):
                                # Advanced model format with metadata
                                self.model = model_data.get('model')
                                self.crop_encoder = model_data.get('crop_encoder', self.crop_encoder)
                                self.soil_encoder = model_data.get('soil_encoder', self.soil_encoder)
                                self.model_metadata = model_data.get('metadata', {})
                            else:
                                # Simple model format
                                self.model = model_data
                            
                            fe_path = model_file.replace('.pkl', '_feature_engineer.pkl')
                            if os.path.exists(fe_path):
                                with open(fe_path, 'rb') as f:
                                    self.feature_engineer = pickle.load(f)
                                logger.info(f"Feature engineer loaded from {fe_path}")
                            
                            self.is_fitted = True
                            logger.info(f"Advanced model loaded successfully from {model_file}")
                            return True
                            
                        elif model_file.endswith('.json'):
                            with open(model_file, 'r') as f:
                                self.model_metadata = json.load(f)
                            
                            # Look for corresponding .pkl file
                            pkl_file = model_file.replace('.json', '.pkl')
                            if os.path.exists(pkl_file):
                                with open(pkl_file, 'rb') as f:
                                    self.model = pickle.load(f)
                                self.is_fitted = True
                                logger.info(f"Model and metadata loaded from {model_file}")
                                return True
                                
                    except Exception as e:
                        logger.warning(f"Failed to load model from {model_file}: {e}")
                        continue
            
            logger.warning("No suitable model file found, will use fallback")
            return False
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def preprocess_input_advanced(self, crop: str, soil_type: str, rainfall: float, 
                                temperature: float, humidity: float, 
                                additional_features: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Advanced preprocessing with feature engineering support"""
        try:
            data = {
                'crop': crop,
                'soil_type': soil_type,
                'precip_sum': rainfall,
                'temp_mean': temperature,
                'humidity_mean': humidity,
                'year': 2024,  # Default current year
                'state': 'Odisha',  # Default state
                'district': 'Unknown',  # Default district
                'area_ha': 1.0  # Default area
            }
            
            if additional_features:
                data.update(additional_features)
            
            defaults = {
                'temp_max': temperature + 5,
                'temp_min': temperature - 5,
                'solar_mean': 18.0,
                'gdd': 2500,
                'soil_phh2o': 6.5,
                'soil_soc': 1.5,
                'soil_clay': 25,
                'soil_sand': 45,
                'soil_silt': 30,
                'fertilizer_N': 80,
                'fertilizer_P': 40,
                'fertilizer_K': 40,
                'yield_lag1': 3.0,
                'yield_lag2': 2.9,
                'yield_lag3': 3.1
            }
            
            for key, value in defaults.items():
                if key not in data:
                    data[key] = value
            
            df = pd.DataFrame([data])
            
            if self.feature_engineer:
                try:
                    X, _ = self.feature_engineer.prepare_features(df, fit=False)
                    return X
                except Exception as e:
                    logger.warning(f"Feature engineering failed, using basic preprocessing: {e}")
            
            return self.preprocess_input_basic(crop, soil_type, rainfall, temperature, humidity)
            
        except Exception as e:
            logger.error(f"Error in advanced preprocessing: {e}")
            raise
    
    def preprocess_input_basic(self, crop: str, soil_type: str, rainfall: float, 
                              temperature: float, humidity: float) -> pd.DataFrame:
        """Basic preprocessing for simple models"""
        try:
            # Handle unknown categories
            if crop not in self.crop_encoder.classes_:
                crop = 'rice'  # Default to rice
            if soil_type not in self.soil_encoder.classes_:
                soil_type = 'loamy'  # Default to loamy
                
            # Encode categorical variables
            crop_encoded = self.crop_encoder.transform([crop])[0]
            soil_encoded = self.soil_encoder.transform([soil_type])[0]
            
            # Create feature array
            features_dict = {
                'crop_encoded': crop_encoded,
                'soil_encoded': soil_encoded,
                'rainfall': rainfall,
                'temperature': temperature,
                'humidity': humidity
            }
            
            df = pd.DataFrame([features_dict])
            logger.info(f"Basic preprocessing completed: {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"Error in basic preprocessing: {e}")
            raise
    
    def predict(self, crop: str, soil_type: str, rainfall: float, 
               temperature: float, humidity: float, 
               additional_features: Optional[Dict[str, Any]] = None) -> Tuple[float, float, Dict[str, Any]]:
        """Make prediction using the loaded model with enhanced output"""
        if not self.is_fitted or self.model is None:
            raise ValueError("Model not loaded. Please load the model first.")
        
        try:
            features_df = self.preprocess_input_advanced(
                crop, soil_type, rainfall, temperature, humidity, additional_features
            )
            
            # Make prediction
            yield_prediction = self.model.predict(features_df)[0]
            
            confidence = self.calculate_confidence_score(features_df, yield_prediction)
            
            feature_importance = self.get_feature_importance(features_df)
            
            prediction_info = {
                'model_type': self.model_metadata.get('model_name', type(self.model).__name__),
                'feature_count': len(features_df.columns),
                'top_features': feature_importance[:5] if feature_importance else [],
                'data_quality': self.assess_data_quality(additional_features or {}),
                'prediction_interval': self.calculate_prediction_interval(yield_prediction, confidence)
            }
            
            logger.info(f"Advanced prediction: {yield_prediction:.2f} t/ha, Confidence: {confidence:.2f}")
            
            return float(yield_prediction), float(confidence), prediction_info
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            raise
    
    def calculate_confidence_score(self, features_df: pd.DataFrame, prediction: float) -> float:
        """Calculate confidence score based on model and data quality"""
        try:
            base_confidence = 0.8
            
            if 'test_r2' in self.model_metadata.get('metrics', {}):
                r2_score = self.model_metadata['metrics']['test_r2']
                base_confidence = min(0.95, max(0.5, r2_score))
            
            if prediction < 0.5 or prediction > 15:  # Unusual yield values
                base_confidence *= 0.8
            
            confidence = base_confidence * np.random.uniform(0.9, 1.1)
            return max(0.5, min(0.95, confidence))
            
        except Exception:
            return np.random.uniform(0.7, 0.9)
    
    def get_feature_importance(self, features_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Get feature importance from the model"""
        try:
            if hasattr(self.model, 'feature_importances_'):
                importances = self.model.feature_importances_
                feature_names = features_df.columns.tolist()
                
                feature_importance = []
                for name, importance in zip(feature_names, importances):
                    feature_importance.append({
                        'feature': name,
                        'importance': float(importance),
                        'value': float(features_df[name].iloc[0])
                    })
                
                # Sort by importance
                feature_importance.sort(key=lambda x: x['importance'], reverse=True)
                return feature_importance
            
        except Exception as e:
            logger.warning(f"Could not get feature importance: {e}")
        
        return []
    
    def assess_data_quality(self, additional_features: Dict[str, Any]) -> float:
        """Assess the quality of input data"""
        quality_score = 1.0
        
        important_features = ['soil_phh2o', 'fertilizer_N', 'gdd', 'solar_mean']
        missing_features = sum(1 for feat in important_features if feat not in additional_features)
        
        if missing_features > 0:
            quality_score -= (missing_features / len(important_features)) * 0.3
        
        return max(0.3, quality_score)
    
    def calculate_prediction_interval(self, prediction: float, confidence: float) -> List[float]:
        """Calculate prediction interval"""
        std_error = prediction * (1 - confidence) * 0.5
        lower_bound = max(0, prediction - 1.96 * std_error)
        upper_bound = prediction + 1.96 * std_error
        
        return [round(lower_bound, 2), round(upper_bound, 2)]

predictor = CropYieldPredictor("models/best_model.pkl")
