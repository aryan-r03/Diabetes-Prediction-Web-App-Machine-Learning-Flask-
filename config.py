"""
Configuration settings for the Diabetes Prediction application
"""

import os

class Config:
    """Base configuration"""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Model settings
    MODEL_PATH = 'diabetes_model.pkl'
    CSV_FILE = 'diabetes.csv'
    
    # Server settings
    HOST = '127.0.0.1'
    PORT = 5000
    
    # CORS settings
    CORS_ENABLED = True


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ENV = 'development'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    ENV = 'production'
    # Add production-specific settings here
    

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
