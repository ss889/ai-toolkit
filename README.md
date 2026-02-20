# 🤖 AI Toolkit

An extensible AI toolkit with custom tools for Ollama, featuring an integrated consulting portfolio for Sadikul Saber.

## 🎯 Quick Start

Your Ollama app already has **5 specialized models** ready to use:

| Model | Purpose |
|-------|---------|
| `web-search-helper` | Web search + Consulting portfolio info |
| `consulting-portfolio-helper` | Sadikul Saber's AI consulting portfolio |
| `calculator-helper` | Math calculations |
| `code-executor-helper` | Run Python code |
| `note-taking-helper` | Store and manage notes |

**How to use:** Open Ollama app → Select a model from dropdown → Start chatting!

---

## 🏢 Consulting Portfolio

The `consulting/` directory contains Sadikul Saber's AI consulting portfolio:

- **GitHub Repo:** https://github.com/ss889/consulting
- **Content Data:** `consulting/content.json`
- **Local Preview:** `python -m http.server 8000` in `consulting/` folder

Both `web-search-helper` and `consulting-portfolio-helper` have full knowledge of:
- Services offered (AI Strategy, LLM Integration, ML Development)
- Featured projects (Chatbot, Analytics, Document Intelligence)
- Contact information (ss889@gmail.com)

---

## 🛠️ Custom Tools Framework

Create your own tools and automatically generate Ollama models!

### Available Tools
```
tools/
├── base_tool.py              ← Base class for all tools
├── calculator_tool.py        ← Math calculations
├── web_search_tool.py        ← Web search + portfolio
├── code_executor_tool.py     ← Python code execution
├── note_taking_tool.py       ← Note management
├── consulting_tool.py        ← Portfolio management
└── registry.py               ← Tool registration
```

### Create a New Tool
1. Create `tools/my_tool.py` extending `BaseTool`
2. Register in `tools/registry.py`
3. Run: `python setup_tools.py --create`
4. New model appears in Ollama!

See [TOOLS_GUIDE.md](TOOLS_GUIDE.md) for detailed instructions.

---

## Prerequisites

- Python 3.8 or higher
- Ollama: https://ollama.ai
- API keys for cloud services (optional)

## Configuration

Edit the `.env` file to customize:

```bash
# Default model on startup
DEFAULT_MODEL=ollama:llama2

# API response limits
MAX_TOKENS=2048

# Response creativity (0.0-2.0)
TEMPERATURE=0.7

# Ollama location
OLLAMA_BASE_URL=http://localhost:11434
```

## Troubleshooting

### "Ollama not detected" / Can't connect to Ollama
- Ensure Ollama is installed and running: `ollama serve`
- Check that it's running at `http://localhost:11434`
- The app gracefully handles offline Ollama

### OpenAI/Gemini API errors
- Verify API keys are correct in `.env`
- Check internet connection
- Ensure API account has credits/quota

### Port already in use
If port is busy when previewing the consulting site:
```bash
python -m http.server 8001
```

## Security

⚠️ **Important:**
- `.env` file contains sensitive API keys
- **NEVER commit `.env` to git** (already in `.gitignore`)
- If you accidentally expose keys, regenerate them immediately:
  - OpenAI: https://platform.openai.com/api-keys
  - Google: https://ai.google.dev

## Project Structure

```
ai-toolkit/
├── .env                      # ⚠️ API keys (DO NOT COMMIT)
├── .env.example              # Template for API keys
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python dependencies
│
├── consulting/               # AI Consulting Portfolio
│   ├── content.json         # Portfolio content data
│   ├── index.html           # Portfolio website
│   ├── styles.css           # Website styling
│   ├── render.js            # Dynamic rendering
│   └── OLLAMA_PROMPTS.md    # Content generation prompts
│
├── tools/                    # Custom Tools Framework
│   ├── base_tool.py         # Base class
│   ├── calculator_tool.py   # Calculator
│   ├── web_search_tool.py   # Web Search + Portfolio
│   ├── code_executor_tool.py# Code Executor
│   ├── note_taking_tool.py  # Note Taking
│   ├── consulting_tool.py   # Portfolio Tool
│   └── registry.py          # Tool Registry
│
├── modelfiles/               # Generated Ollama Modelfiles
│   ├── Modelfile-web-search
│   ├── Modelfile-consulting-portfolio
│   └── ...
│
├── setup_tools.py            # Create/manage Ollama models
├── ollama_client.py          # Ollama API client
├── openai_client.py          # OpenAI API client
├── gemini_client.py          # Google Gemini API client
└── README.md                 # This file
```

## Development

To extend the toolkit:

1. **Add a new tool**: Create a tool class in `tools/` extending `BaseTool`
2. **Register the tool**: Add to `tools/registry.py`
3. **Generate model**: Run `python setup_tools.py --create`

Example: Creating a weather tool
```python
# tools/weather_tool.py
from tools.base_tool import BaseTool

class WeatherTool(BaseTool):
    name = "weather"
    description = "Get weather information"
    
    def get_system_prompt(self):
        return "You are a weather assistant..."
```

## Commands Reference

```bash
# List all Ollama models
ollama list

# Generate Modelfiles only
python setup_tools.py

# Create models in Ollama
python setup_tools.py --create

# Preview consulting portfolio
cd consulting && python -m http.server 8000
```

## 👤 Contact

**Sadikul Saber** - AI Consultant
- Email: ss889@gmail.com
- GitHub: https://github.com/ss889
- Portfolio: https://github.com/ss889/consulting

## Support

For issues or feature requests, check:
- Ollama docs: https://github.com/ollama/ollama
- OpenAI docs: https://platform.openai.com/docs
- Gemini docs: https://ai.google.dev

---
**Built with Ollama + Python** 🚀

---

**Happy Chatting! 🚀**
