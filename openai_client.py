"""OpenAI API client for GPT models"""
import os
from typing import Optional


class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY in .env file")
        
        # Import openai here so it only fails if actually used
        try:
            import openai
            openai.api_key = self.api_key
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    def get_available_models(self) -> list:
        """Get list of available OpenAI models (simplified list)"""
        return ["gpt-3.5-turbo", "gpt-4"]
    
    def is_available(self) -> bool:
        """Check if OpenAI API key is valid"""
        try:
            # Try a simple API call to validate key
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            client.models.list()
            return True
        except Exception:
            return False
    
    def generate_response(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """Generate response from OpenAI GPT model"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"
