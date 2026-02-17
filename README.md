# 🌱 EcoAgent - AI-Powered Campus Sustainability System

> An intelligent multi-agent system for real-time campus energy monitoring, analysis, and optimization using LangGraph and Groq.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB.svg)](https://reactjs.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Latest-orange.svg)](https://github.com/langchain-ai/langgraph)

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Demo Mode](#demo-mode)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

EcoAgent is a sophisticated sustainability management system that leverages a hierarchical multi-agent architecture to monitor, analyze, and optimize energy consumption across educational campuses. The system uses AI agents powered by Groq's LLM to provide intelligent recommendations for energy savings and resource optimization.

### Why EcoAgent?

- **Real-time Monitoring**: Track energy, water, and occupancy across all campus buildings
- **Intelligent Analysis**: AI agents analyze patterns and detect anomalies automatically
- **Predictive Insights**: Forecast future demand and optimize resource allocation
- **Cost Savings**: Identify potential savings opportunities (15-40% energy reduction)
- **Manual Control**: All parameters configurable for demonstrations and testing
- **No Auto-Execution**: Agents run only when explicitly triggered - perfect for API key management

## ✨ Key Features

### 🤖 Multi-Agent Architecture
- **Room Agents**: Monitor individual rooms for occupancy, equipment, and comfort
- **Building Agents**: Aggregate room data and coordinate building-level optimization
- **Campus Agent**: Generate campus-wide sustainability strategies

### 🎛️ User-Controlled Execution
- Set number of rooms and buildings to analyze
- Configure API budget (Low/Medium/High) to control costs
- Adjust environmental parameters (occupancy, temperature, equipment)
- Run analysis only on-demand - no automatic background execution

### 📊 Comprehensive Parameters
- **Occupancy Control**: Set average room occupancy (0-50 people)
- **Equipment Simulation**: Lights, AC, fans, projectors, computers
- **Environmental Conditions**: Outdoor temperature, time of day
- **HVAC Settings**: AC temperature control (18-28°C)

### 🔮 What-If Scenarios
- Close buildings after hours
- Reduce HVAC in low-occupancy areas
- Consolidate classes to fewer buildings
- Compare multiple scenarios side-by-side

### 📈 Analytics Dashboard
- Real-time energy and water consumption metrics
- Building-level performance analysis
- Savings potential calculations
- Critical alerts and recommendations

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                 Campus Agent                         │
│            (Campus-wide Strategy)                    │
└────────────────┬────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
┌───────▼──────┐  ┌──────▼────────┐
│Building Agent│  │Building Agent │
│   (Library)  │  │  (Science)    │
└───────┬──────┘  └──────┬────────┘
        │                │
   ┌────┴───┐       ┌────┴───┐
   │        │       │        │
┌──▼──┐ ┌──▼──┐ ┌──▼──┐ ┌──▼──┐
│Room │ │Room │ │Room │ │Room │
│Agent│ │Agent│ │Agent│ │Agent│
└─────┘ └─────┘ └─────┘ └─────┘
```

### Agent Responsibilities

#### Room Agent (LangGraph State Machine)
- Analyzes current observations (occupancy, temperature, equipment)
- Infers hidden variables (energy, CO2, water usage)
- Predicts future demand patterns
- Generates optimization recommendations
- Detects anomalies and inefficiencies

#### Building Agent
- Aggregates data from all room agents
- Identifies building-level patterns
- Coordinates inter-room optimizations
- Calculates building-wide savings potential

#### Campus Agent
- Synthesizes insights from all buildings
- Generates campus-wide policy recommendations
- Identifies critical buildings and priorities
- Calculates total environmental impact

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **AI/ML**: LangChain, LangGraph, Groq LLM
- **State Management**: LangGraph StateGraph
- **Async Processing**: asyncio, uvicorn

### Frontend
- **Framework**: React 18.3+ with Vite
- **UI Components**: Lucide React icons
- **Styling**: Custom CSS with gradient animations
- **API Client**: Axios

### Key Libraries
- `langchain-groq`: Groq API integration
- `langgraph`: Agent state machine orchestration
- `pydantic`: Data validation
- `python-dotenv`: Environment configuration

## 📦 Installation

### Prerequisites
- Python 3.11 or higher
- Node.js 18+ and npm
- Groq API key ([Get one here](https://console.groq.com/keys))

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/EcoAgent.git
cd EcoAgent
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env  # Windows
# or
cp .env.example .env    # macOS/Linux
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install
```

## ⚙️ Configuration

### Backend Configuration (`backend/.env`)
```env
# Groq API Key (Required)
GROQ_API_KEY=your_api_key_here

# Agent Model Configuration
AGENT_MODEL=llama-3.3-70b-versatile
AGENT_TEMPERATURE=0.7

# API Server Settings
API_HOST=0.0.0.0
API_PORT=8000

# Optional: Enable debug mode
DEBUG=True
```

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Your Groq API key | *Required* |
| `AGENT_MODEL` | Groq model to use | `llama-3.3-70b-versatile` |
| `AGENT_TEMPERATURE` | LLM temperature (0-1) | `0.7` |
| `API_HOST` | Backend server host | `0.0.0.0` |
| `API_PORT` | Backend server port | `8000` |

## 🚀 Usage

### Starting the Backend
```bash
cd backend
python main.py
```
Backend will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Starting the Frontend
```bash
cd frontend
npm run dev
```
Frontend will be available at: `http://localhost:5173`

### Running Analysis

1. **Configure Parameters** (Dashboard):
   - Set number of rooms (5-50)
   - Set number of buildings (1-5)
   - Choose API budget level (Low/Medium/High)
   - Configure room conditions:
     - Average occupancy
     - AC temperature
     - Equipment (lights, AC, fans, computers, projectors)
     - Time of day and outdoor temperature

2. **Run Analysis**:
   - Click "▶️ Run Campus Analysis"
   - Watch agent execution progress
   - View results and recommendations

3. **What-If Scenarios** (Simulation Tab):
   - Select a pre-configured scenario
   - Adjust parameters
   - Click "Run Simulation"
   - Compare baseline vs. simulated results

## 📚 API Documentation

### Main Endpoints

#### Campus Analysis
```http
GET /api/analysis/current
```
**Query Parameters:**
- `num_rooms` (int, optional): Number of rooms to analyze
- `num_buildings` (int, optional): Number of buildings to analyze
- `budget_level` (string): `low` | `medium` | `high`
- `avg_occupancy` (int): Average people per room
- `ac_temperature` (int): AC temperature in Celsius
- `lights_on` (bool): Whether lights are on
- `ac_on` (bool): Whether AC is running
- `fans_on` (bool): Whether fans are on
- `computers_count` (int): Number of computers per room
- `projectors_on_percent` (int): % of rooms with projectors
- `time_of_day` (string): Time period
- `outdoor_temperature` (int): Outdoor temp in Celsius

**Response:**
```json
{
  "campus_name": "State University Campus",
  "timestamp": "2026-01-28T10:30:00",
  "summary": {
    "total_buildings": 2,
    "total_rooms": 10,
    "total_energy_kw": 125.5,
    "total_water_lph": 45.2,
    "occupancy_rate": 65.3
  },
  "savings_potential": {
    "total_kwh_saved": 25.5,
    "estimated_cost_savings_hourly": 3.06
  },
  "building_states": { ... },
  "campus_recommendations": [ ... ],
  "execution_info": {
    "rooms_analyzed": 10,
    "buildings_analyzed": 2,
    "budget_level": "low"
  }
}
```

#### What-If Simulation
```http
POST /api/simulation/run
```
**Request Body:**
```json
{
  "name": "Close Building After 8 PM",
  "type": "close_building",
  "building_id": "lib",
  "parameters": {
    "num_rooms": 10,
    "num_buildings": 2,
    "budget_level": "low"
  }
}
```

#### Health Check
```http
GET /health
```

## 📁 Project Structure

```
EcoAgent/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── room_agent.py           # Room-level LangGraph agent
│   │   ├── building_agent.py       # Building aggregation
│   │   └── campus_graph.py         # Campus orchestration
│   ├── api/
│   │   ├── routes/
│   │   │   ├── analysis.py         # Analysis endpoints
│   │   │   ├── simulation.py       # What-if scenarios
│   │   │   └── campus.py           # Campus data endpoints
│   │   ├── data_service.py         # Data management
│   │   └── dependencies.py         # Dependency injection
│   ├── config.py                   # Configuration management
│   ├── main.py                     # FastAPI application
│   └── requirements.txt            # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx       # Main dashboard
│   │   │   ├── Simulation.jsx      # What-if scenarios
│   │   │   ├── BuildingCard.jsx    # Building display
│   │   │   └── RecommendationPanel.jsx
│   │   ├── services/
│   │   │   ├── api.js              # API client
│   │   │   └── mockData.js         # Demo mode data
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 🎭 Demo Mode

EcoAgent includes a **frontend-only demo mode** that works without a backend server. This is perfect for:
- Quick demonstrations
- Testing UI changes
- Offline presentations
- API key conservation

When the backend is unavailable, the frontend automatically:
- Generates realistic mock data
- Simulates agent execution
- Respects all user parameters
- Provides full UI functionality

The demo banner will indicate: "🌑 Demo" mode.

## 🎯 Use Cases

### Educational Institutions
- Monitor energy usage across campus buildings
- Identify inefficient buildings and rooms
- Optimize HVAC schedules based on class schedules
- Reduce operational costs by 15-30%

### Office Buildings
- Track real-time occupancy and adjust climate control
- Consolidate after-hours activities
- Detect equipment left running unnecessarily
- Generate sustainability reports

### Research & Testing
- Test different energy policies before implementation
- Compare multiple optimization strategies
- Analyze impact of behavioral changes
- Demonstrate AI agent capabilities

## 🔒 API Key Management

**Important**: The system is designed to conserve API usage:
- ✅ No automatic agent execution
- ✅ User controls when analysis runs
- ✅ Configurable budget levels (Low = fewer LLM calls)
- ✅ Limited room/building analysis options
- ✅ Demo mode when backend is offline

**Recommended Settings for Demonstrations:**
- 10 rooms, 2 buildings, Low budget
- ~5-8 API calls per analysis
- Fast execution (~10-15 seconds)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Guidelines
1. Follow existing code style
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass
5. Keep commits atomic and well-described

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://www.langchain.com/) and [LangGraph](https://github.com/langchain-ai/langgraph)
- Powered by [Groq](https://groq.com/)
- UI inspired by modern sustainability dashboards

## 📞 Contact

For questions, issues, or suggestions, please open an issue on GitHub.

---

<div align="center">
  <strong>Built with 💚 for a sustainable future</strong>
</div>
