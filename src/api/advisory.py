"""
Advisory engine for crop yield prediction platform.
Generates farming recommendations based on predictions and input data.
"""

import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from .predict import PredictionRequest

logger = logging.getLogger(__name__)

class AdvisoryEngine:
    """Advisory engine for generating farming recommendations"""
    
    def __init__(self):
        self.advisory_rules = self.load_advisory_rules()
    
    def load_advisory_rules(self) -> Dict[str, Any]:
        """Load advisory rules and thresholds"""
        return {
            'irrigation': {
                'low_rainfall_threshold': 500,  # mm
                'high_rainfall_threshold': 1200,  # mm
                'optimal_irrigation_events': 8,
                'critical_growth_stages': ['tillering', 'flowering', 'grain_filling']
            },
            'fertilizer': {
                'rice': {
                    'N_recommended': 120,  # kg/ha
                    'P_recommended': 60,   # kg/ha
                    'K_recommended': 40,   # kg/ha
                    'split_applications': 3
                },
                'wheat': {
                    'N_recommended': 100,  # kg/ha
                    'P_recommended': 50,   # kg/ha
                    'K_recommended': 30,   # kg/ha
                    'split_applications': 2
                }
            },
            'pest_risk': {
                'high_humidity_threshold': 80,  # %
                'high_temp_threshold': 30,      # °C
                'rainfall_pest_threshold': 100, # mm in 7 days
            },
            'yield_thresholds': {
                'rice': {'low': 2.0, 'medium': 3.5, 'high': 5.0},
                'wheat': {'low': 1.5, 'medium': 2.5, 'high': 4.0}
            }
        }
    
    async def generate_advisory(self, prediction_result: Dict[str, Any], 
                              request: PredictionRequest) -> Dict[str, Any]:
        """Generate comprehensive advisory based on prediction and inputs"""
        try:
            logger.info("Generating advisory recommendations")
            
            # Extract key information
            predicted_yield = prediction_result['predicted_yield']
            confidence = prediction_result['confidence']
            top_features = prediction_result['top_features']
            
            # Generate individual advisories
            irrigation_advisory = self.generate_irrigation_advisory(
                prediction_result, request
            )
            
            fertilizer_advisory = self.generate_fertilizer_advisory(
                prediction_result, request
            )
            
            pest_advisory = self.generate_pest_advisory(
                prediction_result, request
            )
            
            # Generate general recommendations
            general_advisory = self.generate_general_advisory(
                prediction_result, request
            )
            
            # Combine all advisories
            advisory = {
                'irrigation': irrigation_advisory,
                'fertilizer': fertilizer_advisory,
                'pest': pest_advisory,
                'general': general_advisory
            }
            
            # Add confidence-based disclaimers
            if confidence < 0.7:
                advisory['disclaimer'] = (
                    "Recommendations are based on limited data. "
                    "Consider consulting local agricultural experts."
                )
            
            return {
                'advisory': advisory,
                'confidence': confidence,
                'based_on_features': [f['feature'] for f in top_features[:3]]
            }
            
        except Exception as e:
            logger.error(f"Advisory generation failed: {e}")
            return {
                'advisory': {
                    'irrigation': "Unable to generate irrigation advisory",
                    'fertilizer': "Unable to generate fertilizer advisory",
                    'pest': "Unable to generate pest advisory",
                    'general': "Consult local agricultural extension services"
                },
                'confidence': 0.1,
                'based_on_features': []
            }
    
    def generate_irrigation_advisory(self, prediction_result: Dict[str, Any], 
                                   request: PredictionRequest) -> str:
        """Generate irrigation advisory"""
        try:
            # Extract relevant features
            top_features = {f['feature']: f['value'] for f in prediction_result['top_features']}
            
            # Get precipitation data
            precip_sum = top_features.get('precip_sum', 800)
            precip_mean = top_features.get('precip_mean', 4.0)
            
            # Get farmer inputs
            current_irrigation = 0
            if request.farmer_inputs and request.farmer_inputs.irrigation_events:
                current_irrigation = request.farmer_inputs.irrigation_events
            
            # Generate advisory based on rainfall
            if precip_sum < self.advisory_rules['irrigation']['low_rainfall_threshold']:
                # Low rainfall scenario
                recommended_events = self.advisory_rules['irrigation']['optimal_irrigation_events'] + 2
                advisory = (
                    f"Low rainfall detected ({precip_sum:.0f}mm). "
                    f"Increase irrigation to {recommended_events} events. "
                    f"Apply 50-60mm per irrigation. "
                    f"Focus on critical growth stages: tillering and flowering."
                )
            elif precip_sum > self.advisory_rules['irrigation']['high_rainfall_threshold']:
                # High rainfall scenario
                advisory = (
                    f"High rainfall detected ({precip_sum:.0f}mm). "
                    f"Reduce irrigation frequency. Monitor for waterlogging. "
                    f"Ensure proper drainage. Apply irrigation only during dry spells."
                )
            else:
                # Normal rainfall scenario
                recommended_events = self.advisory_rules['irrigation']['optimal_irrigation_events']
                advisory = (
                    f"Normal rainfall pattern ({precip_sum:.0f}mm). "
                    f"Maintain {recommended_events} irrigation events. "
                    f"Apply 40-50mm per irrigation. "
                    f"Monitor soil moisture at 15cm depth."
                )
            
            # Add timing recommendations
            advisory += " Best irrigation times: early morning (6-8 AM) or evening (6-8 PM)."
            
            return advisory
            
        except Exception as e:
            logger.error(f"Irrigation advisory generation failed: {e}")
            return "Monitor soil moisture and irrigate when top 5cm soil is dry."
    
    def generate_fertilizer_advisory(self, prediction_result: Dict[str, Any], 
                                   request: PredictionRequest) -> str:
        """Generate fertilizer advisory"""
        try:
            crop = request.crop.lower()
            top_features = {f['feature']: f['value'] for f in prediction_result['top_features']}
            
            # Get soil data
            soil_ph = top_features.get('soil_phh2o', 6.5)
            soil_organic = top_features.get('soil_soc', 1.5)
            soil_nitrogen = top_features.get('soil_nitrogen', 0.15)
            
            # Get current fertilizer usage
            current_n = 0
            current_p = 0
            current_k = 0
            
            if request.farmer_inputs:
                current_n = request.farmer_inputs.fertilizer_N_kg or 0
                current_p = request.farmer_inputs.fertilizer_P_kg or 0
                current_k = request.farmer_inputs.fertilizer_K_kg or 0
            
            # Get crop-specific recommendations
            crop_rules = self.advisory_rules['fertilizer'].get(crop, 
                                                             self.advisory_rules['fertilizer']['rice'])
            
            recommended_n = crop_rules['N_recommended']
            recommended_p = crop_rules['P_recommended']
            recommended_k = crop_rules['K_recommended']
            
            # Adjust based on soil conditions
            if soil_ph < 6.0:
                advisory = f"Soil pH is low ({soil_ph:.1f}). Apply lime before fertilization. "
            elif soil_ph > 7.5:
                advisory = f"Soil pH is high ({soil_ph:.1f}). Consider sulfur application. "
            else:
                advisory = f"Soil pH is optimal ({soil_ph:.1f}). "
            
            # Nitrogen recommendations
            if soil_organic < 1.0:
                recommended_n += 20  # Increase N for low organic matter
                advisory += f"Low organic matter detected. Increase nitrogen to {recommended_n} kg/ha. "
            
            n_gap = recommended_n - current_n
            if n_gap > 10:
                advisory += f"Apply additional {n_gap:.0f} kg/ha nitrogen. "
            elif n_gap < -10:
                advisory += f"Reduce nitrogen by {abs(n_gap):.0f} kg/ha to avoid lodging. "
            else:
                advisory += f"Current nitrogen level is adequate. "
            
            # Phosphorus and Potassium
            if current_p < recommended_p:
                advisory += f"Apply {recommended_p - current_p:.0f} kg/ha phosphorus. "
            
            if current_k < recommended_k:
                advisory += f"Apply {recommended_k - current_k:.0f} kg/ha potassium. "
            
            # Application timing
            splits = crop_rules['split_applications']
            advisory += f"Split fertilizer application into {splits} doses: "
            
            if crop == 'rice':
                advisory += "basal (50%), tillering (25%), panicle initiation (25%)."
            else:
                advisory += "basal (60%), tillering/jointing (40%)."
            
            return advisory
            
        except Exception as e:
            logger.error(f"Fertilizer advisory generation failed: {e}")
            return "Apply balanced NPK fertilizer as per soil test recommendations."
    
    def generate_pest_advisory(self, prediction_result: Dict[str, Any], 
                             request: PredictionRequest) -> str:
        """Generate pest and disease advisory"""
        try:
            top_features = {f['feature']: f['value'] for f in prediction_result['top_features']}
            crop = request.crop.lower()
            
            # Get weather parameters
            humidity = top_features.get('humidity_mean', 75)
            temp_max = top_features.get('temp_max', 30)
            precip_sum = top_features.get('precip_sum', 800)
            
            # Assess pest risk
            risk_level = "Low"
            risk_factors = []
            
            if humidity > self.advisory_rules['pest_risk']['high_humidity_threshold']:
                risk_level = "High"
                risk_factors.append("high humidity")
            
            if temp_max > self.advisory_rules['pest_risk']['high_temp_threshold']:
                if "High" not in risk_level:
                    risk_level = "Medium"
                risk_factors.append("high temperature")
            
            if precip_sum > 1000:
                risk_level = "High"
                risk_factors.append("excessive rainfall")
            
            # Generate crop-specific advisory
            advisory = f"{risk_level} pest risk detected"
            if risk_factors:
                advisory += f" due to {', '.join(risk_factors)}. "
            else:
                advisory += ". "
            
            if crop == 'rice':
                if risk_level == "High":
                    advisory += (
                        "Monitor for blast, brown spot, and stem borer. "
                        "Apply preventive fungicide spray. "
                        "Use pheromone traps for stem borer control. "
                    )
                elif risk_level == "Medium":
                    advisory += (
                        "Regular field monitoring recommended. "
                        "Watch for early signs of blast and bacterial blight. "
                    )
                else:
                    advisory += (
                        "Continue regular field inspection. "
                        "Maintain field hygiene. "
                    )
            else:
                # General advisory for other crops
                if risk_level == "High":
                    advisory += (
                        "Increase field monitoring frequency. "
                        "Consider preventive spray if weather continues. "
                    )
                else:
                    advisory += (
                        "Regular monitoring sufficient. "
                        "Maintain good field sanitation. "
                    )
            
            # Add IPM recommendations
            advisory += (
                "Use integrated pest management: "
                "biological control, resistant varieties, and targeted pesticide use."
            )
            
            return advisory
            
        except Exception as e:
            logger.error(f"Pest advisory generation failed: {e}")
            return "Monitor crops regularly for pests and diseases. Use IPM practices."
    
    def generate_general_advisory(self, prediction_result: Dict[str, Any], 
                                request: PredictionRequest) -> str:
        """Generate general farming advisory"""
        try:
            predicted_yield = prediction_result['predicted_yield']
            confidence = prediction_result['confidence']
            crop = request.crop.lower()
            
            # Get yield category
            thresholds = self.advisory_rules['yield_thresholds'].get(crop, 
                                                                   self.advisory_rules['yield_thresholds']['rice'])
            
            if predicted_yield < thresholds['low']:
                yield_category = "below average"
                improvement_potential = "high"
            elif predicted_yield < thresholds['medium']:
                yield_category = "average"
                improvement_potential = "medium"
            else:
                yield_category = "above average"
                improvement_potential = "low"
            
            advisory = f"Predicted yield is {yield_category} ({predicted_yield:.1f} t/ha). "
            
            # Improvement suggestions
            if improvement_potential == "high":
                advisory += (
                    "Significant improvement possible through: "
                    "soil testing, balanced nutrition, timely operations, "
                    "and improved varieties. "
                )
            elif improvement_potential == "medium":
                advisory += (
                    "Moderate improvement possible through: "
                    "precision nutrient management and pest control. "
                )
            else:
                advisory += (
                    "Maintain current good practices. "
                    "Focus on cost optimization and sustainability. "
                )
            
            # Confidence-based recommendations
            if confidence < 0.6:
                advisory += (
                    "Prediction confidence is moderate. "
                    "Consider multiple information sources for decision making. "
                )
            
            # Seasonal recommendations
            current_month = datetime.now().month
            if crop == 'rice' and 4 <= current_month <= 6:
                advisory += "Prepare for kharif season: check seed quality, repair equipment."
            elif crop == 'wheat' and 10 <= current_month <= 12:
                advisory += "Prepare for rabi season: ensure timely sowing for optimal yield."
            
            # Market advisory
            advisory += (
                "Monitor market prices and consider value addition opportunities. "
                "Maintain harvest and post-harvest records for better planning."
            )
            
            return advisory
            
        except Exception as e:
            logger.error(f"General advisory generation failed: {e}")
            return "Follow recommended agricultural practices for your region and crop."
    
    def get_advisory_confidence(self, prediction_confidence: float, 
                              data_quality: float) -> float:
        """Calculate advisory confidence based on prediction and data quality"""
        return min(prediction_confidence, data_quality) * 0.9  # Slightly conservative
