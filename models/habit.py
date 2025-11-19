from datetime import datetime

class Habit:
    def __init__(self, id, name, frequency, target_time=None, icon=None, 
                 motivation=None, challenges=None, ai_notes=None, created_at=None):
        self.id = id
        self.name = name
        self.frequency = frequency
        self.target_time = target_time
        self.icon = icon
        self.motivation = motivation
        self.challenges = challenges
        self.ai_notes = ai_notes  # NEW: Additional notes for AI
        self.created_at = created_at or datetime.now()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'frequency': self.frequency,
            'target_time': self.target_time,
            'icon': self.icon,
            'motivation': self.motivation,
            'challenges': self.challenges,
            'ai_notes': self.ai_notes,
            'created_at': self.created_at
        }