import React, { useState } from 'react';
import ApiService from '../services/api';

interface LoginProps {
  onLogin: (userId: string) => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    age: '',
    location: '',
    educationLevel: '',
    careerStage: ''
  });

  const educationLevels = [
    { value: 'high_school', label: 'High School' },
    { value: 'associates', label: 'Associates Degree' },
    { value: 'bachelors', label: 'Bachelor\'s Degree' },
    { value: 'masters', label: 'Master\'s Degree' },
    { value: 'phd', label: 'PhD' },
    { value: 'professional', label: 'Professional Degree' }
  ];

  const careerStages = [
    { value: 'student', label: 'Student' },
    { value: 'entry_level', label: 'Entry Level' },
    { value: 'mid_career', label: 'Mid-Career' },
    { value: 'senior_level', label: 'Senior Level' },
    { value: 'executive', label: 'Executive' }
  ];

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      if (isLogin) {
        // For login, we'll just create a simple user ID based on email
        const userId = formData.email.split('@')[0] || 'user';
        onLogin(userId);
      } else {
        // Registration
        const userData = {
          name: formData.name,
          email: formData.email,
          age: parseInt(formData.age) || undefined,
          location: formData.location || undefined,
          education_level: formData.educationLevel || undefined,
          career_stage: formData.careerStage || undefined
        };

        console.log('Sending registration data:', userData);
        const response = await ApiService.registerUser(userData);
        console.log('Registration response:', response);
        onLogin(response.user_id);
      }
    } catch (err: any) {
      console.error('Registration error:', err);
      let errorMessage = 'An error occurred. Please try again.';
      
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>🎓 AI Career Advisor</h1>
          <p>Plan your future with intelligent career guidance</p>
        </div>

        <div className="auth-tabs">
          <button 
            className={`tab ${isLogin ? 'active' : ''}`}
            onClick={() => setIsLogin(true)}
          >
            Sign In
          </button>
          <button 
            className={`tab ${!isLogin ? 'active' : ''}`}
            onClick={() => setIsLogin(false)}
          >
            Get Started
          </button>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {!isLogin && (
            <>
              <div className="form-group">
                <label htmlFor="name">Full Name *</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required={!isLogin}
                  placeholder="Enter your full name"
                />
              </div>

              <div className="form-group">
                <label htmlFor="age">Age</label>
                <input
                  type="number"
                  id="age"
                  name="age"
                  value={formData.age}
                  onChange={handleInputChange}
                  placeholder="Your age"
                  min="13"
                  max="100"
                />
              </div>

              <div className="form-group">
                <label htmlFor="location">Location</label>
                <input
                  type="text"
                  id="location"
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  placeholder="City, Country"
                />
              </div>

              <div className="form-group">
                <label htmlFor="educationLevel">Education Level</label>
                <select
                  id="educationLevel"
                  name="educationLevel"
                  value={formData.educationLevel}
                  onChange={handleInputChange}
                >
                  <option value="">Select education level</option>
                  {educationLevels.map(level => (
                    <option key={level.value} value={level.value}>
                      {level.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="careerStage">Career Stage</label>
                <select
                  id="careerStage"
                  name="careerStage"
                  value={formData.careerStage}
                  onChange={handleInputChange}
                >
                  <option value="">Select career stage</option>
                  {careerStages.map(stage => (
                    <option key={stage.value} value={stage.value}>
                      {stage.label}
                    </option>
                  ))}
                </select>
              </div>
            </>
          )}

          <div className="form-group">
            <label htmlFor="email">Email *</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
              placeholder="Enter your email"
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button 
            type="submit" 
            className="auth-button"
            disabled={isLoading}
          >
            {isLoading ? 'Please wait...' : (isLogin ? 'Sign In' : 'Create Account')}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            {isLogin ? "New to Career Advisor? " : "Already have an account? "}
            <button 
              type="button"
              className="link-button"
              onClick={() => setIsLogin(!isLogin)}
            >
              {isLogin ? "Get started" : "Sign in"}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;