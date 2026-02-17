import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { LayoutDashboard, Activity, Droplets, Zap } from 'lucide-react';
import Dashboard from './components/Dashboard';
import Simulation from './components/Simulation';
import QuickAnalysis from './components/QuickAnalysis';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="sidebar">
          <div className="sidebar-header">
            <h2>🌍 EcoAgent</h2>
            <p>Sustainability OS</p>
          </div>
          <ul className="nav-links">
            <li>
              <Link to="/quick" className="nav-link">
                <Zap size={20} />
                <span>Quick Analysis</span>
              </Link>
            </li>
            <li>
              <Link to="/" className="nav-link">
                <LayoutDashboard size={20} />
                <span>Dashboard</span>
              </Link>
            </li>
            <li>
              <Link to="/simulation" className="nav-link">
                <Activity size={20} />
                <span>What-If Scenarios</span>
              </Link>
            </li>
          </ul>
          <div className="sidebar-footer">
            <Droplets size={16} />
            <span>Powered by AI Agents</span>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/quick" element={<QuickAnalysis />} />
            <Route path="/" element={<Dashboard />} />
            <Route path="/simulation" element={<Simulation />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
