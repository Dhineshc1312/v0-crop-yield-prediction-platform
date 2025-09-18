"""
Utility functions for the crop yield prediction platform.
"""

import pandas as pd
import numpy as np
import json
import os
from typing import Dict, List, Any, Optional, Tuple
import hashlib
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration"""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('crop_yield_prediction.log'),
            logging.StreamHandler()
        ]
    )

def calculate_data_hash(data: pd.DataFrame) -> str:
    """Calculate hash of dataset for versioning"""
    # Convert dataframe to string and hash it
    data_string = data.to_string()
    return hashlib.sha256(data_string.encode()).hexdigest()

def validate_coordinates(lat: float, lon: float) -> bool:
    """Validate latitude and longitude coordinates"""
    if not (-90 <= lat <= 90):
        return False
    if not (-180 <= lon <= 180):
        return False
    return True

def validate_crop_input(crop: str, valid_crops: List[str] = None) -> bool:
    """Validate crop input"""
    if valid_crops is None:
        valid_crops = ['rice', 'wheat', 'maize', 'sugarcane', 'cotton']
    
    return crop.lower() in [c.lower() for c in valid_crops]

def validate_year(year: int, min_year: int = 2000, max_year: int = None) -> bool:
    """Validate year input"""
    if max_year is None:
        max_year = datetime.now().year + 1
    
    return min_year <= year <= max_year

def calculate_growing_season_dates(year: int, crop: str = 'rice') -> Tuple[datetime, datetime]:
    """Calculate growing season start and end dates for a crop"""
    # Default rice growing season in India (Kharif season)
    if crop.lower() == 'rice':
        start_date = datetime(year, 6, 1)  # June 1st
        end_date = datetime(year, 11, 30)  # November 30th
    elif crop.lower() == 'wheat':
        start_date = datetime(year, 11, 1)  # November 1st
        end_date = datetime(year + 1, 4, 30)  # April 30th next year
    else:
        # Default to rice season
        start_date = datetime(year, 6, 1)
        end_date = datetime(year, 11, 30)
    
    return start_date, end_date

def calculate_confidence_score(prediction: float, model_std: float, 
                             feature_quality: float = 1.0) -> float:
    """Calculate confidence score for prediction"""
    # Base confidence from model uncertainty
    base_confidence = max(0, 1 - (model_std / prediction) if prediction > 0 else 0.5)
    
    # Adjust for feature quality
    confidence = base_confidence * feature_quality
    
    # Ensure confidence is between 0 and 1
    return max(0.1, min(1.0, confidence))

def format_advisory_text(advisory_type: str, recommendation: str, 
                        confidence: float, language: str = 'en') -> str:
    """Format advisory text with confidence indicator"""
    confidence_text = {
        'en': {
            'high': 'Highly recommended',
            'medium': 'Recommended',
            'low': 'Consider this option'
        },
        'or': {  # Odia
            'high': 'ଅତ୍ୟଧିକ ସୁପାରିଶ',
            'medium': 'ସୁପାରିଶ',
            'low': 'ଏହି ବିକଳ୍ପକୁ ବିଚାର କରନ୍ତୁ'
        }
    }
    
    # Determine confidence level
    if confidence >= 0.8:
        conf_level = 'high'
    elif confidence >= 0.6:
        conf_level = 'medium'
    else:
        conf_level = 'low'
    
    # Get confidence text
    conf_text = confidence_text.get(language, confidence_text['en']).get(conf_level, '')
    
    return f"{conf_text}: {recommendation}"

def create_prediction_intervals(predictions: np.ndarray, residuals: np.ndarray, 
                              confidence_level: float = 0.95) -> np.ndarray:
    """Create prediction intervals using residual distribution"""
    # Calculate quantiles from residuals
    alpha = 1 - confidence_level
    lower_quantile = alpha / 2
    upper_quantile = 1 - alpha / 2
    
    residual_std = np.std(residuals)
    z_score = 1.96  # For 95% confidence interval
    
    # Calculate intervals
    margin = z_score * residual_std
    lower_bounds = predictions - margin
    upper_bounds = predictions + margin
    
    return np.column_stack([lower_bounds, upper_bounds])

def load_model_metadata(model_path: str) -> Dict[str, Any]:
    """Load model metadata from JSON file"""
    metadata_path = model_path.replace('.pkl', '.json').replace('.xgb', '.json')
    
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            return json.load(f)
    else:
        logger.warning(f"Metadata file not found: {metadata_path}")
        return {}

def save_prediction_log(prediction_data: Dict[str, Any], log_file: str = 'predictions.log'):
    """Save prediction to log file"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'prediction_data': prediction_data
    }
    
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

def calculate_yield_gap(predicted_yield: float, potential_yield: float = None) -> Dict[str, float]:
    """Calculate yield gap analysis"""
    if potential_yield is None:
        # Use typical potential yields for rice in India (t/ha)
        potential_yield = 6.0
    
    yield_gap = potential_yield - predicted_yield
    yield_gap_percent = (yield_gap / potential_yield) * 100 if potential_yield > 0 else 0
    
    return {
        'predicted_yield': predicted_yield,
        'potential_yield': potential_yield,
        'yield_gap': yield_gap,
        'yield_gap_percent': yield_gap_percent,
        'efficiency': (predicted_yield / potential_yield) * 100 if potential_yield > 0 else 0
    }

def generate_improvement_suggestions(yield_gap_analysis: Dict[str, float], 
                                   input_features: Dict[str, Any]) -> List[str]:
    """Generate yield improvement suggestions based on gap analysis"""
    suggestions = []
    
    if yield_gap_analysis['yield_gap_percent'] > 20:
        suggestions.append("Consider soil testing and nutrient management")
        suggestions.append("Optimize irrigation scheduling")
        suggestions.append("Use improved seed varieties")
    
    if yield_gap_analysis['yield_gap_percent'] > 30:
        suggestions.append("Implement integrated pest management")
        suggestions.append("Consider precision agriculture techniques")
    
    # Feature-specific suggestions
    if 'soil_ph' in input_features:
        ph = input_features['soil_ph']
        if ph < 6.0:
            suggestions.append("Apply lime to increase soil pH")
        elif ph > 7.5:
            suggestions.append("Apply organic matter to reduce soil pH")
    
    return suggestions

def create_summary_report(predictions: List[Dict[str, Any]], 
                         output_file: str = 'prediction_summary.json'):
    """Create summary report of predictions"""
    if not predictions:
        return
    
    # Calculate summary statistics
    yields = [p['predicted_yield_t_ha'] for p in predictions]
    confidences = [p['confidence_score'] for p in predictions]
    
    summary = {
        'total_predictions': len(predictions),
        'average_yield': np.mean(yields),
        'median_yield': np.median(yields),
        'yield_std': np.std(yields),
        'min_yield': np.min(yields),
        'max_yield': np.max(yields),
        'average_confidence': np.mean(confidences),
        'high_confidence_predictions': sum(1 for c in confidences if c >= 0.8),
        'generated_at': datetime.now().isoformat()
    }
    
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Summary report saved to {output_file}")
    return summary

class ConfigManager:
    """Configuration manager for the application"""
    
    def __init__(self, config_file: str = 'config.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'model': {
                'default_model_path': 'models/best_model.json',
                'confidence_threshold': 0.6,
                'prediction_interval_confidence': 0.95
            },
            'data': {
                'default_location': {
                    'lat': 20.508973,
                    'lon': 86.418039,
                    'district': 'Kendrapara',
                    'state': 'Odisha'
                },
                'valid_crops': ['rice', 'wheat', 'maize'],
                'year_range': [2000, 2030]
            },
            'api': {
                'nasa_power_base_url': 'https://power.larc.nasa.gov/api/temporal/daily/point',
                'soilgrids_base_url': 'https://rest.isric.org/soilgrids/v2.0/properties/query',
                'request_timeout': 30
            },
            'translation': {
                'supported_languages': ['en', 'or'],
                'default_language': 'en',
                'cache_translations': True
            }
        }
    
    def save_config(self):
        """Save current configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()

# Global configuration instance
config = ConfigManager()
