import axios from 'axios';
import { generateMockCampusAnalysis, generateMockSimulationTemplates } from './mockData';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // No default timeout - set per request
});

let backendAvailable = true;

// Check backend health
export const checkBackendHealth = async () => {
  try {
    await axios.get('http://localhost:8000/health', { timeout: 3000 });
    backendAvailable = true;
    return true;
  } catch (error) {
    backendAvailable = false;
    return false;
  }
};

// Auto-check backend on load
checkBackendHealth();

// Campus endpoints
export const campusAPI = {
  getInfo: async () => {
    try {
      return await api.get('/campus/info');
    } catch (error) {
      backendAvailable = false;
      throw error;
    }
  },
  getBuilding: (buildingId) => api.get(`/campus/buildings/${buildingId}`),
  getRoom: (roomId) => api.get(`/campus/rooms/${roomId}`),
};

// Analysis endpoints with fallback
export const analysisAPI = {
  getCurrent: async (params = {}) => {
    try {
      // Convert params object to query string
      const queryParams = new URLSearchParams();
      if (params.num_rooms) queryParams.append('num_rooms', params.num_rooms);
      if (params.num_buildings) queryParams.append('num_buildings', params.num_buildings);
      if (params.budget_level) queryParams.append('budget_level', params.budget_level);
      if (params.avg_occupancy !== undefined) queryParams.append('avg_occupancy', params.avg_occupancy);
      if (params.lights_on !== undefined) queryParams.append('lights_on', params.lights_on);
      if (params.ac_on !== undefined) queryParams.append('ac_on', params.ac_on);
      if (params.ac_temperature !== undefined) queryParams.append('ac_temperature', params.ac_temperature);
      if (params.fans_on !== undefined) queryParams.append('fans_on', params.fans_on);
      if (params.projectors_on_percent !== undefined) queryParams.append('projectors_on_percent', params.projectors_on_percent);
      if (params.computers_count !== undefined) queryParams.append('computers_count', params.computers_count);
      if (params.time_of_day) queryParams.append('time_of_day', params.time_of_day);
      if (params.outdoor_temperature !== undefined) queryParams.append('outdoor_temperature', params.outdoor_temperature);
      
      const url = `/analysis/current${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
      // No timeout when backend is available - let it take as long as needed
      console.log('🚀 Requesting analysis from backend (no timeout - waiting for completion)...');
      const response = await api.get(url, { timeout: 0 }); // 0 = no timeout
      console.log('✅ Backend response received!');
      backendAvailable = true;
      return response;
    } catch (error) {
      console.error('❌ Backend error:', error.message);
      if (error.code === 'ECONNABORTED') {
        console.warn('⏱️ Request timed out (this should not happen with timeout=0)');
      }
      if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
        console.warn('🔌 Backend not available, using frontend simulation');
        backendAvailable = false;
      } else {
        console.error('❌ Unexpected error:', error);
      }
      console.warn('📊 Falling back to frontend simulation');
      backendAvailable = false;
      // Return mock data with environmental parameters
      return {
        data: generateMockCampusAnalysis(params),
        status: 200,
        statusText: 'OK (Simulated)',
        headers: {},
        config: {}
      };
    }
  },
  getSummary: () => api.get('/analysis/summary'),
  getBuilding: (buildingId) => api.get(`/analysis/building/${buildingId}`),
  getRoom: (roomId) => api.get(`/analysis/room/${roomId}`),
  refresh: () => api.post('/analysis/refresh'),
};

// Simulation endpoints with fallback
export const simulationAPI = {
  run: async (scenario) => {
    try {
      // No timeout when backend is available - let it take as long as needed
      return await api.post('/simulation/run', scenario, { timeout: 0 }); // 0 = no timeout
    } catch (error) {
      console.warn('Backend unavailable, using mock simulation');
      // Return mock simulation result
      const baseline = generateMockCampusAnalysis();
      const simulated = generateMockCampusAnalysis();
      // Reduce energy in simulated by 15-25%
      const reduction = 0.15 + Math.random() * 0.1;
      simulated.campus_metrics.total_energy_kw *= (1 - reduction);
      
      return {
        data: {
          baseline: baseline.campus_metrics,
          simulated: simulated.campus_metrics,
          savings: {
            energy_kwh: (baseline.campus_metrics.total_energy_kw - simulated.campus_metrics.total_energy_kw).toFixed(2),
            water_liters: parseFloat((Math.random() * 50 + 20).toFixed(1)),
            cost_savings: ((baseline.campus_metrics.total_energy_kw - simulated.campus_metrics.total_energy_kw) * 0.12).toFixed(2)
          },
          recommendations: ["Implement scenario for optimal savings", "Monitor results for 1 week", "Adjust based on feedback"]
        }
      };
    }
  },
  getTemplates: async () => {
    try {
      return await api.get('/simulation/templates');
    } catch (error) {
      console.warn('Backend unavailable, using mock templates');
      return {
        data: generateMockSimulationTemplates()
      };
    }
  },
  compare: (scenarios) => api.post('/simulation/compare', scenarios),
};

// Health check
export const healthCheck = () => axios.get('http://localhost:8000/health');

export const isBackendAvailable = () => backendAvailable;

export default api;
