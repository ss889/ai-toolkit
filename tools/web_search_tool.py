"""Web Search Tool - Search information online with Consulting Portfolio integration"""
from .base_tool import BaseTool
from typing import Dict, List
import requests
from urllib.parse import quote
import json
from pathlib import Path


class WebSearchTool(BaseTool):
    """Tool for searching the web with consulting portfolio integration"""
    
    def __init__(self):
        super().__init__(
            name="Web Search",
            description="Search the internet for information and access Sadikul Saber's AI consulting portfolio.",
            version="2.0"
        )
        self.portfolio_data = self._load_portfolio()
    
    def _load_portfolio(self) -> dict:
        """Load consulting portfolio data"""
        try:
            content_file = Path(__file__).parent.parent / "consulting" / "content.json"
            if content_file.exists():
                with open(content_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading portfolio: {e}")
        return {}
    
    def execute(self, input_text: str) -> str:
        """
        Execute web search.
        
        Args:
            input_text: Search query
            
        Returns:
            Search results summary
        """
        query = input_text.strip()
        
        if not query:
            return "Please provide a search query."
        
        try:
            # Using DuckDuckGo API for anonymous search (no API key required)
            results = self._search_duckduckgo(query)
            
            if results:
                formatted_results = self._format_results(results)
                return formatted_results
            else:
                return f"No results found for: {query}"
        
        except Exception as e:
            return f"Error performing search: {str(e)}\n\nNote: Web search requires internet connection."
    
    def _search_duckduckgo(self, query: str) -> List[Dict]:
        """
        Search using DuckDuckGo API.
        
        Args:
            query: Search query
            
        Returns:
            List of search results
        """
        try:
            # Using DuckDuckGo's API endpoint
            url = f"https://api.duckduckgo.com/?q={quote(query)}&format=json&no_redirect=1&no_html=1"
            
            headers = {
                'User-Agent': 'AI-Toolkit/1.0'
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            data = response.json()
            
            results = []
            
            # Parse RelatedTopics
            if 'RelatedTopics' in data and data['RelatedTopics']:
                for item in data['RelatedTopics'][:5]:  # Limit to 5 results
                    if 'Text' in item and 'FirstURL' in item:
                        results.append({
                            'title': item['Text'][:100],
                            'url': item['FirstURL'],
                            'snippet': item['Text'][:200]
                        })
            
            return results
        
        except Exception as e:
            return []
    
    def _format_results(self, results: List[Dict]) -> str:
        """
        Format search results for display.
        
        Args:
            results: List of search results
            
        Returns:
            Formatted results as string
        """
        if not results:
            return "No results found."
        
        formatted = "Search Results:\n" + "="*50 + "\n\n"
        
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result.get('title', 'No title')}\n"
            formatted += f"   {result.get('snippet', 'No description')}\n"
            formatted += f"   URL: {result.get('url', 'No URL')}\n\n"
        
        return formatted
    
    def get_system_prompt(self) -> str:
        """Get system prompt for web search tool with consulting portfolio"""
        
        # Build portfolio info for the prompt
        portfolio_info = ""
        if self.portfolio_data:
            name = self.portfolio_data.get('name', 'Sadikul Saber')
            title = self.portfolio_data.get('title', 'AI Consultant')
            bio = self.portfolio_data.get('bio', '')
            email = self.portfolio_data.get('contact', {}).get('email', 'ss889@gmail.com')
            
            services = self.portfolio_data.get('services', [])
            services_text = '\\n'.join([f"   - {s.get('title', 'N/A')}: {s.get('description', 'N/A')}" for s in services])
            
            projects = self.portfolio_data.get('projects', [])
            projects_text = '\\n'.join([f"   - {p.get('title', 'N/A')}: {p.get('description', 'N/A')[:100]}..." for p in projects])
            
            portfolio_info = f"""

=== CONSULTING PORTFOLIO ===

You also have access to {name}'s AI consulting portfolio:

ABOUT:
   Name: {name}
   Title: {title}
   Bio: {bio}

SERVICES OFFERED:
{services_text}

FEATURED PROJECTS:
{projects_text}

CONTACT:
   Email: {email}
   Website: https://github.com/ss889/consulting

=== PORTFOLIO EDITING ===

When users want to edit the portfolio (update bio, add projects, etc.), you can help generate content.

For content generation requests, return clean, professional content:
- Bio updates: Return just the new bio text (2-3 sentences)
- Headlines: Return just the headline text (under 15 words)
- Projects: Return JSON format: {{"title": "...", "description": "..."}}
- Services: Return JSON format: {{"title": "...", "description": "..."}}

When users ask about editing or updating portfolio content:
- Help generate professional, engaging content
- Keep bios concise and impactful
- Make project descriptions highlight impact and technologies
- Ensure services clearly communicate value

When users ask about:
- AI consulting services -> Reference the services above
- Hiring an AI consultant -> Direct to {email}
- AI projects or case studies -> Reference the projects above
- Who built this / about the creator -> Share {name}'s info
- Editing/updating portfolio -> Help generate content
"""
        
        return f"""You are a helpful information assistant with access to web search and an AI consulting portfolio.

WEB SEARCH CAPABILITIES:
1. If you can answer from your knowledge, do so
2. If you need current information, use web search to find the latest data
3. Always cite sources when providing web search results
4. Be clear about what information came from web search vs. your training data

You can search the internet for:
- Current events and news
- AI/ML industry trends and developments
- Technical documentation
- Specific facts and statistics
- Product reviews and comparisons

When presenting search results, always:
- Provide the source/URL
- Explain how the information answers the user's question
- Compare multiple sources if available

PORTFOLIO CONTENT EDITING:
When users ask to update, generate, or edit portfolio content:
- For bio updates: Return ONLY the new bio text, nothing else
- For headlines: Return ONLY the headline text (under 15 words)
- For new projects: Return ONLY this JSON format:
  {{"title": "Project Title", "description": "2-3 sentence description"}}
- For new services: Return ONLY this JSON format:
  {{"title": "Service Title", "description": "1-2 sentence description"}}

Keep generated content professional, concise, and impactful.
{portfolio_info}"""
