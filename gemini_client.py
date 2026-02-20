"""Google Gemini API client"""
import os
from typing import Optional


class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key not found. Set GEMINI_API_KEY in .env file")
        
        # Import google.generativeai here so it only fails if actually used
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
    
    def get_available_models(self) -> list:
        """Get list of available Gemini models"""
        return ["gemini-pro"]
    
    def is_available(self) -> bool:
        """Check if Gemini API key is valid"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            # List models to verify API key works
            genai.list_models()
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
        """Generate response from Gemini model"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            
            model_instance = genai.GenerativeModel(model)
            response = model_instance.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
