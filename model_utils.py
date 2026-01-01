"""
Utility functions for model training and management
"""

import os
from models.diabetes_model import DiabetesModel


def train_and_save_model(csv_path=None, model_path='diabetes_model.pkl'):
    """
    Train a new diabetes prediction model and save it
    
    Args:
        csv_path: Path to training data CSV (optional)
        model_path: Path where model should be saved
        
    Returns:
        DiabetesModel instance
    """
    diabetes_model = DiabetesModel()
    
    # Load or create dataset
    if csv_path and os.path.exists(csv_path):
        df = diabetes_model.load_dataset_from_csv(csv_path)
    else:
        df = diabetes_model.create_sample_dataset()
    
    # Train model
    diabetes_model.train(df)
    
    # Save model
    diabetes_model.save_model(model_path)
    
    return diabetes_model


def load_or_train_model(model_path='diabetes_model.pkl', csv_path=None):
    """
    Load existing model or train a new one if not found
    
    Args:
        model_path: Path to saved model
        csv_path: Path to training data (if training needed)
        
    Returns:
        DiabetesModel instance
    """
    diabetes_model = DiabetesModel()
    
    if os.path.exists(model_path):
        print(f"Loading existing model from {model_path}...")
        diabetes_model.load_model(model_path)
    else:
        print(f"Model not found at {model_path}. Training new model...")
        diabetes_model = train_and_save_model(csv_path, model_path)
    
    return diabetes_model


def validate_input_features(features):
    """
    Validate input features for prediction
    
    Args:
        features: Dictionary of feature values
        
    Returns:
        tuple: (is_valid, error_message)
    """
    required_features = [
        'pregnancies', 'glucose', 'blood_pressure', 'skin_thickness',
        'insulin', 'bmi', 'diabetes_pedigree', 'age'
    ]
    
    # Check if all required features are present
    missing_features = [f for f in required_features if f not in features]
    if missing_features:
        return False, f"Missing required features: {', '.join(missing_features)}"
    
    # Validate feature ranges
    validations = {
        'pregnancies': (0, 17, int),
        'glucose': (0, 200, int),
        'blood_pressure': (0, 122, int),
        'skin_thickness': (0, 99, int),
        'insulin': (0, 846, int),
        'bmi': (0, 67.1, float),
        'diabetes_pedigree': (0.0, 2.5, float),
        'age': (21, 81, int)
    }
    
    for feature, (min_val, max_val, dtype) in validations.items():
        try:
            value = dtype(features[feature])
            if not (min_val <= value <= max_val):
                return False, f"{feature} must be between {min_val} and {max_val}"
        except (ValueError, TypeError):
            return False, f"{feature} must be a valid {dtype.__name__}"
    
    return True, None
