import React, { useState, useEffect } from 'react';
import { User, Save, Loader, Edit } from 'lucide-react';
import ApiService from '../services/api';
import type { UserProfile as UserProfileType } from '../services/api';

interface UserProfileProps {
  userId: string;
}

const UserProfile: React.FC<UserProfileProps> = ({ userId }) => {
  const [profile, setProfile] = useState<UserProfileType | null>(null);
  const [editedProfile, setEditedProfile] = useState<UserProfileType | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const profileData = await ApiService.getUserProfile(userId);
        setProfile(profileData);
        setEditedProfile(profileData);
      } catch (error: any) {
        setError('Failed to load profile');
        console.error('Profile error:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchProfile();
  }, [userId]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    if (editedProfile) {
      setEditedProfile({
        ...editedProfile,
        [name]: name === 'age' ? (value ? parseInt(value) : undefined) : value
      });
    }
  };

  const handleSave = async () => {
    if (!editedProfile) return;

    setIsSaving(true);
    setError(null);
    setSuccess(null);

    try {
      await ApiService.updateUserProfile(userId, editedProfile);
      setProfile(editedProfile);
      setIsEditing(false);
      setSuccess('Profile updated successfully!');
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to update profile');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setEditedProfile(profile);
    setIsEditing(false);
    setError(null);
  };

  if (isLoading) {
    return (
      <div className="profile-loading">
        <div className="loading-spinner"></div>
        <p>Loading profile...</p>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="profile-error">
        <p>Error: {error || 'Profile not found'}</p>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <div className="profile-header">
        <User size={48} className="profile-icon" />
        <div>
          <h1>User Profile</h1>
          <p>Manage your personal information and preferences</p>
        </div>
        {!isEditing && (
          <button
            onClick={() => setIsEditing(true)}
            className="edit-btn"
          >
            <Edit size={20} />
            Edit Profile
          </button>
        )}
      </div>

      <div className="profile-card">
        <div className="profile-form">
          <div className="form-section">
            <h2>Basic Information</h2>
            
            <div className="form-group">
              <label htmlFor="name">Full Name</label>
              <input
                type="text"
                id="name"
                name="name"
                value={editedProfile?.name || ''}
                onChange={handleInputChange}
                disabled={!isEditing}
                placeholder="Enter your full name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                type="email"
                id="email"
                name="email"
                value={editedProfile?.email || ''}
                onChange={handleInputChange}
                disabled={!isEditing}
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
                  value={editedProfile?.age || ''}
                  onChange={handleInputChange}
                  disabled={!isEditing}
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
                  value={editedProfile?.location || ''}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  placeholder="City, Country"
                />
              </div>
            </div>
          </div>

          <div className="form-section">
            <h2>Career Information</h2>
            
            <div className="form-group">
              <label htmlFor="education_level">Education Level</label>
              <select
                id="education_level"
                name="education_level"
                value={editedProfile?.education_level || ''}
                onChange={handleInputChange}
                disabled={!isEditing}
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
                value={editedProfile?.career_stage || ''}
                onChange={handleInputChange}
                disabled={!isEditing}
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
          </div>

          {(error || success) && (
            <div className={`message ${error ? 'error' : 'success'}`}>
              {error || success}
            </div>
          )}

          {isEditing && (
            <div className="profile-actions">
              <button
                onClick={handleSave}
                disabled={isSaving}
                className="save-btn"
              >
                {isSaving ? (
                  <>
                    <Loader size={20} className="spinning" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save size={20} />
                    Save Changes
                  </>
                )}
              </button>
              
              <button
                onClick={handleCancel}
                disabled={isSaving}
                className="cancel-btn"
              >
                Cancel
              </button>
            </div>
          )}
        </div>

        <div className="profile-stats">
          <h2>Account Information</h2>
          <div className="stat-item">
            <span className="stat-label">User ID:</span>
            <span className="stat-value">{userId}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Profile Status:</span>
            <span className="stat-value status-active">Active</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;