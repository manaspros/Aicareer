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
import Login from './components/Login';

// Services
import ApiService from './services/api';

function App() {
  const [currentUser, setCurrentUser] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in from localStorage
    const savedUserId = localStorage.getItem('currentUserId');
    if (savedUserId) {
      setCurrentUser(savedUserId);
    }
    setIsLoading(false);
  }, []);

  const handleUserLogin = (userId: string) => {
    setCurrentUser(userId);
    localStorage.setItem('currentUserId', userId);
  };

  const handleUserLogout = () => {
    setCurrentUser(null);
    localStorage.removeItem('currentUserId');
  };

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  // Show login screen if no user is authenticated
  if (!currentUser) {
    return <Login onLogin={handleUserLogin} />;
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
