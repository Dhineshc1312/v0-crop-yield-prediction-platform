"""
Data fetching module for crop yield prediction platform.
Fetches weather data from NASA POWER API, soil data from SoilGrids, and processes crop data.
"""

import requests
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import argparse
from typing import Dict, List, Tuple
import time

class DataFetcher:
    def __init__(self):
        self.nasa_power_base = "https://power.larc.nasa.gov/api/temporal/daily/point"
        self.soilgrids_base = "https://rest.isric.org/soilgrids/v2.0/properties/query"
        
    def fetch_weather_data(self, lat: float, lon: float, start_year: int, end_year: int) -> Dict:
        """Fetch weather data from NASA POWER API"""
        print(f"Fetching weather data for lat={lat}, lon={lon}, years={start_year}-{end_year}")
        
        # Parameters for crop-relevant weather data
        parameters = [
            "T2M",        # Temperature at 2 meters
            "T2M_MAX",    # Maximum temperature
            "T2M_MIN",    # Minimum temperature
            "PRECTOTCORR", # Precipitation corrected
            "RH2M",       # Relative humidity at 2 meters
            "ALLSKY_SFC_SW_DWN"  # Solar radiation
        ]
        
        params = {
            "parameters": ",".join(parameters),
            "community": "AG",  # Agroclimatology community
            "longitude": lon,
            "latitude": lat,
            "start": f"{start_year}0101",
            "end": f"{end_year}1231",
            "format": "JSON"
        }
        
        try:
            response = requests.get(self.nasa_power_base, params=params, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return {}
    
    def fetch_soil_data(self, lat: float, lon: float) -> Dict:
        """Fetch soil properties from SoilGrids API"""
        print(f"Fetching soil data for lat={lat}, lon={lon}")
        
        # Soil properties relevant for crop yield
        properties = [
            "phh2o",     # pH in water
            "soc",       # Soil organic carbon
            "clay",      # Clay content
            "sand",      # Sand content
            "silt",      # Silt content
            "cec",       # Cation exchange capacity
            "nitrogen"   # Total nitrogen
        ]
        
        params = {
            "lon": lon,
            "lat": lat,
            "property": properties,
            "depth": "0-30cm",  # Top soil layer
            "value": "mean"
        }
        
        try:
            response = requests.get(self.soilgrids_base, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching soil data: {e}")
            return {}
    
    def process_weather_data(self, weather_data: Dict, year: int) -> Dict:
        """Process weather data to extract seasonal aggregates"""
        if not weather_data or 'properties' not in weather_data:
            return {}
        
        properties = weather_data['properties']['parameter']
        
        # Convert daily data to pandas DataFrame for easier processing
        daily_data = {}
        for param, values in properties.items():
            dates = list(values.keys())
            vals = list(values.values())
            daily_data[param] = vals
        
        # Create date index
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        df = pd.DataFrame(daily_data, index=date_range[:len(vals)])
        
        # Calculate seasonal aggregates (assuming rice growing season: June-November)
        growing_season = df[(df.index.month >= 6) & (df.index.month <= 11)]
        
        aggregates = {
            'precip_sum': growing_season['PRECTOTCORR'].sum() if 'PRECTOTCORR' in growing_season else 0,
            'precip_mean': growing_season['PRECTOTCORR'].mean() if 'PRECTOTCORR' in growing_season else 0,
            'temp_mean': growing_season['T2M'].mean() if 'T2M' in growing_season else 0,
            'temp_max': growing_season['T2M_MAX'].max() if 'T2M_MAX' in growing_season else 0,
            'temp_min': growing_season['T2M_MIN'].min() if 'T2M_MIN' in growing_season else 0,
            'humidity_mean': growing_season['RH2M'].mean() if 'RH2M' in growing_season else 0,
            'solar_mean': growing_season['ALLSKY_SFC_SW_DWN'].mean() if 'ALLSKY_SFC_SW_DWN' in growing_season else 0,
        }
        
        # Calculate growing degree days (GDD) for rice (base temp 10°C)
        if 'T2M' in growing_season:
            gdd = ((growing_season['T2M'] - 10).clip(lower=0)).sum()
            aggregates['gdd'] = gdd
        
        return aggregates
    
    def process_soil_data(self, soil_data: Dict) -> Dict:
        """Process soil data to extract relevant properties"""
        if not soil_data or 'properties' not in soil_data:
            return {}
        
        layers = soil_data['properties']['layers']
        soil_props = {}
        
        for layer in layers:
            prop_name = layer['name']
            if layer['depths']:
                # Take the first depth (0-30cm)
                depth_data = layer['depths'][0]
                if 'values' in depth_data:
                    # Take mean value
                    soil_props[f'soil_{prop_name}'] = depth_data['values']['mean']
        
        return soil_props

def main():
    parser = argparse.ArgumentParser(description='Fetch agricultural data for crop yield prediction')
    parser.add_argument('--lat', type=float, default=20.508973, help='Latitude')
    parser.add_argument('--lon', type=float, default=86.418039, help='Longitude')
    parser.add_argument('--start', type=int, default=2010, help='Start year')
    parser.add_argument('--end', type=int, default=2023, help='End year')
    parser.add_argument('--outdir', type=str, default='data/raw', help='Output directory')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.outdir, exist_ok=True)
    
    fetcher = DataFetcher()
    
    # Fetch weather data
    weather_data = fetcher.fetch_weather_data(args.lat, args.lon, args.start, args.end)
    if weather_data:
        with open(f"{args.outdir}/nasa_power.json", 'w') as f:
            json.dump(weather_data, f, indent=2)
        print(f"Weather data saved to {args.outdir}/nasa_power.json")
    
    # Fetch soil data
    soil_data = fetcher.fetch_soil_data(args.lat, args.lon)
    if soil_data:
        with open(f"{args.outdir}/soilgrids.json", 'w') as f:
            json.dump(soil_data, f, indent=2)
        print(f"Soil data saved to {args.outdir}/soilgrids.json")
    
    # Create sample crop data for Kendrapara, Odisha (Rice)
    sample_crop_data = {
        'year': list(range(args.start, args.end + 1)),
        'state': ['Odisha'] * (args.end - args.start + 1),
        'district': ['Kendrapara'] * (args.end - args.start + 1),
        'crop': ['Rice'] * (args.end - args.start + 1),
        'area_ha': [1500 + i * 10 for i in range(args.end - args.start + 1)],  # Sample data
        'production_tonnes': [4200 + i * 50 for i in range(args.end - args.start + 1)]  # Sample data
    }
    
    crop_df = pd.DataFrame(sample_crop_data)
    crop_df.to_csv(f"{args.outdir}/crop_districts.csv", index=False)
    print(f"Sample crop data saved to {args.outdir}/crop_districts.csv")

if __name__ == "__main__":
    main()
