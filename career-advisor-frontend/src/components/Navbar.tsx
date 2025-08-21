import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { User, LogOut, Brain, BarChart, MessageSquare, Settings } from 'lucide-react';

interface NavbarProps {
  currentUser: string | null;
  onLogout: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ currentUser, onLogout }) => {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Brain size={28} />
        <h1>AI Career Advisor</h1>
      </div>

      {currentUser && (
        <div className="navbar-links">
          <Link 
            to="/dashboard" 
            className={`nav-link ${isActive('/dashboard') ? 'active' : ''}`}
          >
            <BarChart size={20} />
            Dashboard
          </Link>
          
          <Link 
            to="/analysis" 
            className={`nav-link ${isActive('/analysis') ? 'active' : ''}`}
          >
            <Brain size={20} />
            Career Analysis
          </Link>
          
          <Link 
            to="/chat" 
            className={`nav-link ${isActive('/chat') ? 'active' : ''}`}
          >
            <MessageSquare size={20} />
            AI Chat
          </Link>
          
          <Link 
            to="/analytics" 
            className={`nav-link ${isActive('/analytics') ? 'active' : ''}`}
          >
            <BarChart size={20} />
            Market Analytics
          </Link>
          
          <Link 
            to="/profile" 
            className={`nav-link ${isActive('/profile') ? 'active' : ''}`}
          >
            <Settings size={20} />
            Profile
          </Link>
        </div>
      )}

      <div className="navbar-user">
        {currentUser && (
          <div className="user-menu">
            <User size={20} />
            <span className="user-id">Demo Mode</span>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;