"""Note Taking Tool - Store and retrieve notes"""
import json
from pathlib import Path
from datetime import datetime
from .base_tool import BaseTool


class NoteTakingTool(BaseTool):
    """Tool for taking and managing notes"""
    
    def __init__(self):
        super().__init__(
            name="Note Taking",
            description="Store, organize, retrieve, and manage notes and information.",
            version="1.0"
        )
        self.notes_dir = Path.home() / ".ai_toolkit" / "notes"
        self.notes_dir.mkdir(parents=True, exist_ok=True)
    
    def execute(self, input_text: str) -> str:
        """
        Execute note operations.
        
        Args:
            input_text: Operation in format "ACTION:content" or "ACTION:key|content"
                       Available: SAVE:title|content, GET:title, LIST, DELETE:title
            
        Returns:
            Operation result
        """
        command = input_text.strip()
        
        if not command:
            return "Please specify a note operation.\nFormat: SAVE:title|content, GET:title, LIST, DELETE:title"
        
        if ':' not in command:
            return "Invalid format. Use ACTION:parameters"
        
        action, params = command.split(':', 1)
        action = action.strip().upper()
        params = params.strip()
        
        if action == "SAVE":
            return self._save_note(params)
        elif action == "GET":
            return self._get_note(params)
        elif action == "LIST":
            return self._list_notes()
        elif action == "DELETE":
            return self._delete_note(params)
        else:
            return f"Unknown action: {action}\nAvailable: SAVE, GET, LIST, DELETE"
    
    def _save_note(self, params: str) -> str:
        """Save a note"""
        if '|' not in params:
            return "Format: SAVE:title|content"
        
        title, content = params.split('|', 1)
        title = title.strip()
        content = content.strip()
        
        if not title or not content:
            return "Title and content cannot be empty"
        
        note_file = self.notes_dir / f"{title}.json"
        
        note_data = {
            "title": title,
            "content": content,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat()
        }
        
        with open(note_file, 'w') as f:
            json.dump(note_data, f, indent=2)
        
        return f"Note '{title}' saved successfully!"
    
    def _get_note(self, title: str) -> str:
        """Retrieve a note"""
        title = title.strip()
        note_file = self.notes_dir / f"{title}.json"
        
        if not note_file.exists():
            return f"Note '{title}' not found."
        
        with open(note_file, 'r') as f:
            note_data = json.load(f)
        
        return f"Title: {note_data['title']}\n\n{note_data['content']}\n\n(Modified: {note_data['modified']})"
    
    def _list_notes(self) -> str:
        """List all notes"""
        notes = list(self.notes_dir.glob("*.json"))
        
        if not notes:
            return "No notes found."
        
        note_list = "Your Notes:\n" + "="*40 + "\n\n"
        
        for note_file in sorted(notes, key=lambda x: x.stat().st_mtime, reverse=True):
            with open(note_file, 'r') as f:
                note_data = json.load(f)
            
            preview = note_data['content'][:100]
            if len(note_data['content']) > 100:
                preview += "..."
            
            note_list += f"• {note_data['title']}\n"
            note_list += f"  {preview}\n"
            note_list += f"  Modified: {note_data['modified']}\n\n"
        
        return note_list
    
    def _delete_note(self, title: str) -> str:
        """Delete a note"""
        title = title.strip()
        note_file = self.notes_dir / f"{title}.json"
        
        if not note_file.exists():
            return f"Note '{title}' not found."
        
        note_file.unlink()
        return f"Note '{title}' deleted successfully!"
    
    def get_system_prompt(self) -> str:
        """Get system prompt for note taking tool"""
        return """You are a helpful note-taking assistant. You can help users:

1. Save important information and notes
2. Retrieve previously saved notes
3. Organize and manage their personal knowledge base
4. Keep track of ideas and information

Available note operations:
- SAVE:title|content - Save a new note
- GET:title - Retrieve a note by title
- LIST - Show all notes
- DELETE:title - Delete a note by title

When helping users with notes:
- Suggest organizing information in clear, structured ways
- Offer to save summaries of important information
- Help retrieve relevant notes when asked
- Suggest creating notes for future reference

Make note titles clear and descriptive so they're easy to find later.
Keep note content concise but comprehensive."""
