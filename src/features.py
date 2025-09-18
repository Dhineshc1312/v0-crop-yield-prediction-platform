"""
Feature engineering module for crop yield prediction.
Contains feature extraction, transformation, and selection utilities.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_selection import SelectKBest, f_regression
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class FeatureEngineer:
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        self.feature_names = []
        self.selected_features = []
        
    def create_weather_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create advanced weather features"""
        df = df.copy()
        
        # Temperature-based features
        if 'temp_mean' in df.columns and 'temp_max' in df.columns and 'temp_min' in df.columns:
            df['temp_range'] = df['temp_max'] - df['temp_min']
            df['temp_stress'] = np.where(df['temp_max'] > 35, df['temp_max'] - 35, 0)  # Heat stress
            df['temp_cold_stress'] = np.where(df['temp_min'] < 15, 15 - df['temp_min'], 0)  # Cold stress
        
        # Precipitation features
        if 'precip_sum' in df.columns and 'precip_mean' in df.columns:
            df['precip_intensity'] = df['precip_sum'] / (df['precip_mean'] + 1e-6)
            df['drought_stress'] = np.where(df['precip_sum'] < 500, 500 - df['precip_sum'], 0)
            df['flood_risk'] = np.where(df['precip_sum'] > 1500, df['precip_sum'] - 1500, 0)
        
        # Humidity and solar features
        if 'humidity_mean' in df.columns:
            df['humidity_stress'] = np.where(df['humidity_mean'] > 85, df['humidity_mean'] - 85, 0)
        
        if 'solar_mean' in df.columns:
            df['solar_deficit'] = np.where(df['solar_mean'] < 15, 15 - df['solar_mean'], 0)
        
        # Growing degree days variations
        if 'gdd' in df.columns:
            df['gdd_optimal'] = np.where((df['gdd'] >= 2000) & (df['gdd'] <= 3000), 1, 0)
            df['gdd_deficit'] = np.where(df['gdd'] < 2000, 2000 - df['gdd'], 0)
            df['gdd_excess'] = np.where(df['gdd'] > 3000, df['gdd'] - 3000, 0)
        
        return df
    
    def create_soil_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create advanced soil features"""
        df = df.copy()
        
        # Soil texture ratios
        soil_texture_cols = ['soil_clay', 'soil_sand', 'soil_silt']
        if all(col in df.columns for col in soil_texture_cols):
            df['clay_sand_ratio'] = df['soil_clay'] / (df['soil_sand'] + 1e-6)
            df['silt_clay_ratio'] = df['soil_silt'] / (df['soil_clay'] + 1e-6)
            
            # Soil texture classification (simplified)
            df['soil_texture_score'] = (
                df['soil_clay'] * 0.3 + 
                df['soil_silt'] * 0.5 + 
                df['soil_sand'] * 0.2
            )
        
        # Soil fertility indicators
        if 'soil_phh2o' in df.columns:
            df['soil_ph_optimal'] = np.where((df['soil_phh2o'] >= 6.0) & (df['soil_phh2o'] <= 7.0), 1, 0)
            df['soil_ph_stress'] = np.abs(df['soil_phh2o'] - 6.5)  # Distance from optimal pH
        
        if 'soil_soc' in df.columns:
            df['soil_organic_high'] = np.where(df['soil_soc'] > 2.0, 1, 0)
            df['soil_organic_low'] = np.where(df['soil_soc'] < 1.0, 1, 0)
        
        # Nutrient availability
        if 'soil_cec' in df.columns and 'soil_phh2o' in df.columns:
            df['nutrient_availability'] = df['soil_cec'] * (1 - df['soil_ph_stress'])
        
        return df
    
    def create_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create temporal and cyclical features"""
        df = df.copy()
        
        if 'year' in df.columns:
            # Year-based features
            df['year_normalized'] = (df['year'] - df['year'].min()) / (df['year'].max() - df['year'].min())
            
            # Cyclical patterns (assuming some multi-year cycles)
            df['year_cycle_3'] = np.sin(2 * np.pi * df['year'] / 3)
            df['year_cycle_5'] = np.sin(2 * np.pi * df['year'] / 5)
        
        return df
    
    def create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create interaction features between weather and soil"""
        df = df.copy()
        
        # Weather-soil interactions
        if 'precip_sum' in df.columns and 'soil_clay' in df.columns:
            df['water_retention'] = df['precip_sum'] * df['soil_clay'] / 100
        
        if 'temp_mean' in df.columns and 'soil_soc' in df.columns:
            df['temp_organic_interaction'] = df['temp_mean'] * df['soil_soc']
        
        if 'gdd' in df.columns and 'soil_ph_optimal' in df.columns:
            df['gdd_ph_interaction'] = df['gdd'] * df['soil_ph_optimal']
        
        # Stress combinations
        stress_cols = [col for col in df.columns if 'stress' in col]
        if len(stress_cols) > 1:
            df['total_stress'] = df[stress_cols].sum(axis=1)
        
        return df
    
    def encode_categorical_features(self, df: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """Encode categorical features"""
        df = df.copy()
        
        categorical_cols = ['state', 'district', 'crop']
        
        for col in categorical_cols:
            if col in df.columns:
                if fit:
                    if col not in self.encoders:
                        self.encoders[col] = LabelEncoder()
                    df[f'{col}_encoded'] = self.encoders[col].fit_transform(df[col].astype(str))
                else:
                    if col in self.encoders:
                        # Handle unseen categories
                        unique_vals = set(df[col].astype(str))
                        known_vals = set(self.encoders[col].classes_)
                        
                        if unique_vals.issubset(known_vals):
                            df[f'{col}_encoded'] = self.encoders[col].transform(df[col].astype(str))
                        else:
                            # For unseen categories, use most frequent class
                            most_frequent = self.encoders[col].classes_[0]
                            df[col] = df[col].astype(str).apply(
                                lambda x: x if x in known_vals else most_frequent
                            )
                            df[f'{col}_encoded'] = self.encoders[col].transform(df[col])
        
        return df
    
    def select_features(self, X: pd.DataFrame, y: pd.Series, k: int = 50) -> List[str]:
        """Select top k features using statistical tests"""
        # Remove non-numeric columns
        numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        X_numeric = X[numeric_cols]
        
        # Handle missing values
        X_numeric = X_numeric.fillna(X_numeric.median())
        
        # Feature selection
        selector = SelectKBest(score_func=f_regression, k=min(k, len(numeric_cols)))
        selector.fit(X_numeric, y)
        
        # Get selected feature names
        selected_mask = selector.get_support()
        selected_features = [numeric_cols[i] for i, selected in enumerate(selected_mask) if selected]
        
        # Store feature scores for analysis
        feature_scores = dict(zip(numeric_cols, selector.scores_))
        sorted_features = sorted(feature_scores.items(), key=lambda x: x[1], reverse=True)
        
        print(f"Top 10 features by F-score:")
        for feature, score in sorted_features[:10]:
            print(f"  {feature}: {score:.2f}")
        
        self.selected_features = selected_features
        return selected_features
    
    def scale_features(self, X: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """Scale numerical features"""
        X = X.copy()
        
        # Identify columns to scale (exclude encoded categorical and binary features)
        cols_to_scale = []
        for col in X.columns:
            if X[col].dtype in ['float64', 'int64']:
                # Skip binary features and encoded categories
                if not (col.endswith('_encoded') or 
                       col.endswith('_optimal') or 
                       col.endswith('_high') or 
                       col.endswith('_low') or
                       X[col].nunique() <= 2):
                    cols_to_scale.append(col)
        
        if fit:
            for col in cols_to_scale:
                if col not in self.scalers:
                    self.scalers[col] = StandardScaler()
                X[col] = self.scalers[col].fit_transform(X[[col]])
        else:
            for col in cols_to_scale:
                if col in self.scalers:
                    X[col] = self.scalers[col].transform(X[[col]])
        
        return X
    
    def engineer_features(self, df: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """Main feature engineering pipeline"""
        print("Starting feature engineering...")
        
        # Create advanced features
        df = self.create_weather_features(df)
        df = self.create_soil_features(df)
        df = self.create_temporal_features(df)
        df = self.create_interaction_features(df)
        
        # Encode categorical features
        df = self.encode_categorical_features(df, fit=fit)
        
        # Store feature names
        if fit:
            self.feature_names = [col for col in df.columns 
                                if col not in ['yield_t_ha', 'year', 'state', 'district', 'crop', 
                                             'area_ha', 'production_tonnes']]
        
        print(f"Created {len(self.feature_names)} features")
        return df
    
    def prepare_features(self, df: pd.DataFrame, target_col: str = 'yield_t_ha', 
                        fit: bool = True, feature_selection: bool = True) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features for ML training"""
        # Engineer features
        df_engineered = self.engineer_features(df, fit=fit)
        
        # Separate features and target
        if target_col in df_engineered.columns:
            y = df_engineered[target_col]
            X = df_engineered.drop(columns=[target_col])
        else:
            y = None
            X = df_engineered
        
        # Remove non-feature columns
        cols_to_remove = ['year', 'state', 'district', 'crop', 'area_ha', 'production_tonnes']
        X = X.drop(columns=[col for col in cols_to_remove if col in X.columns])
        
        # Feature selection
        if fit and feature_selection and y is not None:
            selected_features = self.select_features(X, y, k=50)
            X = X[selected_features]
        elif not fit and self.selected_features:
            # Use previously selected features
            available_features = [col for col in self.selected_features if col in X.columns]
            X = X[available_features]
        
        # Scale features
        X = self.scale_features(X, fit=fit)
        
        # Handle any remaining missing values
        X = X.fillna(X.median())
        
        print(f"Final feature matrix shape: {X.shape}")
        if y is not None:
            print(f"Target variable shape: {y.shape}")
        
        return X, y

def create_feature_importance_report(feature_names: List[str], importances: np.ndarray, 
                                   top_k: int = 20) -> pd.DataFrame:
    """Create a feature importance report"""
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': importances
    }).sort_values('importance', ascending=False)
    
    print(f"\nTop {top_k} Most Important Features:")
    print("=" * 50)
    for i, (_, row) in enumerate(importance_df.head(top_k).iterrows()):
        print(f"{i+1:2d}. {row['feature']:<30} {row['importance']:.4f}")
    
    return importance_df
