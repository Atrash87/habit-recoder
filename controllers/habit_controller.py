from database.db_helper import get_connection
from models.habit import Habit
from models.log import Log
from datetime import datetime, timedelta
import sqlite3

def create_habit(user_id, name, frequency, target_time=None, icon=None, motivation=None, challenges=None, ai_notes=None):
    """Create a new habit for a specific user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO habits (user_id, name, frequency, target_time, icon, motivation, challenges, ai_notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (user_id, name, frequency, target_time, icon, motivation, challenges, ai_notes)
    )
    conn.commit()
    habit_id = cursor.lastrowid
    conn.close()
    return habit_id

def update_habit(habit_id, name, frequency, target_time=None, icon=None, motivation=None, challenges=None, ai_notes=None):
    """Update an existing habit"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE habits SET name=?, frequency=?, target_time=?, icon=?, motivation=?, challenges=?, ai_notes=? WHERE id=?',
        (name, frequency, target_time, icon, motivation, challenges, ai_notes, habit_id)
    )
    conn.commit()
    conn.close()

def get_all_habits(user_id):
    """Get all habits for a specific user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM habits WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    habits = []
    for row in rows:
        habit = Habit(
            id=row['id'],
            name=row['name'],
            frequency=row['frequency'],
            target_time=row['target_time'],
            icon=row['icon'],
            motivation=row['motivation'],
            challenges=row['challenges'],
            ai_notes=row['ai_notes'],
            created_at=row['created_at']
        )
        habits.append(habit)
    return habits

def get_habit_by_id(habit_id):
    """Get a specific habit by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM habits WHERE id = ?', (habit_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return Habit(
            id=row['id'],
            name=row['name'],
            frequency=row['frequency'],
            target_time=row['target_time'],
            icon=row['icon'],
            motivation=row['motivation'],
            challenges=row['challenges'],
            ai_notes=row['ai_notes'],
            created_at=row['created_at']
        )
    return None

def delete_habit(habit_id):
    """Delete a habit"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM habits WHERE id = ?', (habit_id,))
    conn.commit()
    conn.close()

def mark_habit_complete(habit_id, mood=None, note=None):
    """Mark habit as complete for today"""
    today = datetime.now().date()
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO logs (habit_id, completed_date, mood, note) VALUES (?, ?, ?, ?)',
            (habit_id, today, mood, note)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def get_habit_logs(habit_id):
    """Get all completion logs for a habit"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM logs WHERE habit_id = ? ORDER BY completed_date DESC',
        (habit_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    logs = []
    for row in rows:
        log = Log(
            id=row['id'],
            habit_id=row['habit_id'],
            completed_date=row['completed_date'],
            mood=row['mood'],
            note=row['note']
        )
        logs.append(log)
    return logs

def get_habit_streak(habit_id):
    """Calculate current streak for a habit"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT completed_date FROM logs WHERE habit_id = ? ORDER BY completed_date DESC',
        (habit_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return 0
    
    streak = 0
    today = datetime.now().date()
    expected_date = today
    
    for row in rows:
        log_date = datetime.strptime(row['completed_date'], '%Y-%m-%d').date()
        if log_date == expected_date:
            streak += 1
            expected_date -= timedelta(days=1)
        else:
            break
    
    return streak

def is_completed_today(habit_id):
    """Check if habit is completed today"""
    today = datetime.now().date()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM logs WHERE habit_id = ? AND completed_date = ?',
        (habit_id, today)
    )
    row = cursor.fetchone()
    conn.close()
    return row is not None

def get_completion_stats(habit_id):
    """Get completion statistics for a habit"""
    logs = get_habit_logs(habit_id)
    total_completions = len(logs)
    
    if total_completions == 0:
        return {
            'total_completions': 0,
            'completion_rate': 0,
            'current_streak': 0
        }
    
    habit = get_habit_by_id(habit_id)
    days_since_creation = (datetime.now().date() - datetime.strptime(habit.created_at, '%Y-%m-%d %H:%M:%S').date()).days + 1
    completion_rate = (total_completions / days_since_creation) * 100 if days_since_creation > 0 else 0
    
    return {
        'total_completions': total_completions,
        'completion_rate': round(completion_rate, 1),
        'current_streak': get_habit_streak(habit_id)
    }