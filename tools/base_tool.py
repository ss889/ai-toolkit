"""Base class for all custom tools"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseTool(ABC):
    """Base class for custom tools in the AI Toolkit"""
    
    def __init__(self, name: str, description: str, version: str = "1.0"):
        """
        Initialize a custom tool.
        
        Args:
            name: Name of the tool (e.g., "Calculator", "Web Search")
            description: Description of what the tool does
            version: Version of the tool
        """
        self.name = name
        self.description = description
        self.version = version
    
    @abstractmethod
    def execute(self, input_text: str) -> str:
        """
        Execute the tool with the given input.
        
        Args:
            input_text: Input to process
            
        Returns:
            Result as a string
        """
        pass
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt that teaches the LLM how to use this tool.
        
        Returns:
            System prompt as a string
        """
        return f"""You have access to the {self.name} tool. {self.description}

When the user asks a question that requires using this tool, provide the answer using the tool's capabilities."""
    
    def get_modelfile(self) -> str:
        """
        Generate an Ollama Modelfile for this tool.
        
        Returns:
            Modelfile content as a string
        """
        system_prompt = self.get_system_prompt()
        # Escape quotes and newlines for Modelfile format
        system_prompt = system_prompt.replace('"', '\\"').replace('\n', '\\n')
        return f'''FROM llama3.2:3b
PARAMETER temperature 0.7
PARAMETER top_p 0.9
SYSTEM "{system_prompt}"
'''
    
    def validate_input(self, input_text: str) -> bool:
        """
        Validate input before execution.
        
        Args:
            input_text: Input to validate
            
        Returns:
            True if valid, False otherwise
        """
        return bool(input_text.strip())
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert tool to dictionary representation.
        
        Returns:
            Dictionary with tool information
        """
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "type": self.__class__.__name__
        }
