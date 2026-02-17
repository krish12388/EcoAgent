# Groq Migration - EcoAgent Backend

## Overview
EcoAgent has been migrated from Ollama (local LLM) to Groq (cloud-based LLM API) for better performance and reliability.

## Changes Made

### 1. Configuration (`config.py`)
- Removed Ollama settings:
  - `ollama_base_url`
- Added Groq configuration:
  - `groq_api_key`: Your Groq API key (required)
  - `agent_model`: Default `llama-3.3-70b-versatile`
  - `agent_temperature`: Default `0.7`

### 2. Agent Files Updated
- **room_agent.py**: Switched from `ChatOllama` to `ChatGroq`
- **building_agent.py**: Switched from `ChatOllama` to `ChatGroq`
- **chat.py**: Switched from `ChatOllama` to `ChatGroq`

### 3. Dependencies (`requirements.txt`)
- Removed: `langchain-ollama==0.2.0`
- Added: `langchain-groq==0.2.0`

### 4. Environment Configuration (`.env`)
- Updated `.env.example` file with Groq settings
- Users need to create `.env` file with:
  ```env
  GROQ_API_KEY=your_groq_api_key_here
  AGENT_MODEL=llama-3.3-70b-versatile
  AGENT_TEMPERATURE=0.7
  ```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install langchain-groq
# or
pip install -r requirements.txt
```

### 2. Get Groq API Key
1. Visit [Groq Console](https://console.groq.com/keys)
2. Sign up or log in
3. Create a new API key
4. Copy the API key

### 3. Configure Environment
Create or update `.env` file in the `backend/` directory:

```env
# Groq API Key (Required)
GROQ_API_KEY=your_groq_api_key_here

# Agent Model (choose from available models)
AGENT_MODEL=llama-3.3-70b-versatile
AGENT_TEMPERATURE=0.7

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### 4. Verify Configuration
```bash
# Start the backend
python main.py

# Check the models endpoint
curl http://localhost:8000/api/chat/models
```

## Available Models

Groq offers several high-performance models:

- **llama-3.3-70b-versatile** (Recommended) - Latest Llama 3.3 70B, excellent balance
- **llama-3.1-70b-versatile** - Llama 3.1 70B, very capable
- **mixtral-8x7b-32768** - Mixtral 8x7B, good for complex reasoning
- **gemma2-9b-it** - Gemma 2 9B, fast and efficient

To change models, update `AGENT_MODEL` in your `.env` file.

## Benefits of Groq

- **Fast Inference**: Extremely fast response times (LPU technology)
- **High Quality**: Access to state-of-the-art open source models
- **No Local Setup**: No need to manage local model downloads or running Ollama
- **Scalable**: Cloud-based infrastructure handles demand
- **Cost-Effective**: Competitive pricing with generous free tier
- **Reliable**: Enterprise-grade availability and performance

## Migration from Ollama

If you were previously using Ollama:

1. **Uninstall Ollama** (optional):
   ```bash
   # Ollama is no longer needed
   # You can keep it for other projects or uninstall
   ```

2. **Update Environment**:
   - Remove `OLLAMA_BASE_URL` from your `.env`
   - Add `GROQ_API_KEY` to your `.env`
   - Update `AGENT_MODEL` to a Groq model

3. **Install New Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Restart Backend**:
   ```bash
   python main.py
   ```

## Troubleshooting

### 1. API Key Not Found
**Error**: "⚠️ Groq API key not configured"

**Solution**: Ensure `GROQ_API_KEY` is set in your `.env` file:
```bash
# Check if .env file exists
ls backend/.env

# If not, copy from example
cp backend/.env.example backend/.env

# Edit and add your API key
```

### 2. Model Not Found
**Error**: Model name not recognized

**Solution**: Use one of the supported models:
```env
AGENT_MODEL=llama-3.3-70b-versatile
```

### 3. Rate Limiting
**Error**: Rate limit exceeded

**Solution**: 
- Reduce `num_rooms` and `num_buildings` in analysis
- Use `budget_level=low` to reduce API calls
- Check your Groq account limits at [console.groq.com](https://console.groq.com)

### 4. Authentication Failed
**Error**: Invalid API key

**Solution**:
- Verify your API key is correct (no extra spaces)
- Check that the key is still active in Groq console
- Generate a new API key if needed

## Performance Comparison

| Feature | Ollama (Local) | Groq (Cloud) |
|---------|----------------|--------------|
| **Setup** | Complex (install + download models) | Simple (API key only) |
| **Speed** | Depends on hardware | Very fast (LPU) |
| **Cost** | Free (uses local resources) | Free tier + paid plans |
| **Reliability** | Depends on local setup | High (cloud infrastructure) |
| **Model Updates** | Manual | Automatic |
| **Hardware Requirements** | High (GPU recommended) | None (cloud-based) |

## API Usage Optimization

To minimize API calls and costs:

1. **Use Low Budget Mode**:
   ```python
   budget_level = "low"  # Uses heuristics instead of LLM when possible
   ```

2. **Analyze Fewer Entities**:
   ```python
   num_rooms = 5-10  # Instead of 50
   num_buildings = 1-2  # Instead of 5
   ```

3. **Cache Results**: The system only runs analysis when explicitly triggered

4. **Monitor Usage**: Check your usage at [console.groq.com](https://console.groq.com)

## Configuration Reference

### Full `.env` Example
```env
# Groq API Configuration
GROQ_API_KEY=gsk_your_actual_api_key_here

# Agent Configuration
AGENT_MODEL=llama-3.3-70b-versatile
AGENT_TEMPERATURE=0.7

# API Server Settings
API_HOST=0.0.0.0
API_PORT=8000

# Data Directory
DATA_DIR=./data
```

## Support

For issues or questions:
1. Check [Groq Documentation](https://console.groq.com/docs)
2. Review error messages in terminal
3. Check backend logs for detailed error information
4. Test with the `/api/chat/models` endpoint

---

**Migration Complete!** The backend is now fully configured to use Groq's fast and reliable LLM API. All agent reasoning will happen via Groq's cloud infrastructure.
