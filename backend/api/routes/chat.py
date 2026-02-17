"""Chat endpoint - AI assistant for analysis reports."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from config import settings

router = APIRouter()


class ChatMessage(BaseModel):
    """Chat message."""
    role: str  # 'user' or 'assistant'
    content: str


class ChatRequest(BaseModel):
    """Chat request with context."""
    message: str
    analysis_data: Dict[str, Any]  # The analysis/report data
    chat_history: List[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    """Chat response."""
    message: str
    chat_history: List[ChatMessage]


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest) -> ChatResponse:
    """
    Send a message to the AI assistant about the analysis report.
    The assistant has context of the current analysis data.
    """
    try:
        # Initialize Groq LLM
        if not settings.groq_api_key:
            return ChatResponse(
                message="⚠️ Groq API key not configured. Please set GROQ_API_KEY in your environment or .env file.",
                chat_history=request.chat_history + [
                    ChatMessage(role="user", content=request.message),
                    ChatMessage(role="assistant", content="⚠️ Groq API key not configured. Please set GROQ_API_KEY in your environment or .env file.")
                ]
            )
        
        try:
            llm = ChatGroq(
                model=settings.agent_model,
                temperature=settings.agent_temperature,
                api_key=settings.groq_api_key
            )
        except Exception as e:
            return ChatResponse(
                message=f"⚠️ Failed to initialize Groq: {str(e)}",
                chat_history=request.chat_history + [
                    ChatMessage(role="user", content=request.message),
                    ChatMessage(role="assistant", content=f"⚠️ Failed to initialize Groq: {str(e)}")
                ]
            )
        
        # Create system prompt with analysis context
        analysis_summary = _create_analysis_summary(request.analysis_data)
        
        system_prompt = f"""You are a helpful sustainability AI assistant for a campus energy management system called EcoAgent. 

You have access to the COMPLETE analysis data below. ALWAYS use this data to answer questions. DO NOT say data is unavailable when it's provided below.

{analysis_summary}

Your role is to:
- Answer questions DIRECTLY using the data provided above
- When asked about savings potential, use the percentage and kW values shown in the data
- Explain what the metrics mean and their implications
- Provide actionable insights based on the recommendations
- Be specific and reference actual numbers from the data
- Keep responses brief (2-4 sentences) unless asked for details

IMPORTANT: The data above contains all the information you need. Reference specific numbers when answering."""

        # Convert chat history to LangChain messages
        messages = [SystemMessage(content=system_prompt)]
        
        for msg in request.chat_history:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))
        
        # Add current user message
        messages.append(HumanMessage(content=request.message))
        
        # Get response from LLM
        response = llm.invoke(messages)
        assistant_message = response.content
        
        # Update chat history
        new_history = request.chat_history + [
            ChatMessage(role="user", content=request.message),
            ChatMessage(role="assistant", content=assistant_message)
        ]
        
        return ChatResponse(
            message=assistant_message,
            chat_history=new_history
        )
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        # Return user-friendly error instead of raising exception
        error_message = f"⚠️ Chat error: {str(e)}. Make sure your Groq API key is configured correctly."
        return ChatResponse(
            message=error_message,
            chat_history=request.chat_history + [
                ChatMessage(role="user", content=request.message),
                ChatMessage(role="assistant", content=error_message)
            ]
        )


def _create_analysis_summary(data: Dict[str, Any]) -> str:
    """Create a concise summary of the analysis data for the AI."""
    summary_parts = []
    
    # Campus metrics
    if "campus_metrics" in data:
        metrics = data["campus_metrics"]
        total_energy = metrics.get('total_energy_kw', 'N/A')
        savings_pct = metrics.get('potential_savings_percent', 'N/A')
        cost_per_hour = metrics.get('estimated_cost_per_hour', 'N/A')
        
        # Calculate potential savings
        if isinstance(total_energy, (int, float)) and isinstance(savings_pct, (int, float)):
            potential_energy_savings = round(total_energy * (savings_pct / 100), 2)
            if isinstance(cost_per_hour, (int, float)):
                potential_cost_savings = round(cost_per_hour * (savings_pct / 100), 2)
            else:
                potential_cost_savings = 'N/A'
        else:
            potential_energy_savings = 'N/A'
            potential_cost_savings = 'N/A'
        
        summary_parts.append(f"""CAMPUS OVERVIEW:
- Current Total Energy Usage: {total_energy} kW
- Total Occupancy: {metrics.get('total_occupancy', 'N/A')} people
- Water Usage: {metrics.get('total_water_lph', 'N/A')} L/hr
- Current Cost: ${cost_per_hour}/hour
- SAVINGS POTENTIAL: {savings_pct}% (this means {potential_energy_savings} kW or ${potential_cost_savings}/hour can be saved)
- Average Occupancy Rate: {metrics.get('avg_occupancy_rate', 'N/A')}%""")
    
    # Building states with detailed savings info
    if "building_states" in data:
        buildings = data["building_states"]
        summary_parts.append(f"\nBUILDINGS ANALYZED ({len(buildings)} total):")
        for bid, bdata in list(buildings.items())[:3]:  # First 3 buildings
            savings = bdata.get('savings_potential', 'N/A')
            energy = bdata.get('total_energy_kw', 'N/A')
            summary_parts.append(f"- {bid}:")
            summary_parts.append(f"  * Energy: {energy} kW")
            summary_parts.append(f"  * Occupancy: {bdata.get('occupancy_rate', 'N/A')}%")
            summary_parts.append(f"  * Savings Potential: {savings}%")
            if isinstance(energy, (int, float)) and isinstance(savings, (int, float)):
                potential = round(energy * (savings / 100), 2)
                summary_parts.append(f"  * Can save: {potential} kW")
    
    # Recommendations with context
    if "campus_recommendations" in data:
        recs = data["campus_recommendations"]
        summary_parts.append(f"\nTOP RECOMMENDATIONS FOR SAVINGS:")
        for i, rec in enumerate(recs[:5], 1):
            summary_parts.append(f"{i}. {rec}")
    
    # Critical buildings
    if "critical_buildings" in data and data["critical_buildings"]:
        summary_parts.append(f"\nHIGH PRIORITY BUILDINGS (need immediate attention):")
        for building in data["critical_buildings"][:3]:
            summary_parts.append(f"- {building.get('building_id', 'N/A')}: {building.get('reason', 'N/A')} ({building.get('energy_kw', 'N/A')} kW)")
    
    # Execution info
    if "execution_info" in data:
        info = data["execution_info"]
        summary_parts.append(f"\nANALYSIS SCOPE: {info.get('rooms_analyzed', 'N/A')} rooms across {info.get('buildings_analyzed', 'N/A')} buildings")
    
    return "\n".join(summary_parts)


@router.get("/models")
async def check_models() -> Dict[str, Any]:
    """Check Groq configuration status."""
    groq_configured = bool(settings.groq_api_key)
    
    return {
        "provider": "Groq",
        "configured": groq_configured,
        "model": settings.agent_model,
        "instructions": "Set GROQ_API_KEY environment variable to enable chat" if not groq_configured else "Groq is configured and ready"
    }


@router.post("/clear")
async def clear_history() -> Dict[str, str]:
    """Clear chat history (frontend manages history)."""
    return {"status": "cleared", "message": "Chat history cleared"}
