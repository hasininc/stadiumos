import os
import pickle
import json
import logging
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Features signature
FEATURES = [
    'attendance', 'stadium_capacity', 'match_minute', 'entry_rate_per_min',
    'exit_rate_per_min', 'temperature', 'humidity', 'rain_probability',
    'parking_occupancy', 'metro_arrivals', 'bus_arrivals', 'ticket_scan_rate',
    'security_queue_length', 'food_court_density', 'restroom_density',
    'medical_incidents', 'previous_congestion', 'gate_open_count',
    'vip_event', 'special_event', 'holiday', 'weekday'
]

# Global cache for pipeline artifacts
_ARTIFACTS_CACHE = {}

def get_artifacts() -> Dict[str, Any]:
    """Lazy-load and cache the trained model models and preprocessor pipelines."""
    if not _ARTIFACTS_CACHE:
        logger.info("Loading model artifacts into memory cache...")
        
        models_dir = "/Users/hasininc/StadiumOS/ml/models"
        prep_dir = "/Users/hasininc/StadiumOS/ml/preprocessing"
        
        best_model_path = os.path.join(models_dir, "best_model.pkl")
        queue_model_path = os.path.join(models_dir, "queue_model.pkl")
        preprocessor_path = os.path.join(prep_dir, "preprocessor.pkl")
        label_encoder_path = os.path.join(prep_dir, "label_encoder.pkl")
        
        # Verify file existence before loading
        for p in [best_model_path, queue_model_path, preprocessor_path, label_encoder_path]:
            if not os.path.exists(p):
                raise FileNotFoundError(f"Missing pipeline artifact file at path: {p}")
                
        with open(best_model_path, 'rb') as f:
            best_model = pickle.load(f)
        with open(queue_model_path, 'rb') as f:
            queue_model = pickle.load(f)
        with open(preprocessor_path, 'rb') as f:
            preprocessor = pickle.load(f)
        with open(label_encoder_path, 'rb') as f:
            label_encoder = pickle.load(f)
            
        _ARTIFACTS_CACHE['best_model'] = best_model
        _ARTIFACTS_CACHE['queue_model'] = queue_model
        _ARTIFACTS_CACHE['preprocessor'] = preprocessor
        _ARTIFACTS_CACHE['label_encoder'] = label_encoder
        
        logger.info("Model artifacts loaded successfully.")
        
    return _ARTIFACTS_CACHE

def map_score_to_risk(score: float) -> str:
    if score < 35:
        return "Low"
    elif score < 65:
        return "Medium"
    elif score < 85:
        return "High"
    else:
        return "Critical"

def predict_crowd_congestion(input_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predicts crowd metrics for a single observation dictionary (FastAPI-ready).
    
    Accepts:
        input_json: Dict containing raw features.
        
    Returns:
        Dict with predicted scores, risk labels, and feature contributions.
    """
    artifacts = get_artifacts()
    best_model = artifacts['best_model']
    queue_model = artifacts['queue_model']
    preprocessor = artifacts['preprocessor']
    
    # 1. Map raw input dictionary to pandas DataFrame
    # If variables are missing, they will be filled with NaN and resolved by simple imputer in pipeline
    raw_obs = {}
    for feat in FEATURES:
        raw_obs[feat] = [input_json.get(feat, np.nan)]
        
    df_obs = pd.DataFrame(raw_obs)
    
    # 2. Transform observation via fitted preprocessing pipeline
    processed_obs = preprocessor.transform(df_obs)
    
    # 3. Model inference pass
    pred_score = float(best_model.predict(processed_obs)[0])
    pred_queue = float(queue_model.predict(processed_obs)[0])
    
    # Clip predictions to sensible bounds
    congestion_score = min(100.0, max(0.0, pred_score))
    queue_prediction = min(60.0, max(1.0, pred_queue))
    
    # 4. Determine risk level band
    risk_level = map_score_to_risk(congestion_score)
    
    # Calculate a mock prediction confidence score
    confidence = float(min(99.6, max(70.0, 96.4 - (congestion_score > 80.0) * 8.5)))
    
    # 5. Local Feature Contributions (simulate local explainability)
    # Grab global feature importances and multiply by scaled values to yield contributions
    if hasattr(best_model, 'feature_importances_'):
        global_importances = best_model.feature_importances_
    else:
        global_importances = np.ones(len(FEATURES)) / len(FEATURES)
        
    scaled_values = np.abs(processed_obs[0])
    raw_contributions = scaled_values * global_importances
    total_contribution = np.sum(raw_contributions) if np.sum(raw_contributions) > 0 else 1.0
    normalized_contributions = (raw_contributions / total_contribution) * 100
    
    top_importances = []
    for idx, feature_name in enumerate(FEATURES):
        top_importances.append({
            'feature': feature_name,
            'contribution': float(normalized_contributions[idx])
        })
        
    # Sort by contribution descending
    top_importances = sorted(top_importances, key=lambda x: x['contribution'], reverse=True)[:5]
    
    return {
        'congestion_score': round(congestion_score, 1),
        'risk_level': risk_level,
        'confidence': round(confidence, 1),
        'queue_prediction': round(queue_prediction, 1),
        'top_feature_importance': top_importances
    }

if __name__ == "__main__":
    # Test observation
    sample_obs = {
        'attendance': 75000,
        'stadium_capacity': 80000,
        'match_minute': 10,
        'entry_rate_per_min': 420,
        'exit_rate_per_min': 5,
        'temperature': 28.5,
        'humidity': 75,
        'rain_probability': 0.1,
        'parking_occupancy': 85.0,
        'metro_arrivals': 950,
        'bus_arrivals': 120,
        'ticket_scan_rate': 380,
        'security_queue_length': 180,
        'food_court_density': 65,
        'restroom_density': 40,
        'medical_incidents': 0,
        'previous_congestion': 50,
        'gate_open_count': 16,
        'vip_event': 0,
        'special_event': 0,
        'holiday': 0,
        'weekday': 1
    }
    
    try:
        res = predict_crowd_congestion(sample_obs)
        print("Inference Test Result:")
        print(json.dumps(res, indent=4))
    except Exception as e:
        logger.error(f"Inference run failed: {e}")
