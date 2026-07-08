import os
import pickle
import json
import time
import logging
from typing import Dict, Any
import numpy as np

# Model classes
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor

# Evaluation helper
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def train_and_compare_models(
    preprocessed_data: Dict[str, Any],
    models_dir: str = "/Users/hasininc/StadiumOS/ml/models"
) -> Dict[str, Any]:
    logger.info("Starting model training and comparison...")
    
    # Extract datasets
    X_train = preprocessed_data['X_train']
    X_test = preprocessed_data['X_test']
    y_train = preprocessed_data['y_train_cong']
    y_test = preprocessed_data['y_test_cong']
    
    # Sub-sample for extremely fast training in container environment (20k training rows)
    sample_size = min(20000, len(X_train))
    indices = np.random.choice(len(X_train), size=sample_size, replace=False)
    X_train_sub = X_train[indices]
    y_train_sub = y_train[indices]
    
    # Define models with fast training parameters
    models = {
        'RandomForest': RandomForestRegressor(n_estimators=30, max_depth=6, random_state=42, n_jobs=-1),
        'XGBoost': XGBRegressor(n_estimators=50, max_depth=5, learning_rate=0.15, random_state=42, n_jobs=-1),
        'LightGBM': LGBMRegressor(n_estimators=60, max_depth=5, learning_rate=0.15, random_state=42, verbosity=-1, n_jobs=-1),
        'CatBoost': CatBoostRegressor(iterations=60, depth=5, learning_rate=0.15, random_state=42, verbose=0),
        'GradientBoosting': GradientBoostingRegressor(n_estimators=30, max_depth=5, random_state=42),
        'ExtraTrees': ExtraTreesRegressor(n_estimators=30, max_depth=6, random_state=42, n_jobs=-1)
    }
    
    comparison_results = {}
    best_algorithm = None
    best_rmse = float('inf')
    best_model_obj = None
    
    for name, model in models.items():
        logger.info(f"Training {name}...")
        start_time = time.time()
        
        # Fit model on sample
        model.fit(X_train_sub, y_train_sub)
        duration = time.time() - start_time
        
        # Predict on validation split
        preds = model.predict(X_test)
        
        # Calculate metrics
        mae = mean_absolute_error(y_test, preds)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        r2 = r2_score(y_test, preds)
        
        comparison_results[name] = {
            'MAE': float(mae),
            'RMSE': float(rmse),
            'R2': float(r2),
            'training_time_sec': float(duration)
        }
        
        logger.info(f"{name} -> RMSE: {rmse:.4f}, MAE: {mae:.4f}, R2: {r2:.4f} (Fit Time: {duration:.2f}s)")
        
        if rmse < best_rmse:
            best_rmse = rmse
            best_algorithm = name
            best_model_obj = model

    logger.info(f"Champion algorithm selected: {best_algorithm} with validation RMSE {best_rmse:.4f}")
    
    # Train queue time prediction model using the champion algorithm type
    logger.info("Training secondary Queue Time prediction model...")
    y_train_q = preprocessed_data['y_train_queue'][indices]
    
    # Create fresh clone of the champion model architecture
    if best_algorithm == 'RandomForest':
        q_model = RandomForestRegressor(n_estimators=30, max_depth=6, random_state=42, n_jobs=-1)
    elif best_algorithm == 'XGBoost':
        q_model = XGBRegressor(n_estimators=50, max_depth=5, learning_rate=0.15, random_state=42, n_jobs=-1)
    elif best_algorithm == 'LightGBM':
        q_model = LGBMRegressor(n_estimators=60, max_depth=5, learning_rate=0.15, random_state=42, verbosity=-1, n_jobs=-1)
    elif best_algorithm == 'CatBoost':
        q_model = CatBoostRegressor(iterations=60, depth=5, learning_rate=0.15, random_state=42, verbose=0)
    elif best_algorithm == 'GradientBoosting':
        q_model = GradientBoostingRegressor(n_estimators=30, max_depth=5, random_state=42)
    else:
        q_model = ExtraTreesRegressor(n_estimators=30, max_depth=6, random_state=42, n_jobs=-1)
        
    q_model.fit(X_train_sub, y_train_q)
    
    # Ensure directory exists
    os.makedirs(models_dir, exist_ok=True)
    
    # Save artifacts
    best_model_path = os.path.join(models_dir, "best_model.pkl")
    q_model_path = os.path.join(models_dir, "queue_model.pkl")
    metadata_path = os.path.join(models_dir, "metadata.json")
    
    with open(best_model_path, 'wb') as f:
        pickle.dump(best_model_obj, f)
        
    with open(q_model_path, 'wb') as f:
        pickle.dump(q_model, f)
        
    metadata = {
        'champion_model': best_algorithm,
        'metrics_comparison': comparison_results,
        'trained_at': time.strftime("%Y-%m-%d %H:%M:%S"),
        'train_samples': len(X_train_sub),
        'features_count': X_train.shape[1]
    }
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4)
        
    logger.info(f"Models and metadata written to {models_dir} successfully.")
    
    return {
        'best_model': best_model_obj,
        'queue_model': q_model,
        'metadata': metadata
    }

if __name__ == "__main__":
    from ml.preprocessing.pipeline import preprocess_dataset
    data = preprocess_dataset()
    train_and_compare_models(data)
