import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the app"""
    
    # Telegram Bot settings
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '8149810684:AAGwHuOnuuXt1EEFicGvXgTIx72H7_xCOzg')
    
    # Flask settings
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'default-secret-key-for-development')
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'
    
    # Database settings
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///bot.db')
