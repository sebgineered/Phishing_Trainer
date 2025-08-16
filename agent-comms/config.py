import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration settings for the application."""
    
    # API Keys
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    JENTIC_API_KEY = os.getenv('JENTIC_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Email Settings
    EMAIL_SENDER = os.getenv('EMAIL_SENDER')
    
    # Database Settings
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Application Settings
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Phishing Campaign Settings
    DEFAULT_DIFFICULTY = 3  # Scale of 1-5
    MAX_EMAILS_PER_CAMPAIGN = 100
    
    # Training Settings
    TRAINING_DELAY_MINUTES = 5  # Time to wait before sending training after click
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present."""
        required_vars = [
            'SENDGRID_API_KEY',
            'EMAIL_SENDER',
            'JENTIC_API_KEY',
            'OPENAI_API_KEY'
        ]
        
        missing = [var for var in required_vars if getattr(cls, var) is None]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True