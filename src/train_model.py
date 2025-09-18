"""
Model training module for crop yield prediction.
Supports XGBoost, LightGBM, and optional PyTorch models with MLflow tracking.
"""

import pandas as pd
import numpy as np
import json
import argparse
import os
import pickle
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

# ML libraries
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
import lightgbm as lgb

# MLflow for experiment tracking
import mlflow
import mlflow.sklearn
import mlflow.xgboost
import mlflow.lightgbm

# Custom modules
from features import FeatureEngineer, create_feature_importance_report

class ModelTrainer:
    def __init__(self, mlflow_tracking_uri: Optional[str] = None):
        self.feature_engineer = FeatureEngineer()
        self.models = {}
        self.best_model = None
        self.best_model_name = None
        self.best_score = float('inf')
        
        # Setup MLflow
        if mlflow_tracking_uri:
            mlflow.set_tracking_uri(mlflow_tracking_uri)
        mlflow.set_experiment("crop_yield_prediction")
    
    def prepare_data(self, df: pd.DataFrame, test_size: float = 0.2, 
                    val_size: float = 0.1) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, 
                                                   pd.Series, pd.Series, pd.Series]:
        """Prepare data with time-aware splitting"""
        print("Preparing data for training...")
        
        # Sort by year for time-aware splitting
        df = df.sort_values('year')
        
        # Engineer features
        X, y = self.feature_engineer.prepare_features(df, fit=True)
        
        # Time-aware split: use last years for testing
        n_samples = len(df)
        n_test = int(n_samples * test_size)
        n_val = int(n_samples * val_size)
        n_train = n_samples - n_test - n_val
        
        # Split indices
        train_idx = range(n_train)
        val_idx = range(n_train, n_train + n_val)
        test_idx = range(n_train + n_val, n_samples)
        
        # Create splits
        X_train = X.iloc[train_idx]
        X_val = X.iloc[val_idx]
        X_test = X.iloc[test_idx]
        y_train = y.iloc[train_idx]
        y_val = y.iloc[val_idx]
        y_test = y.iloc[test_idx]
        
        print(f"Training set: {X_train.shape}")
        print(f"Validation set: {X_val.shape}")
        print(f"Test set: {X_test.shape}")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def train_xgboost(self, X_train: pd.DataFrame, y_train: pd.Series,
                     X_val: pd.DataFrame, y_val: pd.Series,
                     hyperparameter_tuning: bool = True) -> xgb.XGBRegressor:
        """Train XGBoost model with optional hyperparameter tuning"""
        print("Training XGBoost model...")
        
        with mlflow.start_run(run_name="XGBoost"):
            if hyperparameter_tuning:
                # Hyperparameter grid
                param_grid = {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [3, 5, 7],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'subsample': [0.8, 0.9, 1.0],
                    'colsample_bytree': [0.8, 0.9, 1.0]
                }
                
                # Grid search with cross-validation
                xgb_model = xgb.XGBRegressor(random_state=42, n_jobs=-1)
                grid_search = GridSearchCV(
                    xgb_model, param_grid, cv=3, scoring='neg_mean_squared_error',
                    n_jobs=-1, verbose=1
                )
                grid_search.fit(X_train, y_train)
                
                best_model = grid_search.best_estimator_
                best_params = grid_search.best_params_
                
                print(f"Best XGBoost parameters: {best_params}")
                mlflow.log_params(best_params)
            else:
                # Default parameters
                best_model = xgb.XGBRegressor(
                    n_estimators=200,
                    max_depth=5,
                    learning_rate=0.1,
                    subsample=0.9,
                    colsample_bytree=0.9,
                    random_state=42,
                    n_jobs=-1
                )
                best_model.fit(X_train, y_train)
            
            # Evaluate model
            train_pred = best_model.predict(X_train)
            val_pred = best_model.predict(X_val)
            
            # Calculate metrics
            train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
            val_rmse = np.sqrt(mean_squared_error(y_val, val_pred))
            train_mae = mean_absolute_error(y_train, train_pred)
            val_mae = mean_absolute_error(y_val, val_pred)
            train_r2 = r2_score(y_train, train_pred)
            val_r2 = r2_score(y_val, val_pred)
            
            # Log metrics
            mlflow.log_metrics({
                'train_rmse': train_rmse,
                'val_rmse': val_rmse,
                'train_mae': train_mae,
                'val_mae': val_mae,
                'train_r2': train_r2,
                'val_r2': val_r2
            })
            
            # Log model
            mlflow.xgboost.log_model(best_model, "model")
            
            print(f"XGBoost - Train RMSE: {train_rmse:.4f}, Val RMSE: {val_rmse:.4f}")
            print(f"XGBoost - Train R²: {train_r2:.4f}, Val R²: {val_r2:.4f}")
            
            return best_model
    
    def train_lightgbm(self, X_train: pd.DataFrame, y_train: pd.Series,
                      X_val: pd.DataFrame, y_val: pd.Series,
                      hyperparameter_tuning: bool = True) -> lgb.LGBMRegressor:
        """Train LightGBM model with optional hyperparameter tuning"""
        print("Training LightGBM model...")
        
        with mlflow.start_run(run_name="LightGBM"):
            if hyperparameter_tuning:
                # Hyperparameter grid
                param_grid = {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [3, 5, 7, -1],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'num_leaves': [31, 50, 100],
                    'subsample': [0.8, 0.9, 1.0],
                    'colsample_bytree': [0.8, 0.9, 1.0]
                }
                
                # Grid search with cross-validation
                lgb_model = lgb.LGBMRegressor(random_state=42, n_jobs=-1, verbose=-1)
                grid_search = GridSearchCV(
                    lgb_model, param_grid, cv=3, scoring='neg_mean_squared_error',
                    n_jobs=-1, verbose=1
                )
                grid_search.fit(X_train, y_train)
                
                best_model = grid_search.best_estimator_
                best_params = grid_search.best_params_
                
                print(f"Best LightGBM parameters: {best_params}")
                mlflow.log_params(best_params)
            else:
                # Default parameters
                best_model = lgb.LGBMRegressor(
                    n_estimators=200,
                    max_depth=5,
                    learning_rate=0.1,
                    num_leaves=50,
                    subsample=0.9,
                    colsample_bytree=0.9,
                    random_state=42,
                    n_jobs=-1,
                    verbose=-1
                )
                best_model.fit(X_train, y_train)
            
            # Evaluate model
            train_pred = best_model.predict(X_train)
            val_pred = best_model.predict(X_val)
            
            # Calculate metrics
            train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
            val_rmse = np.sqrt(mean_squared_error(y_val, val_pred))
            train_mae = mean_absolute_error(y_train, train_pred)
            val_mae = mean_absolute_error(y_val, val_pred)
            train_r2 = r2_score(y_train, train_pred)
            val_r2 = r2_score(y_val, val_pred)
            
            # Log metrics
            mlflow.log_metrics({
                'train_rmse': train_rmse,
                'val_rmse': val_rmse,
                'train_mae': train_mae,
                'val_mae': val_mae,
                'train_r2': train_r2,
                'val_r2': val_r2
            })
            
            # Log model
            mlflow.lightgbm.log_model(best_model, "model")
            
            print(f"LightGBM - Train RMSE: {train_rmse:.4f}, Val RMSE: {val_rmse:.4f}")
            print(f"LightGBM - Train R²: {train_r2:.4f}, Val R²: {val_r2:.4f}")
            
            return best_model
    
    def train_random_forest(self, X_train: pd.DataFrame, y_train: pd.Series,
                           X_val: pd.DataFrame, y_val: pd.Series) -> RandomForestRegressor:
        """Train Random Forest baseline model"""
        print("Training Random Forest baseline...")
        
        with mlflow.start_run(run_name="RandomForest"):
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            model.fit(X_train, y_train)
            
            # Evaluate model
            train_pred = model.predict(X_train)
            val_pred = model.predict(X_val)
            
            # Calculate metrics
            train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
            val_rmse = np.sqrt(mean_squared_error(y_val, val_pred))
            train_mae = mean_absolute_error(y_train, train_pred)
            val_mae = mean_absolute_error(y_val, val_pred)
            train_r2 = r2_score(y_train, train_pred)
            val_r2 = r2_score(y_val, val_pred)
            
            # Log metrics
            mlflow.log_metrics({
                'train_rmse': train_rmse,
                'val_rmse': val_rmse,
                'train_mae': train_mae,
                'val_mae': val_mae,
                'train_r2': train_r2,
                'val_r2': val_r2
            })
            
            # Log model
            mlflow.sklearn.log_model(model, "model")
            
            print(f"Random Forest - Train RMSE: {train_rmse:.4f}, Val RMSE: {val_rmse:.4f}")
            print(f"Random Forest - Train R²: {train_r2:.4f}, Val R²: {val_r2:.4f}")
            
            return model
    
    def evaluate_model(self, model: Any, X_test: pd.DataFrame, y_test: pd.Series,
                      model_name: str) -> Dict[str, float]:
        """Evaluate model on test set"""
        print(f"Evaluating {model_name} on test set...")
        
        test_pred = model.predict(X_test)
        
        # Calculate metrics
        test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
        test_mae = mean_absolute_error(y_test, test_pred)
        test_r2 = r2_score(y_test, test_pred)
        
        # Calculate prediction intervals (simple approach using residuals)
        residuals = y_test - test_pred
        std_residual = np.std(residuals)
        
        metrics = {
            'test_rmse': test_rmse,
            'test_mae': test_mae,
            'test_r2': test_r2,
            'prediction_std': std_residual
        }
        
        print(f"{model_name} Test Results:")
        print(f"  RMSE: {test_rmse:.4f}")
        print(f"  MAE: {test_mae:.4f}")
        print(f"  R²: {test_r2:.4f}")
        print(f"  Prediction Std: {std_residual:.4f}")
        
        return metrics
    
    def save_model_artifacts(self, model: Any, model_name: str, feature_names: List[str],
                           metrics: Dict[str, float], output_path: str):
        """Save model and associated artifacts"""
        print(f"Saving {model_name} artifacts...")
        
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Model metadata
        metadata = {
            'model_name': model_name,
            'training_date': datetime.now().isoformat(),
            'feature_names': feature_names,
            'metrics': metrics,
            'model_params': model.get_params() if hasattr(model, 'get_params') else {}
        }
        
        # Save model
        if model_name.lower() == 'xgboost':
            model.save_model(output_path.replace('.json', '.xgb'))
            # Also save as JSON for compatibility
            with open(output_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        else:
            # Save using pickle for other models
            with open(output_path.replace('.json', '.pkl'), 'wb') as f:
                pickle.dump(model, f)
            
            # Save metadata
            with open(output_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        
        # Save feature importance if available
        if hasattr(model, 'feature_importances_'):
            importance_df = create_feature_importance_report(
                feature_names, model.feature_importances_
            )
            importance_df.to_csv(output_path.replace('.json', '_feature_importance.csv'), index=False)
        
        # Save feature engineer
        with open(output_path.replace('.json', '_feature_engineer.pkl'), 'wb') as f:
            pickle.dump(self.feature_engineer, f)
        
        print(f"Model artifacts saved to {output_path}")
    
    def train_all_models(self, df: pd.DataFrame, output_dir: str = 'models',
                        hyperparameter_tuning: bool = True) -> Dict[str, Any]:
        """Train all models and return the best one"""
        print("Starting model training pipeline...")
        
        # Prepare data
        X_train, X_val, X_test, y_train, y_val, y_test = self.prepare_data(df)
        
        # Store feature names
        feature_names = X_train.columns.tolist()
        
        # Train models
        models = {}
        
        # 1. Random Forest (baseline)
        rf_model = self.train_random_forest(X_train, y_train, X_val, y_val)
        models['RandomForest'] = rf_model
        
        # 2. XGBoost
        xgb_model = self.train_xgboost(X_train, y_train, X_val, y_val, hyperparameter_tuning)
        models['XGBoost'] = xgb_model
        
        # 3. LightGBM
        lgb_model = self.train_lightgbm(X_train, y_train, X_val, y_val, hyperparameter_tuning)
        models['LightGBM'] = lgb_model
        
        # Evaluate all models on test set
        best_model = None
        best_model_name = None
        best_rmse = float('inf')
        
        for model_name, model in models.items():
            metrics = self.evaluate_model(model, X_test, y_test, model_name)
            
            # Save model artifacts
            output_path = os.path.join(output_dir, f'{model_name.lower()}_model.json')
            self.save_model_artifacts(model, model_name, feature_names, metrics, output_path)
            
            # Track best model
            if metrics['test_rmse'] < best_rmse:
                best_rmse = metrics['test_rmse']
                best_model = model
                best_model_name = model_name
        
        print(f"\nBest model: {best_model_name} (RMSE: {best_rmse:.4f})")
        
        # Save best model as default
        if best_model:
            best_output_path = os.path.join(output_dir, 'best_model.json')
            best_metrics = self.evaluate_model(best_model, X_test, y_test, best_model_name)
            self.save_model_artifacts(best_model, best_model_name, feature_names, best_metrics, best_output_path)
        
        return {
            'models': models,
            'best_model': best_model,
            'best_model_name': best_model_name,
            'feature_names': feature_names,
            'test_data': (X_test, y_test)
        }

def main():
    parser = argparse.ArgumentParser(description='Train crop yield prediction models')
    parser.add_argument('--in_csv', type=str, required=True, help='Input CSV file with processed data')
    parser.add_argument('--out_model', type=str, default='models/xgb_baseline.json', help='Output model path')
    parser.add_argument('--mlflow_uri', type=str, help='MLflow tracking URI')
    parser.add_argument('--no_tuning', action='store_true', help='Skip hyperparameter tuning')
    parser.add_argument('--model_type', type=str, choices=['xgboost', 'lightgbm', 'all'], 
                       default='all', help='Model type to train')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.in_csv):
        print(f"Error: Input file {args.in_csv} not found.")
        return
    
    # Load data
    print(f"Loading data from {args.in_csv}")
    df = pd.read_csv(args.in_csv)
    print(f"Loaded dataset with shape: {df.shape}")
    
    # Initialize trainer
    trainer = ModelTrainer(mlflow_tracking_uri=args.mlflow_uri)
    
    # Create output directory
    output_dir = os.path.dirname(args.out_model)
    os.makedirs(output_dir, exist_ok=True)
    
    if args.model_type == 'all':
        # Train all models
        results = trainer.train_all_models(
            df, 
            output_dir=output_dir,
            hyperparameter_tuning=not args.no_tuning
        )
        print(f"Training completed. Best model: {results['best_model_name']}")
    else:
        # Train specific model
        X_train, X_val, X_test, y_train, y_val, y_test = trainer.prepare_data(df)
        feature_names = X_train.columns.tolist()
        
        if args.model_type == 'xgboost':
            model = trainer.train_xgboost(X_train, y_train, X_val, y_val, not args.no_tuning)
        elif args.model_type == 'lightgbm':
            model = trainer.train_lightgbm(X_train, y_train, X_val, y_val, not args.no_tuning)
        
        # Evaluate and save
        metrics = trainer.evaluate_model(model, X_test, y_test, args.model_type.upper())
        trainer.save_model_artifacts(model, args.model_type.upper(), feature_names, metrics, args.out_model)
        
        print(f"Model saved to {args.out_model}")

if __name__ == "__main__":
    main()
