# Ollama Migration - EcoAgent Backend

## Changes Made

### 1. **Updated Configuration** (`config.py`)
- Removed Google Gemini API settings
- Added Ollama configuration:
  - `ollama_base_url`: Default `http://localhost:11434`
  - `agent_model`: Changed to `mistral-small:24b`

### 2. **Updated All Agents**
- **room_agent.py**: Switched from `ChatGoogleGenerativeAI` to `ChatOllama`
- **building_agent.py**: Switched from `ChatGoogleGenerativeAI` to `ChatOllama`
- **campus_graph.py**: Switched from `ChatGoogleGenerativeAI` to `ChatOllama`

### 3. **Updated Dependencies** (`requirements.txt`)
- Removed: `langchain-google-genai==2.0.5`
- Added: `langchain-ollama==0.2.0`

### 4. **Environment Configuration** (`.env`)
- Created new `.env` file with Ollama settings
- No API key required (local model)

## Installation Steps

1. **Install the new dependency:**
```bash
cd backend
pip install langchain-ollama
```

2. **Verify Ollama is running:**
```bash
ollama list
# Should show: mistral-small:24b
```

3. **Start Ollama service** (if not running):
```bash
ollama serve
```

4. **Test the model:**
```bash
ollama run mistral-small:24b "Hello, are you working?"
```

5. **Start the backend:**
```bash
cd backend
python main.py
```

## How It Works

- **Local Inference**: All AI reasoning now runs on your local machine using Ollama
- **No API Costs**: No external API calls or rate limits
- **Same Functionality**: The multi-agent system works identically, just using your local model
- **Performance**: Mistral-small:24b (14GB) provides strong reasoning capabilities

## Benefits

✅ **No API Key Required** - No need for Google Gemini API key  
✅ **No Rate Limits** - Process as many requests as your machine can handle  
✅ **Privacy** - All data stays on your local machine  
✅ **Cost-Free** - No per-request costs  
✅ **Offline Capable** - Works without internet connection  

## Model Used

**mistral-small:24b**
- Size: 14 GB
- Parameters: 24 billion
- Strengths: Reasoning, analysis, structured outputs
- Perfect for: Multi-agent systems, sustainability analysis

## Troubleshooting

### If backend fails to start:

1. **Check Ollama is running:**
```bash
curl http://localhost:11434/api/tags
```

2. **Verify model is available:**
```bash
ollama list | grep mistral-small
```

3. **Check logs for connection errors**

4. **Ensure port 11434 is not blocked**

## Configuration Options

Edit `.env` to customize:

```env
# Change Ollama URL (if using remote Ollama)
OLLAMA_BASE_URL=http://localhost:11434

# Use different model
AGENT_MODEL=mistral-small:24b

# Adjust temperature (0.0 = deterministic, 1.0 = creative)
AGENT_TEMPERATURE=0.7
```

## Next Steps

The backend is now fully configured to use your local Ollama mistral-small:24b model. All agent reasoning will happen locally without any external API calls.
