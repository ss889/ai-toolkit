#!/usr/bin/env python3
"""
Portfolio Manager - Edit your consulting portfolio by chatting with Ollama.

Usage:
    python portfolio_manager.py

Commands you can use:
    - "update my bio to ..."
    - "add a new project called ..."
    - "change my headline to ..."
    - "add a service about ..."
    - "update my email to ..."
    - "show my current portfolio"
    - "list my projects"
    - "remove project [name]"
    - "quit" or "exit"
"""

import json
import os
import re
import subprocess
import requests
from pathlib import Path

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "web-search-helper"
CONTENT_FILE = Path(__file__).parent / "consulting" / "content.json"


def load_portfolio():
    """Load the current portfolio content."""
    with open(CONTENT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_portfolio(content):
    """Save the portfolio content to file."""
    with open(CONTENT_FILE, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
    print("\n✅ Portfolio updated and saved!")


def push_to_github(message="Update portfolio via Ollama"):
    """Push changes to GitHub."""
    consulting_dir = CONTENT_FILE.parent
    
    try:
        # Check if there are changes to commit
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=consulting_dir,
            capture_output=True,
            text=True
        )
        
        if not result.stdout.strip():
            print("\n📝 No changes to push.")
            return True
        
        # Stage changes
        subprocess.run(
            ["git", "add", "."],
            cwd=consulting_dir,
            check=True
        )
        
        # Commit
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=consulting_dir,
            check=True,
            capture_output=True
        )
        
        # Push
        print("\n📤 Pushing to GitHub...")
        subprocess.run(
            ["git", "push"],
            cwd=consulting_dir,
            check=True
        )
        
        print("✅ Changes pushed to GitHub!")
        print("🌐 Site will update at: https://ss889.github.io/consulting/")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Git error: {e}")
        return False
    except FileNotFoundError:
        print("\n❌ Git not found. Please install Git.")
        return False


def chat_with_ollama(prompt, system_context=""):
    """Send a prompt to Ollama and get the response."""
    full_prompt = f"{system_context}\n\nUser request: {prompt}" if system_context else prompt
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": full_prompt,
                "stream": False
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to Ollama: {e}")
        return None


def extract_json_from_response(response):
    """Extract JSON from LLM response if present."""
    # Try to find JSON in code blocks
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try to find raw JSON object
    json_match = re.search(r'\{[^{}]*"[^"]+"\s*:\s*[^{}]+\}', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    
    return None


def show_portfolio_summary(content):
    """Display a summary of the current portfolio."""
    print("\n" + "="*60)
    print("📋 CURRENT PORTFOLIO")
    print("="*60)
    print(f"\n👤 Name: {content.get('name', 'N/A')}")
    print(f"🎯 Title: {content.get('title', 'N/A')}")
    print(f"💬 Headline: {content.get('headline', 'N/A')}")
    print(f"\n📝 Bio: {content.get('bio', 'N/A')[:100]}...")
    
    print("\n🛠️  Services:")
    for i, service in enumerate(content.get('services', []), 1):
        print(f"   {i}. {service.get('title', 'N/A')}")
    
    print("\n💼 Projects:")
    for i, project in enumerate(content.get('projects', []), 1):
        print(f"   {i}. {project.get('title', 'N/A')}")
    
    print(f"\n📧 Email: {content.get('contact', {}).get('email', 'N/A')}")
    print("="*60)


def update_bio(content, new_bio):
    """Update the bio field."""
    content['bio'] = new_bio
    return content


def update_headline(content, new_headline):
    """Update the headline field."""
    content['headline'] = new_headline
    return content


def update_title(content, new_title):
    """Update the title field."""
    content['title'] = new_title
    return content


def update_email(content, new_email):
    """Update the email field."""
    if 'contact' not in content:
        content['contact'] = {}
    content['contact']['email'] = new_email
    return content


def add_service(content, title, description):
    """Add a new service."""
    if 'services' not in content:
        content['services'] = []
    content['services'].append({
        'title': title,
        'description': description
    })
    return content


def add_project(content, title, description, image="assets/project.svg"):
    """Add a new project."""
    if 'projects' not in content:
        content['projects'] = []
    content['projects'].append({
        'title': title,
        'description': description,
        'image': image
    })
    return content


def remove_project(content, project_name):
    """Remove a project by name (case-insensitive partial match)."""
    original_count = len(content.get('projects', []))
    content['projects'] = [
        p for p in content.get('projects', [])
        if project_name.lower() not in p.get('title', '').lower()
    ]
    removed = original_count - len(content['projects'])
    return content, removed


def remove_service(content, service_name):
    """Remove a service by name (case-insensitive partial match)."""
    original_count = len(content.get('services', []))
    content['services'] = [
        s for s in content.get('services', [])
        if service_name.lower() not in s.get('title', '').lower()
    ]
    removed = original_count - len(content['services'])
    return content, removed


def process_command(user_input, content):
    """Process user command and update portfolio."""
    user_input_lower = user_input.lower().strip()
    
    # Show current portfolio
    if any(x in user_input_lower for x in ['show', 'display', 'current', 'list']):
        show_portfolio_summary(content)
        return content, False
    
    # Update bio
    if 'bio' in user_input_lower and any(x in user_input_lower for x in ['update', 'change', 'set', 'make']):
        print("\n🤖 Generating new bio content...")
        system_context = f"""Current bio: {content.get('bio', '')}
        
The user wants to update their portfolio bio. Generate a professional, engaging bio based on their request.
Return ONLY the new bio text, nothing else. Keep it concise (2-3 sentences)."""
        
        response = chat_with_ollama(user_input, system_context)
        if response:
            # Clean up the response
            new_bio = response.strip().strip('"').strip()
            if len(new_bio) > 20:  # Sanity check
                print(f"\n📝 New bio:\n{new_bio}")
                confirm = input("\nApply this change? (y/n): ").strip().lower()
                if confirm == 'y':
                    content = update_bio(content, new_bio)
                    return content, True
        return content, False
    
    # Update headline
    if 'headline' in user_input_lower and any(x in user_input_lower for x in ['update', 'change', 'set', 'make']):
        print("\n🤖 Generating new headline...")
        system_context = f"""Current headline: {content.get('headline', '')}
        
Generate a compelling, professional headline for an AI consultant based on the user's request.
Return ONLY the headline text, nothing else. Keep it under 15 words."""
        
        response = chat_with_ollama(user_input, system_context)
        if response:
            new_headline = response.strip().strip('"').strip()
            if len(new_headline) > 5:
                print(f"\n📝 New headline: {new_headline}")
                confirm = input("\nApply this change? (y/n): ").strip().lower()
                if confirm == 'y':
                    content = update_headline(content, new_headline)
                    return content, True
        return content, False
    
    # Update title
    if 'title' in user_input_lower and any(x in user_input_lower for x in ['update', 'change', 'set', 'make']):
        print("\n🤖 Generating new title...")
        system_context = """Generate a professional job title based on the user's request.
Return ONLY the title text (2-5 words), nothing else."""
        
        response = chat_with_ollama(user_input, system_context)
        if response:
            new_title = response.strip().strip('"').strip()
            if len(new_title) > 2:
                print(f"\n📝 New title: {new_title}")
                confirm = input("\nApply this change? (y/n): ").strip().lower()
                if confirm == 'y':
                    content = update_title(content, new_title)
                    return content, True
        return content, False
    
    # Update email
    if 'email' in user_input_lower and any(x in user_input_lower for x in ['update', 'change', 'set']):
        # Extract email from the input
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', user_input)
        if email_match:
            new_email = email_match.group()
            print(f"\n📝 New email: {new_email}")
            confirm = input("\nApply this change? (y/n): ").strip().lower()
            if confirm == 'y':
                content = update_email(content, new_email)
                return content, True
        else:
            print("❌ No valid email found in your message.")
        return content, False
    
    # Add project
    if 'project' in user_input_lower and 'add' in user_input_lower:
        print("\n🤖 Generating project details...")
        system_context = """Generate a portfolio project based on the user's request.
Return a JSON object with exactly these fields:
{
  "title": "Project Title",
  "description": "2-3 sentence description of the project, its impact, and technologies used."
}
Return ONLY the JSON, no other text."""
        
        response = chat_with_ollama(user_input, system_context)
        if response:
            project_data = extract_json_from_response(response)
            if not project_data:
                # Try parsing the whole response as JSON
                try:
                    project_data = json.loads(response.strip())
                except:
                    pass
            
            if project_data and 'title' in project_data:
                print(f"\n📝 New project:")
                print(f"   Title: {project_data['title']}")
                print(f"   Description: {project_data.get('description', 'N/A')}")
                confirm = input("\nAdd this project? (y/n): ").strip().lower()
                if confirm == 'y':
                    content = add_project(
                        content,
                        project_data['title'],
                        project_data.get('description', '')
                    )
                    return content, True
            else:
                print("❌ Couldn't parse project details. Try being more specific.")
        return content, False
    
    # Remove project
    if 'project' in user_input_lower and 'remove' in user_input_lower:
        # Extract project name
        match = re.search(r'remove\s+(?:project\s+)?["\']?([^"\']+)["\']?', user_input_lower)
        if match:
            project_name = match.group(1).strip()
            content, removed = remove_project(content, project_name)
            if removed > 0:
                print(f"✅ Removed {removed} project(s) matching '{project_name}'")
                return content, True
            else:
                print(f"❌ No projects found matching '{project_name}'")
        return content, False
    
    # Add service
    if 'service' in user_input_lower and 'add' in user_input_lower:
        print("\n🤖 Generating service details...")
        system_context = """Generate a consulting service offering based on the user's request.
Return a JSON object with exactly these fields:
{
  "title": "Service Title",
  "description": "1-2 sentence description of what this service provides."
}
Return ONLY the JSON, no other text."""
        
        response = chat_with_ollama(user_input, system_context)
        if response:
            service_data = extract_json_from_response(response)
            if not service_data:
                try:
                    service_data = json.loads(response.strip())
                except:
                    pass
            
            if service_data and 'title' in service_data:
                print(f"\n📝 New service:")
                print(f"   Title: {service_data['title']}")
                print(f"   Description: {service_data.get('description', 'N/A')}")
                confirm = input("\nAdd this service? (y/n): ").strip().lower()
                if confirm == 'y':
                    content = add_service(
                        content,
                        service_data['title'],
                        service_data.get('description', '')
                    )
                    return content, True
            else:
                print("❌ Couldn't parse service details. Try being more specific.")
        return content, False
    
    # Remove service
    if 'service' in user_input_lower and 'remove' in user_input_lower:
        match = re.search(r'remove\s+(?:service\s+)?["\']?([^"\']+)["\']?', user_input_lower)
        if match:
            service_name = match.group(1).strip()
            content, removed = remove_service(content, service_name)
            if removed > 0:
                print(f"✅ Removed {removed} service(s) matching '{service_name}'")
                return content, True
            else:
                print(f"❌ No services found matching '{service_name}'")
        return content, False
    
    # General chat / ask for suggestions
    print("\n🤖 Asking web-search-helper...")
    response = chat_with_ollama(user_input)
    if response:
        print(f"\n{response}")
    
    return content, False


def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("🎨 PORTFOLIO MANAGER")
    print("Edit your consulting portfolio by chatting!")
    print("="*60)
    print("\nCommands:")
    print("  • 'show portfolio' - View current content")
    print("  • 'update bio to ...' - Change your bio")
    print("  • 'change headline to ...' - Update headline")
    print("  • 'add project about ...' - Add a new project")
    print("  • 'add service for ...' - Add a new service")
    print("  • 'remove project [name]' - Remove a project")
    print("  • 'update email to ...' - Change contact email")
    print("  • 'push' - Push changes to GitHub")
    print("  • 'quit' or 'exit' - Exit")
    print("-"*60)
    print("💡 Changes auto-push to GitHub after each edit!")
    
    # Check if Ollama is running
    try:
        requests.get("http://localhost:11434/api/tags", timeout=5)
    except:
        print("\n⚠️  Warning: Ollama doesn't seem to be running.")
        print("   Start it with: ollama serve")
    
    # Load current portfolio
    try:
        content = load_portfolio()
        print(f"\n✅ Loaded portfolio for: {content.get('name', 'Unknown')}")
    except FileNotFoundError:
        print(f"\n❌ Portfolio file not found: {CONTENT_FILE}")
        return
    except json.JSONDecodeError:
        print(f"\n❌ Invalid JSON in portfolio file")
        return
    
    # Main loop
    changes_made = False
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        
        if not user_input:
            continue
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        
        # Handle push command
        if user_input.lower() in ['push', 'deploy', 'publish']:
            push_to_github()
            continue
        
        content, changed = process_command(user_input, content)
        if changed:
            save_portfolio(content)
            changes_made = True
            # Auto-push after each change
            push_to_github()
    
    print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()
