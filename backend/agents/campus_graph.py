"""Campus-wide agent graph orchestration."""
from typing import Dict, List, Any
import asyncio
from datetime import datetime

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from .room_agent import RoomAgent, RoomState
from .building_agent import BuildingAgent
from config import settings


class CampusAgentGraph:
    """
    Campus-level orchestration of all agents.
    
    Architecture:
    Campus Agent
    ├── Building Agent 1
    │   ├── Room Agent 1.1
    │   ├── Room Agent 1.2
    │   └── ...
    ├── Building Agent 2
    │   └── ...
    └── ...
    
    Execution Flow:
    1. Load campus data
    2. Run all room agents in parallel
    3. Aggregate at building level
    4. Generate campus-wide insights
    """
    
    def __init__(self):
        self.llm = ChatGroq(
            model=settings.agent_model,
            temperature=settings.agent_temperature,
            api_key=settings.groq_api_key
        )
        self.building_agents: Dict[str, BuildingAgent] = {}
        self.room_agents: Dict[str, RoomAgent] = {}
        self.campus_config = {}
        self.campus_data = {}  # Store full campus data for lazy initialization
    
    def set_campus_data(self, campus_data: Dict[str, Any]):
        """Store campus data without creating agents (lazy initialization)."""
        self.campus_data = campus_data
        self.campus_config = campus_data.get('campus_info', {})
        print(f"📦 Campus data loaded (agents will be created on-demand)")
    
    def _ensure_agents_for_rooms(self, room_ids: List[str]):
        """Create agents only for the specified rooms and their buildings."""
        print(f"🔍 DEBUG: Received {len(room_ids)} room_ids to analyze: {room_ids[:5]}...")
        
        # Clear old agents that are not needed for this analysis
        rooms_to_keep = set(room_ids)
        old_room_count = len(self.room_agents)
        self.room_agents = {rid: agent for rid, agent in self.room_agents.items() if rid in rooms_to_keep}
        print(f"🧹 Cleared {old_room_count - len(self.room_agents)} old room agents, kept {len(self.room_agents)}")
        
        buildings_needed = set()
        
        # Create room agents if they don't exist
        for room_id in room_ids:
            if room_id not in self.room_agents:
                room_config = self.campus_data.get('rooms', {}).get(room_id)
                if room_config:
                    room_agent = RoomAgent(room_id, room_config)
                    self.room_agents[room_id] = room_agent
                    buildings_needed.add(room_config.get('building_id'))
            else:
                # Room agent already exists, add its building to needed set
                room_config = self.campus_data.get('rooms', {}).get(room_id)
                if room_config:
                    buildings_needed.add(room_config.get('building_id'))
        
        print(f"🏢 DEBUG: Buildings needed: {buildings_needed}")
        
        # Clear old building agents and keep only needed ones
        old_building_count = len(self.building_agents)
        self.building_agents = {bid: agent for bid, agent in self.building_agents.items() if bid in buildings_needed}
        print(f"🧹 Cleared {old_building_count - len(self.building_agents)} old building agents, kept {len(self.building_agents)}")
        
        # Create building agents if they don't exist
        for building_id in buildings_needed:
            if building_id not in self.building_agents:
                building_config = self.campus_data.get('buildings', {}).get(building_id)
                if building_config:
                    building_agent = BuildingAgent(building_id, building_config)
                    self.building_agents[building_id] = building_agent
                    print(f"  ➕ Created building agent: {building_id}")
        
        # Register room agents to their buildings
        for room_id in room_ids:
            if room_id in self.room_agents:
                room_config = self.campus_data.get('rooms', {}).get(room_id, {})
                building_id = room_config.get('building_id')
                if building_id in self.building_agents:
                    self.building_agents[building_id].add_room_agent(room_id, self.room_agents[room_id])
        
        print(f"✓ Created agents for {len(room_ids)} rooms across {len(buildings_needed)} buildings")
    
    async def run_campus_analysis(self, current_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run complete campus analysis.
        
        Args:
            current_data: Real-time observations for all rooms
        
        Returns:
            Complete campus state with predictions and recommendations
        """
        print(f"\n🏛️  Running campus-wide analysis at {datetime.now().strftime('%H:%M:%S')}")
        
        # Get list of rooms to analyze
        room_ids = list(current_data.get('rooms', {}).keys())
        
        # Create agents only for the rooms we're analyzing
        self._ensure_agents_for_rooms(room_ids)
        
        # Set budget level on room agents if specified
        budget_level = current_data.get('parameters', {}).get('budget_level', 'medium')
        for room_agent in self.room_agents.values():
            room_agent.budget_level = budget_level
        
        # Step 1: Run all room agents in parallel
        print("📊 Analyzing individual rooms...")
        room_states = await self._run_room_agents(current_data)
        
        # Step 2: Aggregate at building level
        print("🏢 Aggregating building-level insights...")
        building_states = self._run_building_agents(room_states)
        
        # Step 3: Generate campus-wide insights
        print("🌍 Generating campus-wide recommendations...")
        campus_state = self._generate_campus_insights(building_states)
        
        print("✅ Analysis complete!\n")
        
        return campus_state
    
    async def _run_room_agents(self, current_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run all room agents concurrently."""
        tasks = []
        
        for room_id, room_agent in self.room_agents.items():
            # Get current observations for this room
            room_obs = current_data.get('rooms', {}).get(room_id, {})
            
            # Build initial state
            initial_state = self._build_room_initial_state(room_id, room_obs)
            
            # Schedule async execution
            tasks.append(self._run_single_room_agent(room_id, room_agent, initial_state))
        
        # Execute all in parallel
        results = await asyncio.gather(*tasks)
        
        # Convert to dict
        return {result['room_id']: result for result in results}
    
    async def _run_single_room_agent(self, room_id: str, agent: RoomAgent, initial_state: RoomState) -> Dict[str, Any]:
        """Run a single room agent."""
        try:
            result = await agent.run_async(initial_state)
            return result
        except Exception as e:
            print(f"⚠️  Error in room {room_id}: {e}")
            return initial_state  # Return initial state on error
    
    def _build_room_initial_state(self, room_id: str, observations: Dict[str, Any]) -> RoomState:
        """Build initial state for a room agent."""
        room_config = self.room_agents[room_id].room_config
        
        return RoomState(
            room_id=room_id,
            room_type=room_config.get('type', 'classroom'),
            building_id=room_config.get('building_id', 'unknown'),
            floor=room_config.get('floor', 1),
            capacity=room_config.get('capacity', 30),
            
            current_occupancy=observations.get('occupancy', 0),
            occupancy_level=observations.get('occupancy_level', 'low'),
            temperature_comfort=observations.get('temperature_comfort', 'comfortable'),
            equipment_running=observations.get('equipment_running', []),
            water_running=observations.get('water_running', False),
            
            occupancy_history=observations.get('occupancy_history', []),
            energy_history=observations.get('energy_history', []),
            water_history=observations.get('water_history', []),
            
            estimated_energy_kw=0.0,
            estimated_water_lph=0.0,
            estimated_co2_ppm=400,
            thermal_load='neutral',
            
            predicted_occupancy_1h=0,
            predicted_energy_1h=0.0,
            predicted_peak_time='',
            
            recommendations=[],
            anomalies=[],
            savings_potential=0.0,
            
            messages=[],
            last_updated=datetime.now().isoformat()
        )
    
    def _run_building_agents(self, room_states: Dict[str, Any]) -> Dict[str, Any]:
        """Run building-level analysis."""
        building_states = {}
        
        for building_id, building_agent in self.building_agents.items():
            # Get all room states for this building
            building_room_states = [
                state for room_id, state in room_states.items()
                if state.get('building_id') == building_id
            ]
            
            if building_room_states:
                building_state = building_agent.analyze_building(building_room_states)
                building_states[building_id] = building_state
        
        return building_states
    
    def _generate_campus_insights(self, building_states: Dict[str, Any]) -> Dict[str, Any]:
        """Generate campus-wide insights and recommendations."""
        # Aggregate campus metrics
        total_energy = sum(b['total_energy_kw'] for b in building_states.values())
        total_water = sum(b['total_water_lph'] for b in building_states.values())
        total_occupancy = sum(b['total_occupancy'] for b in building_states.values())
        total_capacity = sum(b['total_capacity'] for b in building_states.values())
        
        occupancy_rate = (total_occupancy / max(total_capacity, 1)) * 100
        
        # Aggregate savings potential
        total_kwh_savings = sum(
            b['savings_analysis']['estimated_kwh_saved'] 
            for b in building_states.values()
        )
        total_water_savings = sum(
            b['savings_analysis']['estimated_water_saved_lph'] 
            for b in building_states.values()
        )
        
        # Identify critical buildings
        critical_buildings = sorted(
            building_states.items(),
            key=lambda x: x[1]['total_energy_kw'],
            reverse=True
        )[:3]
        
        # Generate campus-level recommendations using LLM
        campus_recommendations = self._generate_campus_recommendations(
            building_states, total_energy, total_water, occupancy_rate
        )
        
        return {
            "campus_name": self.campus_config.get('name', 'Campus'),
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_buildings": len(building_states),
                "total_rooms": sum(b['total_rooms'] for b in building_states.values()),
                "total_energy_kw": round(total_energy, 2),
                "total_water_lph": round(total_water, 2),
                "total_occupancy": total_occupancy,
                "total_capacity": total_capacity,
                "occupancy_rate": round(occupancy_rate, 1)
            },
            "savings_potential": {
                "total_kwh_saved": round(total_kwh_savings, 2),
                "total_water_saved_lph": round(total_water_savings, 2),
                "estimated_cost_savings_hourly": round(total_kwh_savings * 0.12, 2),  # $0.12/kWh
                "co2_reduction_kg": round(total_kwh_savings * 0.5, 2)  # 0.5 kg CO2/kWh
            },
            "critical_buildings": [
                {
                    "building_id": b_id,
                    "building_name": b_state['building_name'],
                    "energy_kw": b_state['total_energy_kw'],
                    "occupancy_rate": b_state['occupancy_rate']
                }
                for b_id, b_state in critical_buildings
            ],
            "building_states": building_states,
            "campus_recommendations": campus_recommendations
        }
    
    def _generate_campus_recommendations(
        self, 
        building_states: Dict[str, Any],
        total_energy: float,
        total_water: float,
        occupancy_rate: float
    ) -> List[str]:
        """Generate campus-wide recommendations using LLM."""
        # Format building summaries
        building_summary = "\n".join([
            f"  - {b['building_name']}: {b['total_energy_kw']} kW, {b['occupancy_rate']}% occupied"
            for b in building_states.values()
        ])
        
        prompt = f"""
You are the Campus Sustainability Director analyzing the entire campus.

Campus Overview:
- Total Energy: {total_energy:.2f} kW
- Total Water: {total_water:.2f} L/h
- Campus Occupancy: {occupancy_rate:.1f}%
- Time: {datetime.now().strftime('%A %H:%M')}

Building Status:
{building_summary}

Generate 5-7 strategic campus-wide recommendations:
1. Cross-building optimizations
2. Policy changes needed
3. Infrastructure priorities
4. Behavioral change campaigns
5. Emergency responses
6. Long-term sustainability initiatives

Consider: Can we close entire buildings? Shift classes? Implement smart scheduling?

Format: "CAMPUS POLICY: [action] (impact: [metric])"
"""
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        recommendations = []
        for line in response.content.split('\n'):
            if 'CAMPUS POLICY:' in line or 'CAMPUS' in line.upper():
                recommendations.append(line.strip())
        
        return recommendations[:7]
    
    async def run_what_if_simulation(
        self, 
        scenario: Dict[str, Any], 
        current_data: Dict[str, Any],
        num_rooms: int = None,
        num_buildings: int = None,
        budget_level: str = 'medium'
    ) -> Dict[str, Any]:
        """
        Run a what-if simulation with budget constraints.
        
        Args:
            scenario: Scenario configuration
            current_data: Current campus data
            num_rooms: Maximum number of rooms to analyze (None = all)
            num_buildings: Maximum number of buildings to analyze (None = all)
            budget_level: 'low', 'medium', or 'high' - controls analysis depth
        
        Example scenarios:
        - Close building X after 8pm
        - Reduce HVAC in low-occupancy rooms
        - Shift classes to consolidate usage
        """
        print(f"\n🔮 Running what-if simulation: {scenario.get('name', 'Unnamed')}")
        print(f"   Budget constraints: {num_rooms or 'all'} rooms, {num_buildings or 'all'} buildings, {budget_level} budget")
        
        # Limit scope based on budget
        limited_data = self._apply_budget_constraints(
            current_data, 
            num_rooms=num_rooms,
            num_buildings=num_buildings,
            budget_level=budget_level
        )
        
        # Modify current data based on scenario
        modified_data = self._apply_scenario(limited_data, scenario)
        
        # Run analysis on modified data
        simulated_state = await self.run_campus_analysis(modified_data)
        
        # Compare with baseline
        baseline_state = await self.run_campus_analysis(limited_data)
        
        comparison = self._compare_states(baseline_state, simulated_state)
        
        return {
            "scenario": scenario,
            "baseline": baseline_state['summary'],
            "simulated": simulated_state['summary'],
            "comparison": comparison,
            "recommendation": "Implement" if comparison['energy_savings_pct'] > 10 else "Review",
            "execution_info": {
                "rooms_analyzed": len(limited_data.get('rooms', {})),
                "buildings_analyzed": len(set(r.get('building_id') for r in limited_data.get('rooms', {}).values())),
                "budget_level": budget_level
            }
        }
    
    def _apply_scenario(self, data: Dict[str, Any], scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Apply scenario modifications to data."""
        modified = data.copy()
        
        action_type = scenario.get('type')
        
        if action_type == 'close_building':
            building_id = scenario.get('building_id')
            # Set all rooms in building to zero occupancy
            for room_id, room_data in modified.get('rooms', {}).items():
                if room_data.get('building_id') == building_id:
                    room_data['occupancy'] = 0
                    room_data['equipment_running'] = []
        
        elif action_type == 'reduce_hvac':
            # Reduce energy in low-occupancy rooms
            for room_id, room_data in modified.get('rooms', {}).items():
                if room_data.get('occupancy_level') == 'low':
                    room_data['temperature_comfort'] = 'comfortable'
        
        return modified
    
    def _apply_budget_constraints(
        self,
        data: Dict[str, Any],
        num_rooms: int = None,
        num_buildings: int = None,
        budget_level: str = 'medium'
    ) -> Dict[str, Any]:
        """
        Limit the scope of analysis based on budget constraints.
        
        Args:
            data: Full campus data
            num_rooms: Maximum rooms to analyze
            num_buildings: Maximum buildings to analyze
            budget_level: Analysis depth ('low', 'medium', 'high')
        
        Returns:
            Limited dataset
        """
        limited = data.copy()
        
        # If no constraints, return full data
        if num_rooms is None and num_buildings is None:
            return limited
        
        rooms = limited.get('rooms', {})
        print(f"🔍 DEBUG Budget: Starting with {len(rooms)} total rooms")
        
        # First, limit buildings if specified
        if num_buildings is not None:
            available_buildings = list(set(r.get('building_id') for r in rooms.values()))
            print(f"🔍 DEBUG Budget: Available buildings: {available_buildings}")
            selected_buildings = available_buildings[:num_buildings]
            print(f"🔍 DEBUG Budget: Selected {len(selected_buildings)} buildings: {selected_buildings}")
            
            # Filter rooms to only selected buildings
            rooms = {
                room_id: room_data 
                for room_id, room_data in rooms.items()
                if room_data.get('building_id') in selected_buildings
            }
            print(f"🔍 DEBUG Budget: After building filter: {len(rooms)} rooms from {set(r.get('building_id') for r in rooms.values())}")
        
        # Then limit number of rooms if specified
        if num_rooms is not None and len(rooms) > num_rooms:
            # Select rooms with highest occupancy for more interesting results
            sorted_rooms = sorted(
                rooms.items(),
                key=lambda x: x[1].get('occupancy', 0),
                reverse=True
            )
            rooms = dict(sorted_rooms[:num_rooms])
            print(f"🔍 DEBUG Budget: After room limit: {len(rooms)} rooms from {set(r.get('building_id') for r in rooms.values())}")
        
        limited['rooms'] = rooms
        
        # Store budget level for potential use in agent reasoning
        if 'parameters' not in limited:
            limited['parameters'] = {}
        limited['parameters']['budget_level'] = budget_level
        
        final_buildings = set(r.get('building_id') for r in rooms.values())
        print(f"   Analyzing {len(rooms)} rooms across {len(final_buildings)} buildings")
        
        return limited
    
    def _compare_states(self, baseline: Dict[str, Any], simulated: Dict[str, Any]) -> Dict[str, Any]:
        """Compare baseline vs simulated states."""
        baseline_energy = baseline['summary']['total_energy_kw']
        simulated_energy = simulated['summary']['total_energy_kw']
        
        baseline_water = baseline['summary']['total_water_lph']
        simulated_water = simulated['summary']['total_water_lph']
        
        energy_savings = baseline_energy - simulated_energy
        water_savings = baseline_water - simulated_water
        
        return {
            "energy_savings_kw": round(energy_savings, 2),
            "energy_savings_pct": round((energy_savings / max(baseline_energy, 1)) * 100, 1),
            "water_savings_lph": round(water_savings, 2),
            "water_savings_pct": round((water_savings / max(baseline_water, 1)) * 100, 1),
            "cost_savings_hourly": round(energy_savings * 0.12, 2)
        }
