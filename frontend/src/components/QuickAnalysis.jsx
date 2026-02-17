import { useState } from 'react';
import { Zap, TrendingDown, Users, Building2, Droplets, DollarSign, RefreshCw, Sparkles, MessageCircle } from 'lucide-react';
import ChatPanel from './ChatPanel';
import './QuickAnalysis.css';

function QuickAnalysis() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);

  const loadQuickAnalysis = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/mock/analysis/current');
      const data = await response.json();
      setAnalysis(data);
    } catch (error) {
      console.error('Failed to load quick analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  if (!analysis) {
    return (
      <div className="quick-analysis">
        <div className="quick-header">
          <div className="header-title">
            <Sparkles size={32} className="sparkle-icon" />
            <div>
              <h1>Quick Analysis</h1>
              <p>Instant campus insights - no waiting!</p>
            </div>
          </div>
          <div className="quick-badge">
            <Zap size={16} />
            <span>Lightning Fast</span>
          </div>
        </div>

        <div className="welcome-card">
          <div className="welcome-content">
            <h2>Get Instant Campus Insights</h2>
            <p>This page provides rapid analysis of your campus energy and sustainability metrics.</p>
            <ul className="feature-list">
              <li><Zap size={18} /> Responds in less than a second</li>
              <li><Building2 size={18} /> Analyzes all buildings instantly</li>
              <li><TrendingDown size={18} /> Identifies savings opportunities</li>
              <li><Users size={18} /> Real-time occupancy metrics</li>
            </ul>
            <button onClick={loadQuickAnalysis} className="start-button">
              <Sparkles size={20} />
              Get Instant Analysis
            </button>
          </div>
        </div>
      </div>
    );
  }

  const metrics = analysis.campus_metrics;

  return (
    <div className="quick-analysis">
      <div className="quick-header">
        <div className="header-title">
          <Sparkles size={32} className="sparkle-icon" />
          <div>
            <h1>Quick Analysis</h1>
            <p>Last updated: {formatTime(analysis.timestamp)}</p>
          </div>
        </div>
        <button onClick={loadQuickAnalysis} disabled={loading} className="refresh-button">
          <RefreshCw size={18} className={loading ? 'spinning' : ''} />
          Refresh
        </button>
      </div>

      {/* Key Metrics Grid */}
      <div className="metrics-grid">
        <div className="metric-card energy">
          <div className="metric-icon">
            <Zap size={28} />
          </div>
          <div className="metric-content">
            <h3>Total Energy</h3>
            <div className="metric-value">{metrics.total_energy_kw} <span>kW</span></div>
            <p className="metric-cost">${metrics.estimated_cost_per_hour}/hour</p>
          </div>
        </div>

        <div className="metric-card savings">
          <div className="metric-icon">
            <TrendingDown size={28} />
          </div>
          <div className="metric-content">
            <h3>Savings Potential</h3>
            <div className="metric-value">{metrics.potential_savings_percent}<span>%</span></div>
            <p className="metric-detail">Across all buildings</p>
          </div>
        </div>

        <div className="metric-card occupancy">
          <div className="metric-icon">
            <Users size={28} />
          </div>
          <div className="metric-content">
            <h3>Campus Occupancy</h3>
            <div className="metric-value">{metrics.total_occupancy} <span>people</span></div>
            <p className="metric-detail">{metrics.avg_occupancy_rate}% average rate</p>
          </div>
        </div>

        <div className="metric-card water">
          <div className="metric-icon">
            <Droplets size={28} />
          </div>
          <div className="metric-content">
            <h3>Water Usage</h3>
            <div className="metric-value">{metrics.total_water_lph} <span>L/hr</span></div>
            <p className="metric-detail">{metrics.total_buildings} buildings monitored</p>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="recommendations-section">
        <h2>🎯 Top Recommendations</h2>
        <div className="recommendation-list">
          {analysis.campus_recommendations.map((rec, idx) => (
            <div key={idx} className="recommendation-item">
              <div className="rec-number">{idx + 1}</div>
              <p>{rec}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Buildings Overview */}
      <div className="buildings-section">
        <h2>🏢 Buildings Overview</h2>
        <div className="buildings-grid">
          {Object.entries(analysis.building_states).map(([buildingId, building]) => (
            <div key={buildingId} className="building-card-quick">
              <div className="building-header-quick">
                <Building2 size={24} />
                <h3>{buildingId}</h3>
              </div>
              <div className="building-stats">
                <div className="stat">
                  <span className="stat-label">Energy</span>
                  <span className="stat-value">{building.total_energy_kw} kW</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Occupancy</span>
                  <span className="stat-value">{building.occupancy_rate}%</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Rooms</span>
                  <span className="stat-value">{building.total_rooms}</span>
                </div>
                <div className="stat highlight">
                  <span className="stat-label">Savings</span>
                  <span className="stat-value">{building.savings_potential}%</span>
                </div>
              </div>
              <div className="building-recommendations">
                <strong>Top Actions:</strong>
                {building.recommendations.slice(0, 2).map((rec, idx) => (
                  <p key={idx} className="building-rec">• {rec}</p>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Critical Buildings Alert */}
      {analysis.critical_buildings.length > 0 && (
        <div className="critical-section">
          <h2>⚠️ High Priority Buildings</h2>
          <div className="critical-list">
            {analysis.critical_buildings.map((building, idx) => (
              <div key={idx} className="critical-item">
                <Building2 size={20} />
                <span className="critical-name">{building.building_id}</span>
                <span className="critical-reason">{building.reason}</span>
                <span className="critical-energy">{building.energy_kw} kW</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="analysis-info">
        <p>✨ Analysis type: {analysis.analysis_type}</p>
        <p className="note">{analysis.note}</p>
      </div>

      {/* Chat Button */}
      {!chatOpen && (
        <button onClick={() => setChatOpen(true)} className="chat-fab">
          <MessageCircle size={24} />
        </button>
      )}

      {/* Chat Panel */}
      <ChatPanel
        analysisData={analysis}
        isOpen={chatOpen}
        onClose={() => setChatOpen(false)}
      />
    </div>
  );
}

export default QuickAnalysis;
