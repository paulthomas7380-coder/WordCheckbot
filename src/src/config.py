import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("No TELEGRAM_TOKEN found in environment variables!")

# Language settings
LANGUAGE = os.getenv("LANGUAGE", "en")

# Available languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'nl': 'Dutch',
    'ru': 'Russian',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'zh': 'Chinese',
    'ja': 'Japanese'
}

# Bot settings
MAX_TEXT_LENGTH = 4096  # Telegram message limit
DEFAULT_LANGUAGE = 'en'

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
