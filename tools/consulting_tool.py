"""Consulting Portfolio Tool - Manage AI Consultant Portfolio"""
import json
from pathlib import Path
from datetime import datetime
from .base_tool import BaseTool


class ConsultingTool(BaseTool):
    """Tool for managing AI consultant portfolio content"""
    
    def __init__(self):
        super().__init__(
            name="Consulting Portfolio",
            description="Manage Sadikul Saber's AI consulting portfolio - read/update content, search for AI consulting topics, and generate professional content.",
            version="1.0"
        )
        self.content_file = Path(__file__).parent.parent / "consulting" / "content.json"
        self.portfolio_data = self._load_portfolio()
    
    def _load_portfolio(self) -> dict:
        """Load portfolio content from content.json"""
        try:
            if self.content_file.exists():
                with open(self.content_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading portfolio: {e}")
        return {}
    
    def _save_portfolio(self):
        """Save portfolio content to content.json"""
        try:
            with open(self.content_file, 'w', encoding='utf-8') as f:
                json.dump(self.portfolio_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving portfolio: {e}")
            return False
    
    def execute(self, input_text: str) -> str:
        """
        Execute portfolio operations.
        
        Args:
            input_text: Command in format "ACTION:content" or natural language query
                       Actions: GET, UPDATE:field|value, LIST, SERVICES, PROJECTS, BIO
        
        Returns:
            Operation result or portfolio information
        """
        command = input_text.strip()
        
        if not command:
            return self._get_portfolio_summary()
        
        # Handle direct commands
        if ':' in command:
            action, params = command.split(':', 1)
            action = action.strip().upper()
            params = params.strip()
            
            if action == "GET":
                return self._get_field(params)
            elif action == "UPDATE":
                return self._update_field(params)
            elif action == "LIST":
                return self._list_all()
        
        # Handle natural language queries
        command_lower = command.lower()
        
        if any(word in command_lower for word in ['bio', 'about', 'summary']):
            return self._get_bio()
        elif any(word in command_lower for word in ['service', 'offer', 'what do']):
            return self._get_services()
        elif any(word in command_lower for word in ['project', 'work', 'portfolio', 'case']):
            return self._get_projects()
        elif any(word in command_lower for word in ['contact', 'email', 'reach', 'hire']):
            return self._get_contact()
        elif any(word in command_lower for word in ['all', 'everything', 'full', 'summary']):
            return self._get_portfolio_summary()
        
        # Default: return summary
        return self._get_portfolio_summary()
    
    def _get_portfolio_summary(self) -> str:
        """Get full portfolio summary"""
        data = self.portfolio_data
        
        summary = f"""
===========================================
PORTFOLIO: {data.get('name', 'N/A')}
===========================================

TITLE: {data.get('title', 'N/A')}
HEADLINE: {data.get('headline', 'N/A')}

BIO:
{data.get('bio', 'N/A')}

SERVICES ({len(data.get('services', []))}):
"""
        for i, service in enumerate(data.get('services', []), 1):
            summary += f"  {i}. {service.get('title', 'N/A')}\n"
            summary += f"     {service.get('description', 'N/A')}\n\n"
        
        summary += f"\nPROJECTS ({len(data.get('projects', []))}):\n"
        for i, project in enumerate(data.get('projects', []), 1):
            summary += f"  {i}. {project.get('title', 'N/A')}\n"
            summary += f"     {project.get('description', 'N/A')[:100]}...\n\n"
        
        contact = data.get('contact', {})
        summary += f"""
CONTACT:
  Email: {contact.get('email', 'N/A')}
  Call to Action: {contact.get('callToAction', 'N/A')}
"""
        
        return summary
    
    def _get_bio(self) -> str:
        """Get bio/about information"""
        data = self.portfolio_data
        return f"""
NAME: {data.get('name', 'N/A')}
TITLE: {data.get('title', 'N/A')}
HEADLINE: {data.get('headline', 'N/A')}

BIO:
{data.get('bio', 'N/A')}
"""
    
    def _get_services(self) -> str:
        """Get services offered"""
        services = self.portfolio_data.get('services', [])
        
        if not services:
            return "No services defined yet."
        
        result = f"SERVICES OFFERED ({len(services)}):\n" + "="*40 + "\n\n"
        
        for i, service in enumerate(services, 1):
            result += f"{i}. {service.get('title', 'N/A')}\n"
            result += f"   {service.get('description', 'N/A')}\n\n"
        
        return result
    
    def _get_projects(self) -> str:
        """Get project portfolio"""
        projects = self.portfolio_data.get('projects', [])
        
        if not projects:
            return "No projects defined yet."
        
        result = f"PROJECT PORTFOLIO ({len(projects)}):\n" + "="*40 + "\n\n"
        
        for i, project in enumerate(projects, 1):
            result += f"{i}. {project.get('title', 'N/A')}\n"
            result += f"   {project.get('description', 'N/A')}\n"
            if project.get('liveLink') and project.get('liveLink') != '#!':
                result += f"   Live: {project.get('liveLink')}\n"
            result += "\n"
        
        return result
    
    def _get_contact(self) -> str:
        """Get contact information"""
        contact = self.portfolio_data.get('contact', {})
        social = contact.get('social', {})
        
        return f"""
CONTACT INFORMATION
==================

Email: {contact.get('email', 'N/A')}

Social Links:
- LinkedIn: {social.get('linkedin', 'N/A')}
- GitHub: {social.get('github', 'N/A')}
- Twitter: {social.get('twitter', 'N/A')}

Call to Action: {contact.get('callToAction', 'N/A')}
"""
    
    def _get_field(self, field: str) -> str:
        """Get a specific field from portfolio"""
        field = field.strip().lower()
        
        if field in self.portfolio_data:
            value = self.portfolio_data[field]
            if isinstance(value, (dict, list)):
                return json.dumps(value, indent=2)
            return str(value)
        
        return f"Field '{field}' not found. Available fields: {list(self.portfolio_data.keys())}"
    
    def _update_field(self, params: str) -> str:
        """Update a field in portfolio"""
        if '|' not in params:
            return "Format: UPDATE:field|value"
        
        field, value = params.split('|', 1)
        field = field.strip()
        value = value.strip()
        
        # Handle nested updates
        if '.' in field:
            parts = field.split('.')
            obj = self.portfolio_data
            for part in parts[:-1]:
                if part not in obj:
                    return f"Field path '{field}' not found."
                obj = obj[part]
            obj[parts[-1]] = value
        else:
            self.portfolio_data[field] = value
        
        if self._save_portfolio():
            return f"Updated '{field}' successfully!"
        else:
            return "Error saving portfolio."
    
    def _list_all(self) -> str:
        """List all available fields"""
        return f"Available fields: {list(self.portfolio_data.keys())}"
    
    def get_system_prompt(self) -> str:
        """Get system prompt for consulting portfolio tool"""
        return f"""You are an AI assistant for Sadikul Saber's AI consulting portfolio. You have access to the full portfolio data and can help with:

1. PORTFOLIO INFORMATION:
   - Bio and professional summary
   - Services offered (AI Strategy, LLM Integration, ML Development)
   - Project portfolio and case studies
   - Contact information

2. PORTFOLIO OWNER:
   Name: {self.portfolio_data.get('name', 'Sadikul Saber')}
   Title: {self.portfolio_data.get('title', 'AI Consultant')}
   Headline: {self.portfolio_data.get('headline', 'N/A')}
   Email: {self.portfolio_data.get('contact', {}).get('email', 'N/A')}

3. KEY SERVICES:
{chr(10).join(f'   - {s.get("title", "N/A")}' for s in self.portfolio_data.get('services', []))}

4. FEATURED PROJECTS:
{chr(10).join(f'   - {p.get("title", "N/A")}' for p in self.portfolio_data.get('projects', []))}

When users ask about the portfolio, services, projects, or want to contact Sadikul:
- Provide accurate information from the portfolio
- Be professional and helpful
- Highlight relevant services based on user needs
- Direct inquiries to {self.portfolio_data.get('contact', {}).get('email', 'ss889@gmail.com')}

You can also help generate new content for the portfolio using AI."""
