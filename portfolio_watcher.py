#!/usr/bin/env python3
"""
Portfolio Watcher - Background service that executes commands from Ollama.

How it works:
1. You chat with consulting-portfolio-helper in Ollama desktop app
2. When you want to edit something, the model outputs a command like:
   [PORTFOLIO_EDIT: bio | Your new bio text here]
3. You copy the model's response (Ctrl+C)
4. This watcher detects the command and executes it automatically
5. Changes are saved and pushed to GitHub

Run this in the background:
    pythonw portfolio_watcher.py
    
Or with console output:
    python portfolio_watcher.py
"""

import json
import re
import subprocess
import time
import threading
from pathlib import Path
from datetime import datetime

try:
    import win32clipboard
    import win32api
    import win32con
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

# Configuration
CONTENT_FILE = Path(__file__).parent / "consulting" / "content.json"
CHECK_INTERVAL = 0.5  # seconds
LOG_FILE = Path(__file__).parent / "watcher.log"

# Command patterns the LLM will output
COMMAND_PATTERNS = {
    'bio': r'\[PORTFOLIO_EDIT:\s*bio\s*\|\s*(.+?)\]',
    'headline': r'\[PORTFOLIO_EDIT:\s*headline\s*\|\s*(.+?)\]',
    'title': r'\[PORTFOLIO_EDIT:\s*title\s*\|\s*(.+?)\]',
    'email': r'\[PORTFOLIO_EDIT:\s*email\s*\|\s*(.+?)\]',
    'add_project': r'\[PORTFOLIO_ADD:\s*project\s*\|\s*(.+?)\s*\|\s*(.+?)\]',
    'add_service': r'\[PORTFOLIO_ADD:\s*service\s*\|\s*(.+?)\s*\|\s*(.+?)\]',
    'remove_project': r'\[PORTFOLIO_REMOVE:\s*project\s*\|\s*(.+?)\]',
    'remove_service': r'\[PORTFOLIO_REMOVE:\s*service\s*\|\s*(.+?)\]',
}


def log(message):
    """Log message to console and file."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + "\n")
    except:
        pass


def load_portfolio():
    """Load portfolio from JSON file."""
    try:
        with open(CONTENT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log(f"Error loading portfolio: {e}")
        return None


def save_portfolio(content):
    """Save portfolio to JSON file."""
    try:
        with open(CONTENT_FILE, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        log(f"Error saving portfolio: {e}")
        return False


def push_to_github():
    """Push changes to GitHub."""
    try:
        consulting_dir = CONTENT_FILE.parent
        subprocess.run(["git", "add", "."], cwd=consulting_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Update portfolio via Ollama"],
            cwd=consulting_dir, check=True, capture_output=True
        )
        subprocess.run(["git", "push"], cwd=consulting_dir, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def show_notification(title, message):
    """Show Windows notification."""
    try:
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        toaster.show_toast(title, message, duration=3, threaded=True)
    except:
        # Fallback: just log
        log(f"NOTIFICATION: {title} - {message}")


def get_clipboard():
    """Get clipboard content."""
    if HAS_WIN32:
        try:
            win32clipboard.OpenClipboard()
            try:
                data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                return data
            except:
                return ""
            finally:
                win32clipboard.CloseClipboard()
        except:
            return ""
    else:
        # Fallback using subprocess
        try:
            result = subprocess.run(
                ["powershell", "-command", "Get-Clipboard"],
                capture_output=True, text=True, timeout=2
            )
            return result.stdout
        except:
            return ""


def process_commands(text):
    """Process commands found in text."""
    portfolio = load_portfolio()
    if not portfolio:
        return False
    
    changed = False
    
    # Check for bio update
    match = re.search(COMMAND_PATTERNS['bio'], text, re.DOTALL | re.IGNORECASE)
    if match:
        new_bio = match.group(1).strip()
        portfolio['bio'] = new_bio
        log(f"✓ Updated bio: {new_bio[:50]}...")
        changed = True
    
    # Check for headline update
    match = re.search(COMMAND_PATTERNS['headline'], text, re.DOTALL | re.IGNORECASE)
    if match:
        new_headline = match.group(1).strip()
        portfolio['headline'] = new_headline
        log(f"✓ Updated headline: {new_headline}")
        changed = True
    
    # Check for title update
    match = re.search(COMMAND_PATTERNS['title'], text, re.DOTALL | re.IGNORECASE)
    if match:
        new_title = match.group(1).strip()
        portfolio['title'] = new_title
        log(f"✓ Updated title: {new_title}")
        changed = True
    
    # Check for email update
    match = re.search(COMMAND_PATTERNS['email'], text, re.DOTALL | re.IGNORECASE)
    if match:
        new_email = match.group(1).strip()
        if 'contact' not in portfolio:
            portfolio['contact'] = {}
        portfolio['contact']['email'] = new_email
        log(f"✓ Updated email: {new_email}")
        changed = True
    
    # Check for add project
    match = re.search(COMMAND_PATTERNS['add_project'], text, re.DOTALL | re.IGNORECASE)
    if match:
        title = match.group(1).strip()
        description = match.group(2).strip()
        if 'projects' not in portfolio:
            portfolio['projects'] = []
        portfolio['projects'].append({
            'title': title,
            'description': description,
            'image': 'assets/project.svg'
        })
        log(f"✓ Added project: {title}")
        changed = True
    
    # Check for add service
    match = re.search(COMMAND_PATTERNS['add_service'], text, re.DOTALL | re.IGNORECASE)
    if match:
        title = match.group(1).strip()
        description = match.group(2).strip()
        if 'services' not in portfolio:
            portfolio['services'] = []
        portfolio['services'].append({
            'title': title,
            'description': description
        })
        log(f"✓ Added service: {title}")
        changed = True
    
    # Check for remove project
    match = re.search(COMMAND_PATTERNS['remove_project'], text, re.DOTALL | re.IGNORECASE)
    if match:
        name = match.group(1).strip().lower()
        original = len(portfolio.get('projects', []))
        portfolio['projects'] = [
            p for p in portfolio.get('projects', [])
            if name not in p.get('title', '').lower()
        ]
        if len(portfolio['projects']) < original:
            log(f"✓ Removed project matching: {name}")
            changed = True
    
    # Check for remove service
    match = re.search(COMMAND_PATTERNS['remove_service'], text, re.DOTALL | re.IGNORECASE)
    if match:
        name = match.group(1).strip().lower()
        original = len(portfolio.get('services', []))
        portfolio['services'] = [
            s for s in portfolio.get('services', [])
            if name not in s.get('title', '').lower()
        ]
        if len(portfolio['services']) < original:
            log(f"✓ Removed service matching: {name}")
            changed = True
    
    if changed:
        if save_portfolio(portfolio):
            log("✓ Portfolio saved")
            if push_to_github():
                log("✓ Pushed to GitHub!")
                show_notification("Portfolio Updated", "Changes pushed to GitHub")
            else:
                log("⚠ Could not push to GitHub (no changes or error)")
        else:
            log("✗ Failed to save portfolio")
    
    return changed


def main():
    """Main watcher loop."""
    print("=" * 50)
    print("🔍 PORTFOLIO WATCHER")
    print("=" * 50)
    print("\nWatching clipboard for Ollama commands...")
    print("Chat with consulting-portfolio-helper in Ollama,")
    print("then copy (Ctrl+C) the response to execute commands.")
    print("\nCommands the model can output:")
    print("  [PORTFOLIO_EDIT: bio | Your new bio here]")
    print("  [PORTFOLIO_EDIT: headline | Your new headline]")
    print("  [PORTFOLIO_EDIT: title | Your new title]")
    print("  [PORTFOLIO_EDIT: email | your@email.com]")
    print("  [PORTFOLIO_ADD: project | Title | Description]")
    print("  [PORTFOLIO_ADD: service | Title | Description]")
    print("  [PORTFOLIO_REMOVE: project | project name]")
    print("  [PORTFOLIO_REMOVE: service | service name]")
    print("\nPress Ctrl+C to stop.")
    print("-" * 50)
    
    last_clipboard = ""
    
    while True:
        try:
            current = get_clipboard()
            
            # Check if clipboard changed and contains commands
            if current and current != last_clipboard:
                if '[PORTFOLIO_' in current:
                    log("📋 Detected portfolio command in clipboard!")
                    process_commands(current)
                last_clipboard = current
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n👋 Watcher stopped.")
            break
        except Exception as e:
            log(f"Error: {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()
