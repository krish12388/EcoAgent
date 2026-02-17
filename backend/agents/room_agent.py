"""Room Agent using LangGraph for stateful resource management."""
from typing import TypedDict, Annotated, Sequence, List, Dict, Any
from datetime import datetime
import operator

from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from config import settings


class RoomState(TypedDict):
    """State structure for a room agent."""
    # Room Identity
    room_id: str
    room_type: str  # classroom, lab, library, dorm, bathroom, cafeteria
    building_id: str
    floor: int
    capacity: int
    
    # Current Observations (from dataset)
    current_occupancy: int
    occupancy_level: str  # low, medium, high
    temperature_comfort: str  # too_cold, comfortable, too_hot
    equipment_running: List[str]  # e.g., ["projector", "computers", "lights"]
    water_running: bool
    
    # Historical Context
    occupancy_history: List[Dict[str, Any]]  # last 24 hours
    energy_history: List[Dict[str, Any]]
    water_history: List[Dict[str, Any]]
    
    # Inferred State
    estimated_energy_kw: float
    estimated_water_lph: float  # liters per hour
    estimated_co2_ppm: int
    thermal_load: str  # heating, cooling, neutral
    
    # Predictions
    predicted_occupancy_1h: int
    predicted_energy_1h: float
    predicted_peak_time: str
    
    # Recommendations
    recommendations: List[str]
    anomalies: List[str]
    savings_potential: float  # percentage
    
    # Agent Communication
    messages: Annotated[Sequence[BaseMessage], operator.add]
    
    # Metadata
    last_updated: str


class RoomAgent:
    """
    Intelligent room agent using LangGraph.
    
    Each room has its own agent that:
    1. Analyzes current state from observations
    2. Infers hidden variables (energy, CO2, water)
    3. Predicts future demand
    4. Generates optimization recommendations
    """
    
    def __init__(self, room_id: str, room_config: Dict[str, Any]):
        self.room_id = room_id
        self.room_config = room_config
        self.budget_level = 'medium'  # Default budget level
        self.llm = ChatGroq(
            model=settings.agent_model,
            temperature=settings.agent_temperature,
            api_key=settings.groq_api_key
        )
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the agent's reasoning graph."""
        workflow = StateGraph(RoomState)
        
        # Add nodes for different reasoning steps
        workflow.add_node("analyze_observations", self._analyze_observations)
        workflow.add_node("infer_resources", self._infer_resources)
        workflow.add_node("predict_demand", self._predict_demand)
        workflow.add_node("generate_recommendations", self._generate_recommendations)
        
        # Define the flow
        workflow.set_entry_point("analyze_observations")
        workflow.add_edge("analyze_observations", "infer_resources")
        workflow.add_edge("infer_resources", "predict_demand")
        workflow.add_edge("predict_demand", "generate_recommendations")
        workflow.add_edge("generate_recommendations", END)
        
        return workflow.compile()
    
    def _analyze_observations(self, state: RoomState) -> RoomState:
        """Analyze current room observations."""
        # For low budget, skip LLM and use heuristics only
        if self.budget_level == 'low':
            # Simple heuristic-based anomaly detection
            anomalies = []
            if state['temperature_comfort'] != 'comfortable':
                anomalies.append(f"Temperature discomfort: {state['temperature_comfort']}")
            if state['current_occupancy'] < state['capacity'] * 0.2 and len(state.get('equipment_running', [])) > 2:
                anomalies.append(f"Low occupancy ({state['current_occupancy']}) but multiple equipment running")
            
            return {
                **state,
                "anomalies": anomalies,
                "last_updated": datetime.now().isoformat()
            }
        
        # For medium/high budget, use LLM
        # Build context for LLM
        context = f"""
You are analyzing room {state['room_id']} ({state['room_type']}).

Current Observations:
- Occupancy: {state['current_occupancy']}/{state['capacity']} ({state['occupancy_level']})
- Temperature: {state['temperature_comfort']}
- Equipment: {', '.join(state['equipment_running']) if state['equipment_running'] else 'None'}
- Water: {'Running' if state.get('water_running', False) else 'Off'}

Room Type Profile: {self._get_room_type_profile(state['room_type'])}

Task: Analyze if current conditions are normal or anomalous for this room type and time.
"""
        
        messages = list(state.get("messages", []))
        messages.append(HumanMessage(content=context))
        
        response = self.llm.invoke(messages)
        messages.append(response)
        
        # Parse anomalies from response
        anomalies = self._extract_anomalies(response.content)
        
        return {
            **state,
            "messages": messages,
            "anomalies": anomalies,
            "last_updated": datetime.now().isoformat()
        }
    
    def _infer_resources(self, state: RoomState) -> RoomState:
        """Infer energy, water, CO2 from observations."""
        room_type = state['room_type']
        occupancy = state['current_occupancy']
        equipment = state.get('equipment_running', [])
        
        # Base inference logic (can be enhanced with LLM)
        energy_kw = self._calculate_energy(room_type, occupancy, equipment)
        water_lph = self._calculate_water(room_type, state.get('water_running', False))
        co2_ppm = self._calculate_co2(occupancy, state['capacity'])
        thermal_load = self._determine_thermal_load(state['temperature_comfort'])
        
        # Use LLM for context-aware inference
        inference_prompt = f"""
Based on the room analysis, refine these resource estimates:

Room: {state['room_type']} with {occupancy} people (capacity: {state['capacity']})
Equipment: {', '.join(equipment) if equipment else 'None'}
Temperature: {state['temperature_comfort']}

Initial Estimates:
- Energy: {energy_kw:.2f} kW
- Water: {water_lph:.2f} L/h
- CO2: {co2_ppm} ppm
- Thermal Load: {thermal_load}

Consider:
1. Are these estimates realistic for this room type?
2. Are there hidden energy loads (HVAC working harder due to discomfort)?
3. Any unusual patterns?

Provide refined estimates with brief reasoning.
"""
        
        messages = list(state.get("messages", []))
        messages.append(HumanMessage(content=inference_prompt))
        
        response = self.llm.invoke(messages)
        messages.append(response)
        
        return {
            **state,
            "estimated_energy_kw": energy_kw,
            "estimated_water_lph": water_lph,
            "estimated_co2_ppm": co2_ppm,
            "thermal_load": thermal_load,
            "messages": messages
        }
    
    def _predict_demand(self, state: RoomState) -> RoomState:
        """Predict future resource demand."""
        current_time = datetime.now()
        hour = current_time.hour
        
        # Use historical patterns + LLM reasoning
        prediction_prompt = f"""
Predict resource demand for the next 1 hour.

Current State (at {hour}:00):
- Occupancy: {state['current_occupancy']} ({state['occupancy_level']})
- Energy: {state['estimated_energy_kw']:.2f} kW
- Room Type: {state['room_type']}

Historical Pattern (last 24h):
{self._format_history(state.get('occupancy_history', []))}

Predict:
1. Occupancy in 1 hour
2. Energy demand in 1 hour  
3. Peak usage time today

Consider: day of week, time of day, room type typical schedule.
Provide numeric predictions.
"""
        
        messages = list(state.get("messages", []))
        messages.append(HumanMessage(content=prediction_prompt))
        
        response = self.llm.invoke(messages)
        messages.append(response)
        
        # Simple heuristic prediction (enhance with LLM parsing)
        predicted_occupancy = self._predict_occupancy_heuristic(state)
        predicted_energy = predicted_occupancy / state['capacity'] * self._get_max_energy(state['room_type'])
        
        return {
            **state,
            "predicted_occupancy_1h": predicted_occupancy,
            "predicted_energy_1h": predicted_energy,
            "predicted_peak_time": self._find_peak_time(state),
            "messages": messages
        }
    
    def _generate_recommendations(self, state: RoomState) -> RoomState:
        """Generate optimization recommendations."""
        # For low budget, use simple rule-based recommendations
        if self.budget_level == 'low':
            recommendations = []
            
            if state['temperature_comfort'] != 'comfortable':
                recommendations.append(f"ACTION: Adjust HVAC to reach comfortable temperature (est. 10% savings)")
            
            occupancy_ratio = state['current_occupancy'] / max(state['capacity'], 1)
            if occupancy_ratio < 0.3 and state['estimated_energy_kw'] > 2.0:
                recommendations.append(f"ACTION: Reduce lighting and equipment in low-occupancy room (est. 15% savings)")
            
            if state.get('water_running') and state['room_type'] not in ['bathroom', 'cafeteria']:
                recommendations.append(f"ACTION: Check for water leaks or unnecessary usage (est. 20% savings)")
            
            if not recommendations:
                recommendations.append("No immediate actions needed - room operating efficiently")
            
            savings_potential = self._calculate_savings_potential(state)
            
            return {
                **state,
                "recommendations": recommendations,
                "savings_potential": savings_potential
            }
        
        # For medium/high budget, use LLM
        recommendation_prompt = f"""
You are an energy optimization expert. Generate actionable recommendations.

Room Analysis Summary:
- Room: {state['room_id']} ({state['room_type']})
- Current Energy: {state['estimated_energy_kw']:.2f} kW
- Predicted 1h: {state['predicted_energy_1h']:.2f} kW
- Comfort: {state['temperature_comfort']}
- Occupancy: {state['current_occupancy']}/{state['capacity']}
- Anomalies: {', '.join(state['anomalies']) if state['anomalies'] else 'None'}

Generate 3-5 specific recommendations:
1. Immediate actions (next 1 hour)
2. Energy/water savings opportunities
3. Comfort improvements
4. Predictive adjustments

Format each as: "ACTION: specific recommendation (estimated X% savings)"
"""
        
        messages = list(state.get("messages", []))
        messages.append(HumanMessage(content=recommendation_prompt))
        
        response = self.llm.invoke(messages)
        messages.append(response)
        
        # Parse recommendations
        recommendations = self._parse_recommendations(response.content)
        savings_potential = self._calculate_savings_potential(state)
        
        return {
            **state,
            "recommendations": recommendations,
            "savings_potential": savings_potential,
            "messages": messages
        }
    
    # Helper methods
    def _get_room_type_profile(self, room_type: str) -> str:
        """Get expected behavior profile for room type."""
        profiles = {
            "classroom": "Scheduled usage, 9AM-5PM peaks, equipment varies by class",
            "lab": "High baseline energy, specialized equipment, irregular hours",
            "library": "Steady occupancy, long sessions, quiet hours after 10PM",
            "dorm": "Residential 24/7, evening/night peaks, personal electronics",
            "bathroom": "Short visits, water-centric, hygiene equipment",
            "cafeteria": "Meal-time peaks (7-9AM, 12-2PM, 6-8PM), high water/energy"
        }
        return profiles.get(room_type, "General purpose space")
    
    def _calculate_energy(self, room_type: str, occupancy: int, equipment: List[str]) -> float:
        """Calculate estimated energy consumption."""
        base_energy = {
            "classroom": 2.0,
            "lab": 8.0,
            "library": 3.0,
            "dorm": 1.5,
            "bathroom": 1.0,
            "cafeteria": 15.0
        }.get(room_type, 2.0)
        
        # Add equipment load
        equipment_load = len(equipment) * 0.5
        
        # Add occupancy factor
        occupancy_load = occupancy * 0.1
        
        return base_energy + equipment_load + occupancy_load
    
    def _calculate_water(self, room_type: str, water_running: bool) -> float:
        """Calculate water usage in liters per hour."""
        if not water_running:
            return 0.0
        
        usage_rates = {
            "bathroom": 120.0,  # Multiple fixtures
            "cafeteria": 200.0,  # Dishwashing, cooking
            "lab": 50.0,
            "classroom": 10.0
        }
        return usage_rates.get(room_type, 0.0)
    
    def _calculate_co2(self, occupancy: int, capacity: int) -> int:
        """Calculate estimated CO2 levels."""
        base_co2 = 400  # Outdoor ambient
        per_person = 100  # CO2 contribution per person
        crowding_factor = (occupancy / max(capacity, 1)) * 200
        
        return int(base_co2 + (occupancy * per_person) + crowding_factor)
    
    def _determine_thermal_load(self, comfort: str) -> str:
        """Determine if HVAC should heat or cool."""
        if comfort == "too_cold":
            return "heating"
        elif comfort == "too_hot":
            return "cooling"
        return "neutral"
    
    def _extract_anomalies(self, llm_response: str) -> List[str]:
        """Extract anomalies from LLM response."""
        # Simple keyword extraction (can be enhanced)
        anomaly_keywords = ["unusual", "anomaly", "unexpected", "high", "waste"]
        anomalies = []
        
        for line in llm_response.split('\n'):
            if any(keyword in line.lower() for keyword in anomaly_keywords):
                anomalies.append(line.strip())
        
        return anomalies[:3]  # Top 3
    
    def _format_history(self, history: List[Dict]) -> str:
        """Format historical data for LLM."""
        if not history:
            return "No historical data available"
        
        return "\n".join([
            f"  {h.get('time', 'N/A')}: {h.get('occupancy', 0)} people"
            for h in history[-5:]  # Last 5 entries
        ])
    
    def _predict_occupancy_heuristic(self, state: RoomState) -> int:
        """Simple heuristic for occupancy prediction."""
        current = state['current_occupancy']
        capacity = state['capacity']
        
        # Simple trend: assume slight decrease off-peak, increase at peak
        hour = datetime.now().hour
        
        if 9 <= hour < 17:  # Peak hours
            return min(int(current * 1.1), capacity)
        else:
            return max(int(current * 0.8), 0)
    
    def _get_max_energy(self, room_type: str) -> float:
        """Maximum energy for room at full capacity."""
        return {
            "classroom": 5.0,
            "lab": 15.0,
            "library": 6.0,
            "dorm": 3.0,
            "bathroom": 2.0,
            "cafeteria": 30.0
        }.get(room_type, 5.0)
    
    def _find_peak_time(self, state: RoomState) -> str:
        """Find predicted peak usage time."""
        room_type = state['room_type']
        
        peak_times = {
            "classroom": "10:00-11:00",
            "lab": "14:00-16:00",
            "library": "19:00-21:00",
            "dorm": "21:00-23:00",
            "bathroom": "08:00-09:00",
            "cafeteria": "12:00-13:00"
        }
        
        return peak_times.get(room_type, "12:00-13:00")
    
    def _parse_recommendations(self, llm_response: str) -> List[str]:
        """Parse recommendations from LLM response."""
        recommendations = []
        
        for line in llm_response.split('\n'):
            if line.strip() and ('ACTION:' in line or any(c.isdigit() and '%' in line for c in line)):
                recommendations.append(line.strip())
        
        return recommendations[:5]  # Top 5
    
    def _calculate_savings_potential(self, state: RoomState) -> float:
        """Calculate potential savings percentage."""
        # Simple heuristic based on anomalies and inefficiencies
        savings = 0.0
        
        if state['anomalies']:
            savings += len(state['anomalies']) * 5.0
        
        if state['temperature_comfort'] != 'comfortable':
            savings += 10.0
        
        occupancy_ratio = state['current_occupancy'] / max(state['capacity'], 1)
        if occupancy_ratio < 0.3 and state['estimated_energy_kw'] > 2.0:
            savings += 15.0  # Low occupancy but high energy
        
        return min(savings, 40.0)  # Cap at 40%
    
    def run(self, initial_state: RoomState) -> RoomState:
        """Run the agent's reasoning pipeline."""
        return self.graph.invoke(initial_state)
    
    async def run_async(self, initial_state: RoomState) -> RoomState:
        """Async version for concurrent execution."""
        return await self.graph.ainvoke(initial_state)
