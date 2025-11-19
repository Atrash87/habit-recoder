from database.db_helper import get_connection
from models.journal import JournalEntry
from datetime import datetime
import sqlite3

def create_or_update_journal_entry(user_id, entry_date, content, tags=None):
    """Create or update a journal entry for a specific user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO journal_entries (user_id, entry_date, content, tags) VALUES (?, ?, ?, ?)',
            (user_id, entry_date, content, tags)
        )
    except sqlite3.IntegrityError:
        # Entry exists, update it
        cursor.execute(
            'UPDATE journal_entries SET content=?, tags=?, updated_at=? WHERE user_id=? AND entry_date=?',
            (content, tags, datetime.now(), user_id, entry_date)
        )
    
    conn.commit()
    conn.close()

def get_journal_entry_by_date(user_id, entry_date):
    """Get journal entry for a specific date and user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM journal_entries WHERE user_id = ? AND entry_date = ?', (user_id, entry_date))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return JournalEntry(
            id=row['id'],
            entry_date=row['entry_date'],
            content=row['content'],
            tags=row['tags'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    return None

def get_all_journal_entries(user_id):
    """Get all journal entries for a specific user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM journal_entries WHERE user_id = ? ORDER BY entry_date DESC', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    entries = []
    for row in rows:
        entry = JournalEntry(
            id=row['id'],
            entry_date=row['entry_date'],
            content=row['content'],
            tags=row['tags'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
        entries.append(entry)
    return entries

def search_journal_entries(user_id, search_term):
    """Search journal entries for a specific user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM journal_entries WHERE user_id = ? AND (content LIKE ? OR tags LIKE ?) ORDER BY entry_date DESC',
        (user_id, f'%{search_term}%', f'%{search_term}%')
    )
    rows = cursor.fetchall()
    conn.close()
    
    entries = []
    for row in rows:
        entry = JournalEntry(
            id=row['id'],
            entry_date=row['entry_date'],
            content=row['content'],
            tags=row['tags'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
        entries.append(entry)
    return entries

def get_all_tags(user_id):
    """Get all unique tags for a specific user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT tags FROM journal_entries WHERE user_id = ? AND tags IS NOT NULL', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    all_tags = set()
    for row in rows:
        if row['tags']:
            tags = [tag.strip() for tag in row['tags'].split(',')]
            all_tags.update(tags)
    
    return sorted(list(all_tags))

def delete_journal_entry(user_id, entry_date):
    """Delete a journal entry for a specific user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM journal_entries WHERE user_id = ? AND entry_date = ?', (user_id, entry_date))
    conn.commit()
    conn.close()