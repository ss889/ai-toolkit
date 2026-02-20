#!/usr/bin/env python3
"""
Portfolio Chat - A simple GUI to edit your portfolio by chatting with Ollama.
"""

import json
import re
import subprocess
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from pathlib import Path
import requests

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "consulting-portfolio-helper"
CONTENT_FILE = Path(__file__).parent / "consulting" / "content.json"


class PortfolioChat:
    def __init__(self, root):
        self.root = root
        self.root.title("Portfolio Chat - Consulting Portfolio Helper")
        self.root.geometry("700x600")
        self.root.configure(bg="#1a1a2e")
        
        # Load portfolio
        self.portfolio = self.load_portfolio()
        
        # Create UI
        self.create_widgets()
        
        # Welcome message
        self.add_message("assistant", f"👋 Hi! I'm your Portfolio Assistant.\n\nI can help you edit your consulting portfolio at:\nhttps://ss889.github.io/consulting/\n\nTry saying:\n• 'show my portfolio'\n• 'update my bio to...'\n• 'add a project about...'\n• 'change headline to...'\n• 'remove service [name]'\n\nWhat would you like to change?")
    
    def create_widgets(self):
        # Title
        title = tk.Label(
            self.root,
            text="🎨 Portfolio Chat",
            font=("Segoe UI", 18, "bold"),
            fg="#e94560",
            bg="#1a1a2e"
        )
        title.pack(pady=10)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            bg="#16213e",
            fg="#eee",
            insertbackground="#eee",
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.chat_display.config(state=tk.DISABLED)
        
        # Configure tags for styling
        self.chat_display.tag_config("user", foreground="#4ecca3", font=("Segoe UI", 11, "bold"))
        self.chat_display.tag_config("assistant", foreground="#e94560", font=("Segoe UI", 11, "bold"))
        self.chat_display.tag_config("system", foreground="#ffd700", font=("Segoe UI", 10, "italic"))
        
        # Input frame
        input_frame = tk.Frame(self.root, bg="#1a1a2e")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Input field
        self.input_field = tk.Entry(
            input_frame,
            font=("Segoe UI", 12),
            bg="#16213e",
            fg="#eee",
            insertbackground="#eee",
            relief=tk.FLAT
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))
        self.input_field.bind("<Return>", self.send_message)
        self.input_field.focus()
        
        # Send button
        self.send_btn = tk.Button(
            input_frame,
            text="Send",
            font=("Segoe UI", 11, "bold"),
            bg="#e94560",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=5,
            command=self.send_message
        )
        self.send_btn.pack(side=tk.RIGHT)
        
        # Status bar
        self.status = tk.Label(
            self.root,
            text="Connected to Ollama • Model: consulting-portfolio-helper",
            font=("Segoe UI", 9),
            fg="#666",
            bg="#1a1a2e"
        )
        self.status.pack(pady=5)
    
    def add_message(self, role, content):
        self.chat_display.config(state=tk.NORMAL)
        
        if role == "user":
            self.chat_display.insert(tk.END, "\n👤 You: ", "user")
        elif role == "assistant":
            self.chat_display.insert(tk.END, "\n🤖 Assistant: ", "assistant")
        else:
            self.chat_display.insert(tk.END, "\n⚙️ ", "system")
        
        self.chat_display.insert(tk.END, f"{content}\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def load_portfolio(self):
        try:
            with open(CONTENT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def save_portfolio(self):
        with open(CONTENT_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.portfolio, f, indent=2, ensure_ascii=False)
    
    def push_to_github(self):
        try:
            consulting_dir = CONTENT_FILE.parent
            subprocess.run(["git", "add", "."], cwd=consulting_dir, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Update portfolio via chat"],
                cwd=consulting_dir,
                check=True,
                capture_output=True
            )
            subprocess.run(["git", "push"], cwd=consulting_dir, check=True)
            return True
        except:
            return False
    
    def send_message(self, event=None):
        user_input = self.input_field.get().strip()
        if not user_input:
            return
        
        self.input_field.delete(0, tk.END)
        self.add_message("user", user_input)
        self.send_btn.config(state=tk.DISABLED, text="...")
        self.status.config(text="Thinking...")
        
        # Process in thread
        thread = threading.Thread(target=self.process_message, args=(user_input,))
        thread.start()
    
    def process_message(self, user_input):
        user_lower = user_input.lower()
        
        # Handle show portfolio
        if any(x in user_lower for x in ['show', 'display', 'current', 'view']):
            self.show_portfolio()
            self.reset_ui()
            return
        
        # Handle updates via LLM
        response = self.chat_with_ollama(user_input)
        
        if response:
            # Check for edit commands
            edited = self.process_llm_response(user_input, response)
            
            if edited:
                self.save_portfolio()
                self.root.after(0, lambda: self.add_message("system", "✅ Portfolio updated!"))
                
                if self.push_to_github():
                    self.root.after(0, lambda: self.add_message("system", "📤 Pushed to GitHub! Site updating..."))
                else:
                    self.root.after(0, lambda: self.add_message("system", "⚠️ Could not push to GitHub"))
            
            self.root.after(0, lambda: self.add_message("assistant", response))
        else:
            self.root.after(0, lambda: self.add_message("system", "❌ Could not connect to Ollama"))
        
        self.reset_ui()
    
    def show_portfolio(self):
        p = self.portfolio
        summary = f"""📋 **Current Portfolio**

👤 Name: {p.get('name', 'N/A')}
🎯 Title: {p.get('title', 'N/A')}
💬 Headline: {p.get('headline', 'N/A')}

📝 Bio: {p.get('bio', 'N/A')[:150]}...

🛠️ Services:
"""
        for i, s in enumerate(p.get('services', []), 1):
            summary += f"   {i}. {s.get('title', 'N/A')}\n"
        
        summary += "\n💼 Projects:\n"
        for i, proj in enumerate(p.get('projects', []), 1):
            summary += f"   {i}. {proj.get('title', 'N/A')}\n"
        
        summary += f"\n📧 Email: {p.get('contact', {}).get('email', 'N/A')}"
        
        self.root.after(0, lambda: self.add_message("assistant", summary))
    
    def chat_with_ollama(self, prompt):
        context = f"""You are a portfolio editing assistant. The user wants to modify their consulting portfolio.

Current portfolio data:
- Name: {self.portfolio.get('name', 'Sadikul Saber')}
- Title: {self.portfolio.get('title', '')}
- Headline: {self.portfolio.get('headline', '')}
- Bio: {self.portfolio.get('bio', '')}
- Services: {json.dumps([s.get('title') for s in self.portfolio.get('services', [])])}
- Projects: {json.dumps([p.get('title') for p in self.portfolio.get('projects', [])])}

When the user asks to update content, provide helpful suggestions or confirmations.
For bio/headline changes: Generate professional, engaging content.
For new projects: Suggest a title and description that highlights impact.
For new services: Suggest a title and description that communicates value.

Be concise and helpful. Focus on the task at hand."""

        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL_NAME,
                    "prompt": f"{context}\n\nUser: {prompt}",
                    "stream": False
                },
                timeout=120
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except:
            return None
    
    def process_llm_response(self, user_input, response):
        """Process user input and potentially edit portfolio."""
        user_lower = user_input.lower()
        edited = False
        
        # Update bio
        if 'bio' in user_lower and any(x in user_lower for x in ['update', 'change', 'set', 'make']):
            # Extract new bio from response or generate
            new_bio = self.extract_content(response, 'bio')
            if new_bio and len(new_bio) > 20:
                self.portfolio['bio'] = new_bio
                edited = True
        
        # Update headline
        elif 'headline' in user_lower and any(x in user_lower for x in ['update', 'change', 'set']):
            new_headline = self.extract_content(response, 'headline')
            if new_headline and len(new_headline) > 5:
                self.portfolio['headline'] = new_headline
                edited = True
        
        # Update title
        elif 'title' in user_lower and any(x in user_lower for x in ['update', 'change', 'set']):
            new_title = self.extract_content(response, 'title')
            if new_title and len(new_title) > 2:
                self.portfolio['title'] = new_title
                edited = True
        
        # Add project
        elif 'project' in user_lower and 'add' in user_lower:
            project = self.extract_json(response)
            if project and 'title' in project:
                if 'projects' not in self.portfolio:
                    self.portfolio['projects'] = []
                self.portfolio['projects'].append({
                    'title': project.get('title', ''),
                    'description': project.get('description', ''),
                    'image': 'assets/project.svg'
                })
                edited = True
        
        # Add service
        elif 'service' in user_lower and 'add' in user_lower:
            service = self.extract_json(response)
            if service and 'title' in service:
                if 'services' not in self.portfolio:
                    self.portfolio['services'] = []
                self.portfolio['services'].append({
                    'title': service.get('title', ''),
                    'description': service.get('description', '')
                })
                edited = True
        
        # Remove project
        elif 'project' in user_lower and 'remove' in user_lower:
            match = re.search(r'remove\s+(?:project\s+)?["\']?([^"\']+)["\']?', user_lower)
            if match:
                name = match.group(1).strip()
                original_len = len(self.portfolio.get('projects', []))
                self.portfolio['projects'] = [
                    p for p in self.portfolio.get('projects', [])
                    if name not in p.get('title', '').lower()
                ]
                edited = len(self.portfolio['projects']) < original_len
        
        # Remove service
        elif 'service' in user_lower and 'remove' in user_lower:
            match = re.search(r'remove\s+(?:service\s+)?["\']?([^"\']+)["\']?', user_lower)
            if match:
                name = match.group(1).strip()
                original_len = len(self.portfolio.get('services', []))
                self.portfolio['services'] = [
                    s for s in self.portfolio.get('services', [])
                    if name not in s.get('title', '').lower()
                ]
                edited = len(self.portfolio['services']) < original_len
        
        # Update email
        elif 'email' in user_lower:
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', user_input)
            if email_match:
                if 'contact' not in self.portfolio:
                    self.portfolio['contact'] = {}
                self.portfolio['contact']['email'] = email_match.group()
                edited = True
        
        return edited
    
    def extract_content(self, response, content_type):
        """Extract clean content from LLM response."""
        # Remove common prefixes
        text = response.strip()
        text = re.sub(r'^(here\'s|here is|new|updated|suggested).*?:\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^["\'"]|["\'"]$', '', text.strip())
        
        # For headlines, take first line
        if content_type == 'headline':
            lines = text.split('\n')
            return lines[0].strip().strip('"\'')[:100]
        
        # For bio, take substantial text
        if content_type == 'bio':
            # Remove markdown formatting
            text = re.sub(r'\*\*|\*|##|#', '', text)
            # Take first paragraph if multiple
            paragraphs = text.split('\n\n')
            for p in paragraphs:
                if len(p.strip()) > 50:
                    return p.strip()[:500]
        
        return text[:200] if content_type == 'title' else text[:500]
    
    def extract_json(self, response):
        """Extract JSON from response."""
        # Try code block
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass
        
        # Try raw JSON
        match = re.search(r'\{[^{}]*"title"[^{}]*\}', response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
        
        # Try to construct from response
        title_match = re.search(r'title["\s:]+([^"\n]+)', response, re.IGNORECASE)
        desc_match = re.search(r'description["\s:]+([^"\n]+)', response, re.IGNORECASE)
        
        if title_match:
            return {
                'title': title_match.group(1).strip().strip('"'),
                'description': desc_match.group(1).strip().strip('"') if desc_match else ''
            }
        
        return None
    
    def reset_ui(self):
        self.root.after(0, lambda: self.send_btn.config(state=tk.NORMAL, text="Send"))
        self.root.after(0, lambda: self.status.config(text="Connected to Ollama • Model: consulting-portfolio-helper"))


def main():
    # Check Ollama
    try:
        requests.get("http://localhost:11434/api/tags", timeout=3)
    except:
        messagebox.showwarning("Warning", "Ollama doesn't seem to be running.\nStart it with: ollama serve")
    
    root = tk.Tk()
    app = PortfolioChat(root)
    root.mainloop()


if __name__ == "__main__":
    main()
