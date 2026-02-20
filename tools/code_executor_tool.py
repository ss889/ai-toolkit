"""Code Executor Tool - Execute and analyze code"""
import re
import subprocess
import tempfile
from pathlib import Path
from .base_tool import BaseTool


class CodeExecutorTool(BaseTool):
    """Tool for executing Python code and analyzing code"""
    
    def __init__(self):
        super().__init__(
            name="Code Executor",
            description="Execute Python code snippets, run scripts, and analyze code functionality.",
            version="1.0"
        )
    
    def execute(self, input_text: str) -> str:
        """
        Execute Python code.
        
        Args:
            input_text: Python code to execute
            
        Returns:
            Execution output or error message
        """
        code = input_text.strip()
        
        # Extract code from markdown blocks if present
        code = self._extract_code_block(code)
        
        if not code:
            return "Please provide Python code to execute."
        
        try:
            # Create temporary file for code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # Execute code with timeout
                result = subprocess.run(
                    ['python', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                output = result.stdout
                if result.stderr:
                    output += "\nErrors:\n" + result.stderr
                
                return output if output else "Code executed successfully but produced no output."
            
            finally:
                # Cleanup temp file
                Path(temp_file).unlink(missing_ok=True)
        
        except subprocess.TimeoutExpired:
            return "Error: Code execution timed out (exceeded 10 seconds)"
        except Exception as e:
            return f"Error executing code: {str(e)}"
    
    def _extract_code_block(self, text: str) -> str:
        """
        Extract Python code from markdown code blocks.
        
        Args:
            text: Text that may contain code blocks
            
        Returns:
            Extracted code or original text
        """
        # Try to extract from ```python ... ``` blocks
        match = re.search(r'```python\n(.*?)\n```', text, re.DOTALL)
        if match:
            return match.group(1)
        
        # Try to extract from ``` ... ``` blocks
        match = re.search(r'```\n(.*?)\n```', text, re.DOTALL)
        if match:
            return match.group(1)
        
        return text
    
    def get_system_prompt(self) -> str:
        """Get system prompt for code executor tool"""
        return """You are a helpful code assistant. When users ask questions related to programming:

1. Provide clear, well-commented code
2. Explain what the code does
3. If asked to execute code, provide it in a code block
4. For complex problems, break the solution into steps
5. When showing code, format it properly:
   ```python
   # Your code here
   ```

You can execute Python code to:
- Demonstrate solutions
- Run calculations and simulations
- Process data
- Test algorithms
- Visualize concepts (text-based)

When providing executable code:
- Make it self-contained and runnable
- Include any necessary imports
- Add print statements to show results
- Handle errors gracefully

Safety considerations:
- Code runs in isolation with a 10-second timeout
- Focus on constructive, educational code
- Be explicit about what the code does"""
