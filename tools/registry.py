"""Tool Registry - Manage and organize custom tools"""
from typing import Dict, List
from pathlib import Path
import json
from .base_tool import BaseTool
from .calculator_tool import CalculatorTool
from .web_search_tool import WebSearchTool
from .code_executor_tool import CodeExecutorTool
from .note_taking_tool import NoteTakingTool
from .consulting_tool import ConsultingTool


class ToolRegistry:
    """Registry for managing all custom tools"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register all default tools"""
        self.register(CalculatorTool())
        self.register(WebSearchTool())
        self.register(CodeExecutorTool())
        self.register(NoteTakingTool())
        self.register(ConsultingTool())
    
    def register(self, tool: BaseTool):
        """
        Register a new tool.
        
        Args:
            tool: BaseTool instance to register
        """
        self.tools[tool.name.lower().replace(' ', '-')] = tool
        print(f"Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> BaseTool:
        """
        Get a tool by name.
        
        Args:
            name: Tool name (case-insensitive)
            
        Returns:
            BaseTool instance or None
        """
        return self.tools.get(name.lower().replace(' ', '-'))
    
    def list_tools(self) -> List[str]:
        """
        List all registered tools.
        
        Returns:
            List of tool names
        """
        return list(self.tools.keys())
    
    def get_all_tools(self) -> List[BaseTool]:
        """
        Get all registered tool instances.
        
        Returns:
            List of BaseTool instances
        """
        return list(self.tools.values())
    
    def generate_modelfiles(self, output_dir: Path = None) -> Dict[str, str]:
        """
        Generate Modelfiles for all tools.
        
        Args:
            output_dir: Directory to save Modelfiles (optional)
            
        Returns:
            Dictionary mapping tool names to Modelfile content
        """
        if output_dir is None:
            output_dir = Path.cwd() / "modelfiles"
        
        output_dir.mkdir(exist_ok=True)
        modelfiles = {}
        
        for tool_id, tool in self.tools.items():
            modelfile_content = tool.get_modelfile()
            modelfiles[tool_id] = modelfile_content
            
            # Write to file
            modelfile_path = output_dir / f"Modelfile-{tool_id}"
            with open(modelfile_path, 'w', encoding='utf-8') as f:
                f.write(modelfile_content)
            
            print(f"Generated Modelfile for {tool.name}: {modelfile_path}")
        
        return modelfiles
    
    def export_tools_manifest(self, output_file: Path = None) -> Dict:
        """
        Export a manifest of all tools.
        
        Args:
            output_file: File to save manifest (optional)
            
        Returns:
            Manifest dictionary
        """
        if output_file is None:
            output_file = Path.cwd() / "tools_manifest.json"
        
        manifest = {
            "version": "1.0",
            "tools": [tool.to_dict() for tool in self.get_all_tools()]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"Exported tools manifest: {output_file}")
        return manifest
    
    def execute_tool(self, tool_name: str, input_text: str) -> str:
        """
        Execute a tool.
        
        Args:
            tool_name: Name of the tool to execute
            input_text: Input for the tool
            
        Returns:
            Tool execution result
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return f"Tool '{tool_name}' not found. Available tools: {', '.join(self.list_tools())}"
        
        if not tool.validate_input(input_text):
            return f"Invalid input for {tool.name}"
        
        return tool.execute(input_text)
