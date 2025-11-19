from datetime import datetime

class JournalEntry:
    def __init__(self, id, entry_date, content, tags=None, created_at=None, updated_at=None):
        self.id = id
        self.entry_date = entry_date
        self.content = content
        self.tags = tags  # Comma-separated tags
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def get_tags_list(self):
        """Convert comma-separated tags to list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    def to_dict(self):
        return {
            'id': self.id,
            'entry_date': self.entry_date,
            'content': self.content,
            'tags': self.tags,
            'tags_list': self.get_tags_list(),
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }