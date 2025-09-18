"""
Data preprocessing module for crop yield prediction.
Combines weather, soil, and crop data into a clean dataset for ML training.
"""

import pandas as pd
import numpy as np
import json
import argparse
import os
from typing import Dict, List
from fetch_data import DataFetcher

class DataPreprocessor:
    def __init__(self):
        self.fetcher = DataFetcher()
    
    def load_crop_data(self, crop_file: str) -> pd.DataFrame:
        """Load and validate crop production data"""
        print(f"Loading crop data from {crop_file}")
        
        df = pd.read_csv(crop_file)
        
        # Calculate yield if not present
        if 'yield_t_ha' not in df.columns:
            df['yield_t_ha'] = df['production_tonnes'] / df['area_ha']
        
        # Basic validation
        df = df.dropna(subset=['yield_t_ha'])
        df = df[df['yield_t_ha'] > 0]  # Remove invalid yields
        
        print(f"Loaded {len(df)} crop records")
        return df
    
    def load_weather_data(self, weather_file: str) -> Dict:
        """Load weather data from JSON file"""
        print(f"Loading weather data from {weather_file}")
        
        with open(weather_file, 'r') as f:
            return json.load(f)
    
    def load_soil_data(self, soil_file: str) -> Dict:
        """Load soil data from JSON file"""
        print(f"Loading soil data from {soil_file}")
        
        with open(soil_file, 'r') as f:
            return json.load(f)
    
    def create_weather_features(self, weather_data: Dict, years: List[int]) -> pd.DataFrame:
        """Create weather features for each year"""
        weather_features = []
        
        for year in years:
            features = self.fetcher.process_weather_data(weather_data, year)
            features['year'] = year
            weather_features.append(features)
        
        return pd.DataFrame(weather_features)
    
    def create_soil_features(self, soil_data: Dict) -> Dict:
        """Create soil features (same for all years)"""
        return self.fetcher.process_soil_data(soil_data)
    
    def create_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create lagged yield features for time series patterns"""
        df = df.sort_values(['district', 'crop', 'year'])
        
        # Create lag features
        df['yield_lag1'] = df.groupby(['district', 'crop'])['yield_t_ha'].shift(1)
        df['yield_lag2'] = df.groupby(['district', 'crop'])['yield_t_ha'].shift(2)
        df['yield_lag3'] = df.groupby(['district', 'crop'])['yield_t_ha'].shift(3)
        
        # Create rolling mean features
        df['yield_lag3_mean'] = df.groupby(['district', 'crop'])['yield_t_ha'].rolling(3, min_periods=1).mean().reset_index(0, drop=True)
        
        # Create trend feature (simple linear trend over last 3 years)
        def calculate_trend(series):
            if len(series) < 2:
                return 0
            x = np.arange(len(series))
            return np.polyfit(x, series, 1)[0]  # Slope of linear fit
        
        df['yield_trend'] = df.groupby(['district', 'crop'])['yield_t_ha'].rolling(3, min_periods=2).apply(calculate_trend).reset_index(0, drop=True)
        
        return df
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values with domain-aware imputation"""
        print("Handling missing values...")
        
        # Weather features - use median imputation
        weather_cols = [col for col in df.columns if any(x in col for x in ['precip', 'temp', 'humidity', 'solar', 'gdd'])]
        for col in weather_cols:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].median())
        
        # Soil features - use median imputation
        soil_cols = [col for col in df.columns if col.startswith('soil_')]
        for col in soil_cols:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].median())
        
        # Lag features - forward fill then backward fill
        lag_cols = [col for col in df.columns if 'lag' in col or 'trend' in col]
        for col in lag_cols:
            if col in df.columns:
                df[col] = df[col].fillna(method='ffill').fillna(method='bfill')
        
        return df
    
    def create_feature_flags(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create flags for missing data to help model understand data quality"""
        # Flag missing weather data
        weather_cols = [col for col in df.columns if any(x in col for x in ['precip', 'temp', 'humidity', 'solar', 'gdd'])]
        for col in weather_cols:
            if col in df.columns:
                df[f'{col}_missing'] = df[col].isna().astype(int)
        
        return df
    
    def process_dataset(self, crop_file: str, weather_file: str, soil_file: str) -> pd.DataFrame:
        """Main processing pipeline"""
        print("Starting data preprocessing pipeline...")
        
        # Load data
        crop_df = self.load_crop_data(crop_file)
        weather_data = self.load_weather_data(weather_file)
        soil_data = self.load_soil_data(soil_file)
        
        # Get unique years from crop data
        years = sorted(crop_df['year'].unique())
        
        # Create weather features
        weather_df = self.create_weather_features(weather_data, years)
        
        # Create soil features
        soil_features = self.create_soil_features(soil_data)
        
        # Merge crop data with weather data
        df = crop_df.merge(weather_df, on='year', how='left')
        
        # Add soil features to all rows
        for key, value in soil_features.items():
            df[key] = value
        
        # Create lag features
        df = self.create_lag_features(df)
        
        # Create missing data flags before imputation
        df = self.create_feature_flags(df)
        
        # Handle missing values
        df = self.handle_missing_values(df)
        
        # Final cleanup
        df = df.dropna(subset=['yield_t_ha'])  # Remove rows with missing target
        
        print(f"Final dataset shape: {df.shape}")
        print(f"Features: {list(df.columns)}")
        
        return df

def main():
    parser = argparse.ArgumentParser(description='Preprocess agricultural data for ML training')
    parser.add_argument('--in_dir', type=str, default='data/raw', help='Input directory with raw data')
    parser.add_argument('--out_file', type=str, default='data/processed/dataset_clean.csv', help='Output file path')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(os.path.dirname(args.out_file), exist_ok=True)
    
    # File paths
    crop_file = os.path.join(args.in_dir, 'crop_districts.csv')
    weather_file = os.path.join(args.in_dir, 'nasa_power.json')
    soil_file = os.path.join(args.in_dir, 'soilgrids.json')
    
    # Check if files exist
    for file_path in [crop_file, weather_file, soil_file]:
        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found. Please run fetch_data.py first.")
            return
    
    # Process data
    preprocessor = DataPreprocessor()
    df = preprocessor.process_dataset(crop_file, weather_file, soil_file)
    
    # Save processed dataset
    df.to_csv(args.out_file, index=False)
    print(f"Processed dataset saved to {args.out_file}")
    
    # Print summary statistics
    print("\nDataset Summary:")
    print(f"Shape: {df.shape}")
    print(f"Yield statistics:")
    print(df['yield_t_ha'].describe())
    
    print(f"\nFeature columns:")
    feature_cols = [col for col in df.columns if col not in ['year', 'state', 'district', 'crop', 'area_ha', 'production_tonnes']]
    for col in feature_cols:
        print(f"  {col}")

if __name__ == "__main__":
    main()
