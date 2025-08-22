import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// Components
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import UserProfile from './components/UserProfile';
import CareerAnalysis from './components/CareerAnalysis';
import AIChat from './components/AIChat';
import Analytics from './components/Analytics';
import Settings from './components/Settings';

// Services
import ApiService from './services/api';

function App() {
  const [currentUser, setCurrentUser] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Auto-generate or get existing user ID
    let savedUserId = localStorage.getItem('currentUserId');
    if (!savedUserId) {
      // Generate a unique user ID
      savedUserId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('currentUserId', savedUserId);
    }
    setCurrentUser(savedUserId);
    setIsLoading(false);
  }, []);

  const handleUserLogout = () => {
    setCurrentUser(null);
    localStorage.removeItem('currentUserId');
    // Generate new user ID on logout
    const newUserId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('currentUserId', newUserId);
    setCurrentUser(newUserId);
  };

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  // Show main app if user is authenticated
  return (
    <Router>
      <div className="App">
        <Navbar currentUser={currentUser} onLogout={handleUserLogout} />
        
        <main className="main-content">
          <Routes>            
            <Route 
              path="/dashboard" 
              element={<Dashboard userId={currentUser} />} 
            />
            
            <Route 
              path="/profile" 
              element={<UserProfile userId={currentUser} />} 
            />
            
            <Route 
              path="/analysis" 
              element={<CareerAnalysis userId={currentUser} />} 
            />
            
            <Route 
              path="/chat" 
              element={<AIChat userId={currentUser} />} 
            />
            
            <Route 
              path="/analytics" 
              element={<Analytics />} 
            />

            <Route 
              path="/settings" 
              element={<Settings userId={currentUser} />} 
            />
            
            <Route 
              path="/" 
              element={<Navigate to="/dashboard" />} 
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
