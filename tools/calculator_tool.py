"""Calculator Tool - Performs mathematical calculations"""
import re
import math
from .base_tool import BaseTool


class CalculatorTool(BaseTool):
    """Tool for performing mathematical calculations"""
    
    def __init__(self):
        super().__init__(
            name="Calculator",
            description="Performs mathematical calculations, algebra, trigonometry, and other math operations.",
            version="1.0"
        )
        self.supported_functions = {
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'sqrt': math.sqrt,
            'log': math.log10,
            'ln': math.log,
            'abs': abs,
            'floor': math.floor,
            'ceil': math.ceil,
            'pi': math.pi,
            'e': math.e,
        }
    
    def execute(self, input_text: str) -> str:
        """
        Execute calculation from natural language or mathematical expression.
        
        Args:
            input_text: Calculation request (e.g., "2 + 2", "sqrt of 16", "sin(π/2)")
            
        Returns:
            Calculation result
        """
        try:
            # Clean input
            expression = input_text.strip()
            
            # Replace common words with operators
            expression = expression.lower()
            expression = expression.replace('plus', '+')
            expression = expression.replace('minus', '-')
            expression = expression.replace('multiply', '*')
            expression = expression.replace('divide', '/')
            expression = expression.replace('squared', '**2')
            expression = expression.replace('cubed', '**3')
            expression = expression.replace('to the power of', '**')
            expression = expression.replace('power', '**')
            expression = expression.replace('sqrt', f'math.sqrt')
            expression = expression.replace('square root', f'math.sqrt')
            expression = expression.replace('sin', f'math.sin')
            expression = expression.replace('cos', f'math.cos')
            expression = expression.replace('tan', f'math.tan')
            expression = expression.replace('log', f'math.log10')
            expression = expression.replace('ln', f'math.log')
            expression = expression.replace('π', str(math.pi))
            expression = expression.replace('pi', str(math.pi))
            expression = expression.replace('e', str(math.e))
            
            # Remove spaces around operators for cleaner evaluation
            expression = re.sub(r'\s*([+\-*/%^])\s*', r'\1', expression)
            
            # Safe evaluation with math functions
            safe_dict = {
                'math': math,
                '__builtins__': {},
            }
            
            result = eval(expression, safe_dict)
            
            # Format result
            if isinstance(result, float):
                # Round to reasonable precision
                if result == int(result):
                    return str(int(result))
                else:
                    return str(round(result, 10))
            else:
                return str(result)
        
        except Exception as e:
            return f"Error: Could not calculate. {str(e)}\n\nSupported operations: +, -, *, /, **, sqrt, sin, cos, tan, log, ln, abs, floor, ceil"
    
    def get_system_prompt(self) -> str:
        """Get system prompt for calculator tool"""
        return """You are a helpful calculator assistant. When users ask mathematical questions:

1. If it's a straightforward calculation, provide the answer
2. Show the formula or steps if it helps understanding
3. If the calculation is complex, break it down into steps
4. Handle both simple arithmetic and advanced math (trigonometry, logarithms, etc.)

Examples of what you can calculate:
- Basic arithmetic: 2 + 2, 10 * 5, etc.
- Powers and roots: 2^10, sqrt(16), 3^(1/3)
- Trigonometry: sin(π/2), cos(0), tan(π/4)
- Logarithms: log(100), ln(e)

Always show the result clearly and in a user-friendly format."""
