import sqlite3
import os
from config import DATABASE_PATH, ADMIN_EMAIL

def get_connection():
    """Create and return a database connection"""
    # Check if running on Render (PostgreSQL)
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Using PostgreSQL on Render
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # Fix Render's postgres:// URL
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        return conn
    else:
        # Using SQLite locally - FIXED: Ensure directory exists
        database_dir = os.path.dirname(DATABASE_PATH)
        if not os.path.exists(database_dir):
            os.makedirs(database_dir, exist_ok=True)
            print(f"📁 Created database directory: {database_dir}")
        
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        
        print(f"🔗 Database connected: {DATABASE_PATH}")
        print(f"🔗 Database file exists: {os.path.exists(DATABASE_PATH)}")
        
        return conn

def init_db():
    """Initialize database with tables"""
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # PostgreSQL initialization (for web version)
        import psycopg2
        
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create habits table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                frequency TEXT NOT NULL,
                target_time TEXT,
                icon TEXT,
                motivation TEXT,
                challenges TEXT,
                ai_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Create logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id SERIAL PRIMARY KEY,
                habit_id INTEGER NOT NULL,
                completed_date DATE NOT NULL,
                mood TEXT,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
                UNIQUE(habit_id, completed_date)
            )
        ''')
        
        # Create journal entries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS journal_entries (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                entry_date DATE NOT NULL,
                content TEXT NOT NULL,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, entry_date)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("PostgreSQL database initialized successfully!")
        
    else:
        # SQLite initialization (local development/desktop) - FIXED
        # Ensure directory exists first
        database_dir = os.path.dirname(DATABASE_PATH)
        if not os.path.exists(database_dir):
            os.makedirs(database_dir, exist_ok=True)
            print(f"📁 Created database directory: {database_dir}")
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create habits table with user_id
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                frequency TEXT NOT NULL,
                target_time TEXT,
                icon TEXT,
                motivation TEXT,
                challenges TEXT,
                ai_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Create logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                completed_date DATE NOT NULL,
                mood TEXT,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
                UNIQUE(habit_id, completed_date)
            )
        ''')
        
        # Create journal entries table with user_id
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS journal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                entry_date DATE NOT NULL,
                content TEXT NOT NULL,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, entry_date)
            )
        ''')
        
        conn.commit()
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📊 Database tables created: {[table[0] for table in tables]}")
        
        conn.close()
        print(f"✅ SQLite database initialized successfully at: {DATABASE_PATH}")
        print(f"✅ Database file size: {os.path.getsize(DATABASE_PATH) if os.path.exists(DATABASE_PATH) else 0} bytes")
    
    print(f"Admin email: {ADMIN_EMAIL}")