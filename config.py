import os

# Base directory of the app
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Database configuration
DATABASE_PATH = os.path.join(BASE_DIR, 'habit_tracker.db')

# Flask configuration
SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-12345'
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Admin configuration
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'hasan.alatrash87@gmail.com'

# App configuration
APP_NAME = 'Habit Re:coder'

# Production check
IS_PRODUCTION = os.environ.get('RENDER') is not None

APP_VERSION = "1.0.0"