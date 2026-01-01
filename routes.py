"""
API routes for diabetes prediction
"""

from flask import Blueprint, request, jsonify
from utils.model_utils import validate_input_features

# Create Blueprint
api = Blueprint('api', __name__, url_prefix='/api')

# Model will be injected by app.py
diabetes_analyzer = None


def init_routes(model):
    """Initialize routes with model instance"""
    global diabetes_analyzer
    diabetes_analyzer = model


@api.route('/predict', methods=['POST'])
def predict_diabetes():
    """
    Predict diabetes based on input features
    
    Expected JSON format:
    {
        "features": {
            "pregnancies": int,
            "glucose": int,
            "blood_pressure": int,
            "skin_thickness": int,
            "insulin": int,
            "bmi": float,
            "diabetes_pedigree": float,
            "age": int
        }
    }
    
    Returns:
        JSON with prediction results or error message
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        features = data.get('features', {})
        
        if not features:
            return jsonify({
                'success': False,
                'error': 'No features provided'
            }), 400
        
        # Validate input features
        is_valid, error_message = validate_input_features(features)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_message
            }), 400
        
        # Make prediction
        result = diabetes_analyzer.predict(features)
        
        # Check for prediction errors
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'model_loaded': diabetes_analyzer is not None
    })
