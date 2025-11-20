import os
import sys

# Base directory of the app
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# FIXED: Database path - use persistent location for desktop app
if getattr(sys, 'frozen', False):
    # Running as compiled executable (.exe)
    if os.name == 'nt':  # Windows
        # Use AppData/Local for better persistence
        APP_DATA_DIR = os.path.join(os.environ['LOCALAPPDATA'], 'HabitRecoder')
    elif os.name == 'posix':  # Mac/Linux
        APP_DATA_DIR = os.path.join(os.path.expanduser('~'), '.habitrecoder')
    else:
        APP_DATA_DIR = BASE_DIR
else:
    # Running as script (development)
    APP_DATA_DIR = BASE_DIR

# Create app data directory if it doesn't exist
os.makedirs(APP_DATA_DIR, exist_ok=True)

# Database configuration - FIXED: Use persistent location
DATABASE_PATH = os.path.join(APP_DATA_DIR, 'habit_tracker.db')

print(f"🚀 DEBUG: Database will be stored at: {DATABASE_PATH}")
print(f"🚀 DEBUG: App data directory: {APP_DATA_DIR}")
print(f"🚀 DEBUG: Directory exists: {os.path.exists(APP_DATA_DIR)}")

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