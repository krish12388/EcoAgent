import { Link } from 'react-router-dom';
import { ArrowRight, Zap, BarChart3, Brain, Moon, Sun } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import '../styles/Landing_theme.css';

export default function Landing() {
  const { isDark, toggleTheme } = useTheme();

  return (
    <div className="landing">
      {/* Navigation */}
      <nav className="landing-nav">
        <div className="nav-brand">
          <span className="brand-icon">🌍</span>
          <span className="brand-text">EcoAgent</span>
        </div>
        <div className="nav-right">
          <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle theme">
            {isDark ? <Sun size={20} /> : <Moon size={20} />}
          </button>
          <Link to="/dashboard" className="nav-dashboard">
            DASHBOARD
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="landing-container">
        <div className="hero-left">
          <div className="hero-content">
            <h1 className="hero-title">
              Intelligent
              <br />
              Sustainability
              <br />
              <span className="accent-text">Management</span>
            </h1>

            <p className="hero-subtitle">
              Real-time analytics and AI-driven insights for enterprise-level energy optimization and environmental impact reduction.
            </p>

            <div className="features">
              <div className="feature-item">
                <Zap size={20} className="feature-icon" />
                <span>Real-time Energy Analytics</span>
              </div>
              <div className="feature-item">
                <BarChart3 size={20} className="feature-icon" />
                <span>Predictive Optimization</span>
              </div>
              <div className="feature-item">
                <Brain size={20} className="feature-icon" />
                <span>AI-Powered Recommendations</span>
              </div>
            </div>

            <Link to="/dashboard" className="hero-cta">
              <span>Launch Dashboard</span>
              <ArrowRight size={20} />
            </Link>
          </div>
        </div>

        <div className="hero-right">
          <div className="bg-image" />
          <div className="glow-overlay glow-top"></div>
          <div className="glow-overlay glow-bottom"></div>
        </div>
      </div>

      {/* Footer */}
      <footer className="landing-footer">
        <p>Powered by AI Agents • Enterprise-grade Sustainability Platform</p>
      </footer>
    </div>
  );
}
