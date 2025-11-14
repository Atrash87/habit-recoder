from datetime import datetime

class Log:
    def __init__(self, id, habit_id, completed_date, mood=None, note=None):
        self.id = id
        self.habit_id = habit_id
        self.completed_date = completed_date
        self.mood = mood  # 'happy', 'neutral', 'stressed'
        self.note = note
    
    def to_dict(self):
        return {
            'id': self.id,
            'habit_id': self.habit_id,
            'completed_date': self.completed_date,
            'mood': self.mood,
            'note': self.note
        }