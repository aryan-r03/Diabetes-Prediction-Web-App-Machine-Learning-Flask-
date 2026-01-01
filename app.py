"""
Flask Application for Diabetes Prediction
Main entry point for the web application
"""

import os
from flask import Flask, render_template
from flask_cors import CORS
from config.config import config
from routes import api, init_routes
from utils.model_utils import load_or_train_model


def create_app(config_name='development'):
    """
    Application factory function
    
    Args:
        config_name: Configuration to use (development/production/testing)
        
    Returns:
        Flask application instance
    """
    # Initialize Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Enable CORS
    if app.config['CORS_ENABLED']:
        CORS(app)
    
    # Load or train model
    model_path = app.config['MODEL_PATH']
    csv_path = app.config['CSV_FILE']
    
    print("\n" + "=" * 60)
    print("INITIALIZING DIABETES PREDICTION APPLICATION")
    print("=" * 60)
    
    diabetes_model = load_or_train_model(
        model_path=model_path,
        csv_path=csv_path if os.path.exists(csv_path) else None
    )
    
    # Initialize routes with model
    init_routes(diabetes_model)
    
    # Register blueprints
    app.register_blueprint(api)
    
    # Home route
    @app.route('/')
    def home():
        """Render the main application page"""
        return render_template('index.html')
    
    print("\n✓ Application initialized successfully")
    print("=" * 60)
    
    return app


if __name__ == '__main__':
    # Get configuration from environment or use default
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create application
    app = create_app(config_name)
    
    # Get host and port from config
    host = app.config.get('HOST', '127.0.0.1')
    port = app.config.get('PORT', 5000)
    debug = app.config.get('DEBUG', False)
    
    # Print startup message
    print("\n" + "=" * 60)
    print("STARTING FLASK SERVER")
    print("=" * 60)
    print(f"\n🌐 Server running at: http://{host}:{port}")
    print(f"📊 Environment: {config_name}")
    print(f"🔧 Debug mode: {'ON' if debug else 'OFF'}")
    print("\nPress CTRL+C to quit\n")
    
    # Run application
    app.run(host=host, port=port, debug=debug)
