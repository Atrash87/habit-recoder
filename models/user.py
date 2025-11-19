from datetime import datetime
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email, password_hash, is_admin=False, created_at=None):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.is_admin = is_admin
        self.created_at = created_at or datetime.now()
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at
        }