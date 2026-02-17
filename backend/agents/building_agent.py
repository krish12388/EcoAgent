"""Building Agent - aggregates room agents."""
from typing import Dict, List, Any
from datetime import datetime

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from config import settings


class BuildingAgent:
    """
    Building-level agent that aggregates room agent outputs.
    
    Responsibilities:
    1. Aggregate resource consumption across all rooms
    2. Identify building-level patterns
    3. Coordinate inter-room optimizations
    4. Generate building-wide recommendations
    """
    
    def __init__(self, building_id: str, building_config: Dict[str, Any]):
        self.building_id = building_id
        self.building_config = building_config
        self.llm = ChatGroq(
            model=settings.agent_model,
            temperature=settings.agent_temperature,
            api_key=settings.groq_api_key
        )
        self.room_agents = {}
    
    def add_room_agent(self, room_id: str, room_agent):
        """Register a room agent to this building."""
        self.room_agents[room_id] = room_agent
    
    def aggregate_building_state(self, room_states: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate all room states into building-level metrics."""
        total_energy = sum(r.get('estimated_energy_kw', 0) for r in room_states)
        total_water = sum(r.get('estimated_water_lph', 0) for r in room_states)
        total_occupancy = sum(r.get('current_occupancy', 0) for r in room_states)
        total_capacity = sum(r.get('capacity', 0) for r in room_states)
        
        avg_co2 = sum(r.get('estimated_co2_ppm', 400) for r in room_states) / max(len(room_states), 1)
        
        # Aggregate anomalies
        all_anomalies = []
        for room in room_states:
            for anomaly in room.get('anomalies', []):
                all_anomalies.append(f"{room['room_id']}: {anomaly}")
        
        # Collect all recommendations
        all_recommendations = []
        for room in room_states:
            for rec in room.get('recommendations', []):
                all_recommendations.append(f"{room['room_id']}: {rec}")
        
        occupancy_rate = (total_occupancy / max(total_capacity, 1)) * 100
        
        return {
            "building_id": self.building_id,
            "building_name": self.building_config.get('name', self.building_id),
            "total_rooms": len(room_states),
            "total_energy_kw": round(total_energy, 2),
            "total_water_lph": round(total_water, 2),
            "total_occupancy": total_occupancy,
            "total_capacity": total_capacity,
            "occupancy_rate": round(occupancy_rate, 1),
            "avg_co2_ppm": int(avg_co2),
            "room_states": room_states,
            "anomalies": all_anomalies,
            "room_recommendations": all_recommendations,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_building_recommendations(self, building_state: Dict[str, Any]) -> List[str]:
        """Generate building-level optimization recommendations using LLM."""
        prompt = f"""
You are optimizing {building_state['building_name']} with {building_state['total_rooms']} rooms.

Current Building Metrics:
- Total Energy: {building_state['total_energy_kw']} kW
- Total Water: {building_state['total_water_lph']} L/h
- Occupancy: {building_state['total_occupancy']}/{building_state['total_capacity']} ({building_state['occupancy_rate']}%)
- Average CO2: {building_state['avg_co2_ppm']} ppm

Building-Level Anomalies:
{self._format_list(building_state.get('anomalies', [])[:5])}

Room-Level Recommendations:
{self._format_list(building_state.get('room_recommendations', [])[:5])}

Generate 5 building-wide recommendations considering:
1. Can we coordinate HVAC across floors?
2. Should we close sections of the building?
3. Are there load-balancing opportunities?
4. Can we shift usage patterns?
5. Emergency responses needed?

Format: "BUILDING ACTION: [specific action] (estimated impact)"
"""
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        recommendations = []
        for line in response.content.split('\n'):
            if 'BUILDING ACTION:' in line or any(c.isdigit() and '%' in line for c in line):
                recommendations.append(line.strip())
        
        return recommendations[:5]
    
    def calculate_building_savings(self, building_state: Dict[str, Any]) -> Dict[str, float]:
        """Calculate potential savings at building level."""
        room_savings = [r.get('savings_potential', 0) for r in building_state['room_states']]
        avg_room_savings = sum(room_savings) / max(len(room_savings), 1)
        
        # Building-level additional savings
        building_coordination_savings = 0.0
        
        # Low occupancy bonus
        if building_state['occupancy_rate'] < 30:
            building_coordination_savings += 10.0
        
        # Time-based savings
        hour = datetime.now().hour
        if hour > 20 or hour < 6:  # Night hours
            building_coordination_savings += 15.0
        
        total_savings_potential = avg_room_savings + building_coordination_savings
        
        return {
            "room_level_savings": round(avg_room_savings, 1),
            "building_level_savings": round(building_coordination_savings, 1),
            "total_potential_savings": round(min(total_savings_potential, 50.0), 1),
            "estimated_kwh_saved": round(building_state['total_energy_kw'] * total_savings_potential / 100, 2),
            "estimated_water_saved_lph": round(building_state['total_water_lph'] * total_savings_potential / 100, 2)
        }
    
    def _format_list(self, items: List[str]) -> str:
        """Format list for LLM prompt."""
        if not items:
            return "  None"
        return "\n".join([f"  - {item}" for item in items])
    
    def analyze_building(self, room_states: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Complete building analysis pipeline."""
        # Aggregate state
        building_state = self.aggregate_building_state(room_states)
        
        # Generate recommendations
        building_recommendations = self.generate_building_recommendations(building_state)
        
        # Calculate savings
        savings = self.calculate_building_savings(building_state)
        
        # Combine results
        building_state['building_recommendations'] = building_recommendations
        building_state['savings_analysis'] = savings
        
        return building_state
