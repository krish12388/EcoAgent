import { useState, useEffect } from 'react';
import { analysisAPI, isBackendAvailable, checkBackendHealth } from '../services/api';
import { Activity, Zap, Droplets, Users, TrendingDown, AlertTriangle, Wifi, WifiOff, Clock, MessageCircle } from 'lucide-react';
import BuildingCard from './BuildingCard';
import RecommendationPanel from './RecommendationPanel';
import ChatPanel from './ChatPanel';
import './Dashboard.css';

function Dashboard() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [backendStatus, setBackendStatus] = useState('checking');
  const [chatOpen, setChatOpen] = useState(false);
  
  // Agent execution parameters
  const [numRooms, setNumRooms] = useState(10);
  const [numBuildings, setNumBuildings] = useState(2);
  const [budgetLevel, setBudgetLevel] = useState('low');
  const [useCustomSettings, setUseCustomSettings] = useState(true);
  const [showControls, setShowControls] = useState(true);
  
  // Environmental parameters
  const [avgOccupancy, setAvgOccupancy] = useState(15);
  const [lightsOn, setLightsOn] = useState(true);
  const [acOn, setAcOn] = useState(true);
  const [acTemp, setAcTemp] = useState(22);
  const [fansOn, setFansOn] = useState(false);
  const [projectorsOn, setProjectorsOn] = useState(30); // percentage
  const [computersOn, setComputersOn] = useState(5);
  const [timeOfDay, setTimeOfDay] = useState('afternoon');
  const [outdoorTemp, setOutdoorTemp] = useState(30);
  const [loadingStartTime, setLoadingStartTime] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0);

  useEffect(() => {
    checkBackend();
    // Only check backend status on mount, DO NOT run analysis automatically
    // Analysis only runs when user clicks "Run Analysis" button
  }, []);

  // Timer effect for loading screen
  useEffect(() => {
    if (loading && loadingStartTime) {
      const timer = setInterval(() => {
        setElapsedTime(Math.floor((Date.now() - loadingStartTime) / 1000));
      }, 1000);
      return () => clearInterval(timer);
    } else {
      setElapsedTime(0);
    }
  }, [loading, loadingStartTime]);

  const checkBackend = async () => {
    const available = await checkBackendHealth();
    setBackendStatus(available ? 'online' : 'offline');
  };

  const loadAnalysis = async () => {
    try {
      setLoadingStartTime(Date.now());
      setLoading(true);
      console.log('🔄 Starting analysis request...');
      
      // Pass parameters to backend
      const params = useCustomSettings ? {
        num_rooms: numRooms,
        num_buildings: numBuildings,
        budget_level: budgetLevel,
        // Environmental parameters
        avg_occupancy: avgOccupancy,
        lights_on: lightsOn,
        ac_on: acOn,
        ac_temperature: acTemp,
        fans_on: fansOn,
        projectors_on_percent: projectorsOn,
        computers_count: computersOn,
        time_of_day: timeOfDay,
        outdoor_temperature: outdoorTemp
      } : {};
      
      console.log('📤 Sending request to backend with params:', params);
      const startTime = Date.now();
      const response = await analysisAPI.getCurrent(params);
      const duration = ((Date.now() - startTime) / 1000).toFixed(1);
      console.log(`✅ Analysis completed in ${duration}s`);
      
      setAnalysis(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load campus analysis');
      console.error('❌ Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!analysis && !loading) {
    return (
      <div className="dashboard">
        <header className="dashboard-header">
          <div className="header-content">
            <h1>EcoAgent Dashboard</h1>
            <p className="subtitle">Configure and Run Multi-Agent Analysis</p>
          </div>
        </header>

        <div className="pre-analysis-container">
          <div className="control-panel-main">
            <h2>🎛️ Configure Agent Execution</h2>
            <p className="control-description">
              Set the scope of analysis before running. Lower values = faster execution and less API usage.
              Perfect for demonstrations!
            </p>
            
            <div className="controls-grid">
              <div className="control-item">
                <label htmlFor="numRooms">
                  Number of Rooms to Analyze
                  <span className="control-hint">(Recommended: 5-20 for demos)</span>
                </label>
                <input
                  id="numRooms"
                  type="range"
                  min="5"
                  max="50"
                  value={numRooms}
                  onChange={(e) => setNumRooms(parseInt(e.target.value))}
                  className="slider"
                />
                <span className="value-display">{numRooms} rooms</span>
              </div>

              <div className="control-item">
                <label htmlFor="numBuildings">
                  Number of Buildings
                  <span className="control-hint">(Recommended: 1-3 for demos)</span>
                </label>
                <input
                  id="numBuildings"
                  type="range"
                  min="1"
                  max="5"
                  value={numBuildings}
                  onChange={(e) => setNumBuildings(parseInt(e.target.value))}
                  className="slider"
                />
                <span className="value-display">{numBuildings} buildings</span>
              </div>

              <div className="control-item">
                <label htmlFor="budgetLevel">
                  API Key Budget
                  <span className="control-hint">(Controls analysis depth)</span>
                </label>
                <select
                  id="budgetLevel"
                  value={budgetLevel}
                  onChange={(e) => setBudgetLevel(e.target.value)}
                  className="budget-select"
                >
                  <option value="low">Low (Fast, minimal API usage)</option>
                  <option value="medium">Medium (Balanced)</option>
                  <option value="high">High (Deep analysis)</option>
                </select>
              </div>

              <div className="control-item checkbox-item">
                <label>
                  <input
                    type="checkbox"
                    checked={useCustomSettings}
                    onChange={(e) => setUseCustomSettings(e.target.checked)}
                  />
                  Use custom settings (uncheck for full campus analysis)
                </label>
              </div>
            </div>

            {/* Environmental & Equipment Parameters */}
            <div className="section-divider">
              <h3>🌡️ Room Conditions & Equipment</h3>
              <p className="section-hint">Configure typical room conditions for the simulation</p>
            </div>

            <div className="controls-grid">
              <div className="control-item">
                <label htmlFor="avgOccupancy">
                  Average Room Occupancy
                  <span className="control-hint">(Number of people per room)</span>
                </label>
                <input
                  id="avgOccupancy"
                  type="range"
                  min="0"
                  max="50"
                  value={avgOccupancy}
                  onChange={(e) => setAvgOccupancy(parseInt(e.target.value))}
                  className="slider"
                />
                <span className="value-display">{avgOccupancy} people</span>
              </div>

              <div className="control-item">
                <label htmlFor="acTemp">
                  AC Temperature Setting
                  <span className="control-hint">(°C)</span>
                </label>
                <input
                  id="acTemp"
                  type="range"
                  min="18"
                  max="28"
                  value={acTemp}
                  onChange={(e) => setAcTemp(parseInt(e.target.value))}
                  className="slider"
                />
                <span className="value-display">{acTemp}°C</span>
              </div>

              <div className="control-item">
                <label htmlFor="computersOn">
                  Computers Running
                  <span className="control-hint">(Per room average)</span>
                </label>
                <input
                  id="computersOn"
                  type="range"
                  min="0"
                  max="30"
                  value={computersOn}
                  onChange={(e) => setComputersOn(parseInt(e.target.value))}
                  className="slider"
                />
                <span className="value-display">{computersOn} computers</span>
              </div>

              <div className="control-item">
                <label htmlFor="projectorsOn">
                  Projectors Usage
                  <span className="control-hint">(% of rooms with projectors on)</span>
                </label>
                <input
                  id="projectorsOn"
                  type="range"
                  min="0"
                  max="100"
                  value={projectorsOn}
                  onChange={(e) => setProjectorsOn(parseInt(e.target.value))}
                  className="slider"
                />
                <span className="value-display">{projectorsOn}%</span>
              </div>

              <div className="control-item">
                <label htmlFor="outdoorTemp">
                  Outdoor Temperature
                  <span className="control-hint">(Affects HVAC load)</span>
                </label>
                <input
                  id="outdoorTemp"
                  type="range"
                  min="10"
                  max="45"
                  value={outdoorTemp}
                  onChange={(e) => setOutdoorTemp(parseInt(e.target.value))}
                  className="slider"
                />
                <span className="value-display">{outdoorTemp}°C</span>
              </div>

              <div className="control-item">
                <label htmlFor="timeOfDay">
                  Time of Day
                  <span className="control-hint">(Affects usage patterns)</span>
                </label>
                <select
                  id="timeOfDay"
                  value={timeOfDay}
                  onChange={(e) => setTimeOfDay(e.target.value)}
                  className="budget-select"
                >
                  <option value="early_morning">Early Morning (6-9 AM)</option>
                  <option value="morning">Morning (9-12 PM)</option>
                  <option value="afternoon">Afternoon (12-5 PM)</option>
                  <option value="evening">Evening (5-9 PM)</option>
                  <option value="night">Night (9 PM-6 AM)</option>
                </select>
              </div>
            </div>

            {/* Equipment Toggle Switches */}
            <div className="equipment-toggles">
              <div className="toggle-item">
                <label>
                  <input
                    type="checkbox"
                    checked={lightsOn}
                    onChange={(e) => setLightsOn(e.target.checked)}
                  />
                  💡 Lights On
                </label>
              </div>
              <div className="toggle-item">
                <label>
                  <input
                    type="checkbox"
                    checked={acOn}
                    onChange={(e) => setAcOn(e.target.checked)}
                  />
                  ❄️ AC Running
                </label>
              </div>
              <div className="toggle-item">
                <label>
                  <input
                    type="checkbox"
                    checked={fansOn}
                    onChange={(e) => setFansOn(e.target.checked)}
                  />
                  🌀 Fans On
                </label>
              </div>
            </div>

            <div className="execution-info">
              <p><strong>Current Configuration:</strong></p>
              <ul>
                <li>Will analyze {useCustomSettings ? numRooms : 'all'} rooms across {useCustomSettings ? numBuildings : 'all'} buildings</li>
                <li>Budget level: {budgetLevel.toUpperCase()}</li>
                <li>Avg {avgOccupancy} people/room, AC at {acTemp}°C, {computersOn} computers/room</li>
                <li>Time: {timeOfDay.replace('_', ' ')}, Outdoor: {outdoorTemp}°C</li>
                <li>Equipment: {lightsOn ? '💡' : '🌑'} {acOn ? '❄️' : '🔥'} {fansOn ? '🌀' : '⛔'}</li>
                <li>Estimated API calls: ~{useCustomSettings ? Math.ceil(numRooms * 0.3 + numBuildings * 0.5) : '50+'}</li>
              </ul>
            </div>

            <button className="run-now-btn" onClick={loadAnalysis} disabled={loading}>
              <Activity size={20} />
              ▶️ Run Campus Analysis
            </button>
          </div>
        </div>
      </div>
    );
  }
  
  if (loading) {
    return (
      <div className="loading-container">
        <Activity className="loading-icon spinning" size={64} />
        <h2>AI Agents Processing...</h2>
        <div className="loading-progress">
          <p className="progress-step">🤖 Room Agents → 🏢 Building Agents → 🌍 Campus Agent</p>
          <div className="timer-display">
            <Clock size={20} />
            <span>{elapsedTime}s elapsed</span>
          </div>
          <p className="progress-note">
            {elapsedTime < 10 && '⏳ Loading Ollama model into memory...'}
            {elapsedTime >= 10 && elapsedTime < 30 && '🧠 Analyzing rooms with AI...'}
            {elapsedTime >= 30 && elapsedTime < 60 && '🏗️ Processing building data...'}
            {elapsedTime >= 60 && elapsedTime < 120 && '🌍 Generating campus insights...'}
            {elapsedTime >= 120 && '⏰ Large-scale analysis in progress...'}
          </p>
          <p className="progress-hint">No timeout • Waiting for backend completion • Using local mistral-small:24b</p>
        </div>
      </div>
    );
  }

  const summary = analysis?.campus_metrics || analysis?.summary || {};
  const savings = analysis?.savings_potential || {};
  const buildings = analysis?.building_states || {};
  const isSimulation = analysis?.analysis_type === 'FRONTEND_SIMULATION';

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <h1>{analysis?.campus_name || 'EcoAgent Dashboard'}</h1>
            {backendStatus === 'online' ? (
              <span className="status-badge status-online">
                <Wifi size={14} /> Live
              </span>
            ) : (
              <span className="status-badge status-offline">
                <WifiOff size={14} /> Demo
              </span>
            )}
          </div>
          <p className="subtitle">AI-Powered Campus Sustainability System</p>
        </div>
        <button className="refresh-btn" onClick={loadAnalysis} disabled={loading}>
          <Activity className={loading ? 'spinning' : ''} size={20} />
          {loading ? 'Analyzing...' : (analysis ? 'Run Again' : '▶️ Run Analysis')}
        </button>
      </header>

      {/* Info Banner */}
      <div className="info-banner">
        <div className="info-icon">ℹ️</div>
        <div className="info-content">
          <strong>Manual Agent Execution</strong>
          <p>Agents run only when you click "Run Analysis". Configure settings above before running to control API usage.</p>
        </div>
      </div>

      {/* Show execution info if available */}
      {analysis?.execution_info && (
        <div className="execution-summary-dashboard">
          <h3>🤖 Last Analysis Execution</h3>
          <div className="execution-stats-dashboard">
            <span>✓ Analyzed {analysis.execution_info.rooms_analyzed} rooms</span>
            <span>✓ Across {analysis.execution_info.buildings_analyzed} buildings</span>
            <span>✓ Budget level: {analysis.execution_info.budget_level.toUpperCase()}</span>
          </div>
        </div>
      )}

      {/* Key Metrics */}
      <div className="metrics-grid">
        <MetricCard
          icon={<Zap />}
          title="Total Energy"
          value={`${summary.total_energy_kw?.toFixed(1) || 0} kW`}
          subtitle={`${Object.keys(buildings).length} buildings active`}
          color="energy"
        />
        <MetricCard
          icon={<Droplets />}
          title="Water Usage"
          value={`${summary.total_water_lph?.toFixed(1) || 0} L/h`}
          subtitle={`${summary.total_rooms || 0} rooms monitored`}
          color="water"
        />
        <MetricCard
          icon={<Users />}
          title="Occupancy"
          value={`${summary.occupancy_rate?.toFixed(1) || 0}%`}
          subtitle={`${summary.total_occupancy || 0} / ${summary.total_capacity || 0} people`}
          color="occupancy"
        />
        <MetricCard
          icon={<TrendingDown />}
          title="Savings Potential"
          value={`${savings.total_kwh_saved?.toFixed(1) || summary.potential_savings_percent?.toFixed(1) || 0}${savings.total_kwh_saved ? ' kWh' : '%'}`}
          subtitle={`$${savings.estimated_cost_savings_hourly?.toFixed(2) || (summary.estimated_cost_per_hour * 0.25)?.toFixed(2) || 0}/hour`}
          color="savings"
        />
      </div>

      {/* Campus Recommendations */}
      <RecommendationPanel recommendations={analysis?.campus_recommendations || []} />

      {/* Building Status */}
      <section className="buildings-section">
        <h2>Building Status</h2>
        <div className="buildings-grid">
          {Object.entries(buildings).map(([buildingId, buildingData]) => (
            <BuildingCard key={buildingId} building={buildingData} />
          ))}
        </div>
      </section>

      {/* Critical Buildings Alert */}
      {analysis?.critical_buildings?.length > 0 && (
        <section className="critical-section">
          <h2>⚠️ High Energy Consumption</h2>
          <div className="critical-list">
            {analysis.critical_buildings.map((building, idx) => (
              <div key={building.building_id || idx} className="critical-item">
                <div className="critical-info">
                  <h3>{building.building_name || building.building_id}</h3>
                  <span className="critical-reason">{building.reason}</span>
                </div>
                <div className="critical-metrics">
                  <span className="energy-badge">{building.energy_kw?.toFixed(1) || 0} kW</span>
                  <span className="occupancy-badge">{building.occupancy_rate?.toFixed(1) || 0}% occupied</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Chat Button */}
      {analysis && !chatOpen && (
        <button onClick={() => setChatOpen(true)} className="chat-fab">
          <MessageCircle size={24} />
        </button>
      )}

      {/* Chat Panel */}
      {analysis && (
        <ChatPanel
          analysisData={analysis}
          isOpen={chatOpen}
          onClose={() => setChatOpen(false)}
        />
      )}
    </div>
  );
}

function MetricCard({ icon, title, value, subtitle, color }) {
  return (
    <div className="metric-card">
      <div className="metric-header">
        <div className="metric-info">
          <h3>{title}</h3>
          <div className="metric-value">{value}</div>
          <span className="metric-subtitle">{subtitle}</span>
        </div>
        <div className={`metric-icon ${color}`}>{icon}</div>
      </div>
    </div>
  );
}

export default Dashboard;
