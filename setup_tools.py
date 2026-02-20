"""
Setup Custom Tools in Ollama

This script generates custom Ollama models for each tool.
Run this to create models like "calculator-helper", "web-search", etc.
"""
import subprocess
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from tools.registry import ToolRegistry


def create_ollama_models():
    """Create custom Ollama models for each tool"""
    
    registry = ToolRegistry()
    
    print("="*60)
    print("AI TOOLKIT - Custom Ollama Models Setup")
    print("="*60)
    print()
    
    # Create modelfiles directory
    modelfiles_dir = Path(__file__).parent / "modelfiles"
    modelfiles_dir.mkdir(exist_ok=True)
    
    print(f"Generating Modelfiles in: {modelfiles_dir}")
    print()
    
    # Generate modelfiles for all tools
    for tool in registry.get_all_tools():
        tool_id = tool.name.lower().replace(' ', '-')
        model_name = f"{tool_id}-helper"
        
        modelfile_content = tool.get_modelfile()
        modelfile_path = modelfiles_dir / f"Modelfile-{tool_id}"
        
        # Write modelfile
        with open(modelfile_path, 'w', encoding='utf-8') as f:
            f.write(modelfile_content)
        
        print(f"✓ Created: {modelfile_path}")
        print(f"  Model name: {model_name}")
        print(f"  Description: {tool.description}")
        print()
    
    print("="*60)
    print("Next Steps:")
    print("="*60)
    print()
    print("To create the custom models in Ollama, run:")
    print()
    
    for tool in registry.get_all_tools():
        tool_id = tool.name.lower().replace(' ', '-')
        model_name = f"{tool_id}-helper"
        modelfile_path = modelfiles_dir / f"Modelfile-{tool_id}"
        
        print(f"  ollama create {model_name} -f {modelfile_path}")
    
    print()
    print("OR run the automated setup:")
    print()
    print(f"  python setup_tools.py --create")
    print()
    print("="*60)


def setup_models_with_ollama(registry: ToolRegistry):
    """Automatically create models in Ollama"""
    
    # Check if ollama is available
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True)
        if result.returncode != 0:
            print("Error: Ollama not found in PATH")
            return False
    except FileNotFoundError:
        print("Error: Ollama not installed or not in PATH")
        return False
    
    modelfiles_dir = Path(__file__).parent / "modelfiles"
    
    print("\nCreating custom models in Ollama...")
    print("="*60)
    
    for tool in registry.get_all_tools():
        tool_id = tool.name.lower().replace(' ', '-')
        model_name = f"{tool_id}-helper"
        modelfile_path = modelfiles_dir / f"Modelfile-{tool_id}"
        
        print(f"\nCreating model: {model_name}")
        
        try:
            # Create the model in Ollama
            result = subprocess.run(
                ['ollama', 'create', model_name, '-f', str(modelfile_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✓ Successfully created: {model_name}")
            else:
                print(f"✗ Failed to create {model_name}")
                if result.stderr:
                    print(f"  Error: {result.stderr}")
        
        except Exception as e:
            print(f"✗ Error creating {model_name}: {e}")
    
    print("\n" + "="*60)
    print("Setup complete!")
    print("Your custom models are now available in Ollama:")
    print("="*60)
    
    for tool in registry.get_all_tools():
        tool_id = tool.name.lower().replace(' ', '-')
        model_name = f"{tool_id}-helper"
        print(f"  • {model_name}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup custom AI Toolkit tools in Ollama")
    parser.add_argument("--create", action="store_true", help="Automatically create models in Ollama")
    
    args = parser.parse_args()
    
    registry = ToolRegistry()
    
    if args.create:
        setup_models_with_ollama(registry)
    else:
        create_ollama_models()
