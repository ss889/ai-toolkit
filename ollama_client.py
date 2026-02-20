"""Ollama API client for local model inference"""
import requests
from typing import List, Dict, Optional


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.api_version = "v1"
    
    def get_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            return models
        except requests.exceptions.ConnectionError:
            return []
        except Exception:
            return []
    
    def is_available(self) -> bool:
        """Check if Ollama service is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False
    
    def generate_response(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """Generate response from Ollama model"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "stream": False
                },
                timeout=300  # 5 minute timeout for long responses
            )
            response.raise_for_status()
            data = response.json()
            return data.get('response', '').strip()
        except requests.exceptions.Timeout:
            return "Error: Request timed out. The model may be slow or overloaded."
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama. Is it running at " + self.base_url + "?"
        except Exception as e:
            return f"Error: {str(e)}"
