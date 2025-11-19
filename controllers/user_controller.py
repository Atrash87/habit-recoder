from database.db_helper import get_connection
from models.user import User
from flask_bcrypt import Bcrypt
from config import ADMIN_EMAIL

bcrypt = Bcrypt()

def create_user(email, password):
    """Create a new user with hashed password"""
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    is_admin = (email == ADMIN_EMAIL)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO users (email, password_hash, is_admin) VALUES (?, ?, ?)',
            (email, password_hash, is_admin)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except Exception as e:
        conn.close()
        return None

def get_user_by_email(email):
    """Get user by email"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return User(
            id=row['id'],
            email=row['email'],
            password_hash=row['password_hash'],
            is_admin=bool(row['is_admin']),
            created_at=row['created_at']
        )
    return None

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return User(
            id=row['id'],
            email=row['email'],
            password_hash=row['password_hash'],
            is_admin=bool(row['is_admin']),
            created_at=row['created_at']
        )
    return None

def verify_password(user, password):
    """Verify user password"""
    return bcrypt.check_password_hash(user.password_hash, password)

def get_all_users():
    """Get all users (admin only)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    
    users = []
    for row in rows:
        user = User(
            id=row['id'],
            email=row['email'],
            password_hash=row['password_hash'],
            is_admin=bool(row['is_admin']),
            created_at=row['created_at']
        )
        users.append(user)
    return users

def delete_user(user_id):
    """Delete a user (admin only)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()