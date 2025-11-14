import os
from urllib.parse import urlparse

def get_database_url():
    """Get database URL from environment or use SQLite for local"""
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Render uses postgres:// but SQLAlchemy needs postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url
    
    # Local development - use SQLite
    from config import DATABASE_PATH
    return f'sqlite:///{DATABASE_PATH}'

def is_postgres():
    """Check if using PostgreSQL"""
    return os.environ.get('DATABASE_URL') is not None