import React, { useState } from 'react';
import { UserPlus, Loader } from 'lucide-react';
import ApiService from '../services/api';
import type { UserProfile } from '../services/api';

interface RegistrationProps {
  onUserRegistered: (userId: string) => void;
}

const Registration: React.FC<RegistrationProps> = ({ onUserRegistered }) => {
  const [formData, setFormData] = useState<UserProfile>({
    name: '',
    email: '',
    age: undefined,
    location: '',
    education_level: '',
    career_stage: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'age' ? (value ? parseInt(value) : undefined) : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.email) {
      setError('Name and email are required');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await ApiService.registerUser(formData);
      onUserRegistered(result.user_id);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="registration-container">
      <div className="registration-card">
        <div className="registration-header">
          <UserPlus size={48} className="registration-icon" />
          <h1>Welcome to AI Career Advisor</h1>
          <p>Create your profile to get personalized career guidance</p>
        </div>

        <form onSubmit={handleSubmit} className="registration-form">
          <div className="form-group">
            <label htmlFor="name">Full Name *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              required
              placeholder="Enter your full name"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email Address *</label>
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

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="age">Age</label>
              <input
                type="number"
                id="age"
                name="age"
                value={formData.age || ''}
                onChange={handleInputChange}
                min="16"
                max="100"
                placeholder="Age"
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
          </div>

          <div className="form-group">
            <label htmlFor="education_level">Education Level</label>
            <select
              id="education_level"
              name="education_level"
              value={formData.education_level}
              onChange={handleInputChange}
            >
              <option value="">Select education level</option>
              <option value="high_school">High School</option>
              <option value="associate">Associate Degree</option>
              <option value="bachelor">Bachelor's Degree</option>
              <option value="master">Master's Degree</option>
              <option value="doctorate">Doctorate</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="career_stage">Career Stage</label>
            <select
              id="career_stage"
              name="career_stage"
              value={formData.career_stage}
              onChange={handleInputChange}
            >
              <option value="">Select career stage</option>
              <option value="student">Student</option>
              <option value="entry_level">Entry Level</option>
              <option value="mid_level">Mid Level</option>
              <option value="senior_level">Senior Level</option>
              <option value="executive">Executive</option>
              <option value="career_change">Career Change</option>
              <option value="returning">Returning to Work</option>
            </select>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <button 
            type="submit" 
            className="register-btn"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <Loader size={20} className="spinning" />
                Creating Profile...
              </>
            ) : (
              <>
                <UserPlus size={20} />
                Create Profile
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Registration;