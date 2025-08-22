import React, { useState } from 'react';
import { RotateCcw, AlertTriangle, CheckCircle } from 'lucide-react';
import ApiService from '../services/api';

interface SettingsProps {
  userId: string;
}

const Settings: React.FC<SettingsProps> = ({ userId }) => {
  const [isResetting, setIsResetting] = useState(false);
  const [resetStatus, setResetStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);

  const handleResetData = async () => {
    try {
      setIsResetting(true);
      setResetStatus('idle');
      
      const response = await ApiService.resetUserData(userId);
      
      if (response.status === 'reset_complete') {
        setResetStatus('success');
        // Refresh the page after 2 seconds to show clean state
        setTimeout(() => {
          window.location.reload();
        }, 2000);
      }
    } catch (error) {
      console.error('Failed to reset user data:', error);
      setResetStatus('error');
    } finally {
      setIsResetting(false);
      setShowConfirmDialog(false);
    }
  };

  const confirmReset = () => {
    setShowConfirmDialog(true);
  };

  const cancelReset = () => {
    setShowConfirmDialog(false);
  };

  return (
    <div className="settings-container">
      <div className="settings-header">
        <h2>Settings</h2>
        <p>Manage your application preferences and data</p>
      </div>

      <div className="settings-sections">
        <div className="settings-section">
          <h3>Data Management</h3>
          
          <div className="settings-item">
            <div className="settings-item-info">
              <h4>Reset Application Data</h4>
              <p>
                This will clear all your questionnaire responses, personality insights, 
                and career analysis. You'll be able to start fresh with new questions.
              </p>
            </div>
            
            <button
              onClick={confirmReset}
              disabled={isResetting}
              className="reset-button"
            >
              <RotateCcw size={18} />
              {isResetting ? 'Resetting...' : 'Reset Data'}
            </button>
          </div>

          {resetStatus === 'success' && (
            <div className="status-message success">
              <CheckCircle size={20} />
              <span>Data reset successfully! Reloading application...</span>
            </div>
          )}

          {resetStatus === 'error' && (
            <div className="status-message error">
              <AlertTriangle size={20} />
              <span>Failed to reset data. Please try again.</span>
            </div>
          )}
        </div>
      </div>

      {/* Confirmation Dialog */}
      {showConfirmDialog && (
        <div className="modal-overlay">
          <div className="confirmation-dialog">
            <div className="dialog-header">
              <AlertTriangle size={24} className="warning-icon" />
              <h3>Confirm Data Reset</h3>
            </div>
            
            <div className="dialog-content">
              <p>
                Are you sure you want to reset all your application data? 
                This action cannot be undone.
              </p>
              <p>
                <strong>This will clear:</strong>
              </p>
              <ul>
                <li>All questionnaire responses</li>
                <li>Personality insights and analysis</li>
                <li>Career recommendations</li>
                <li>Progress history</li>
              </ul>
            </div>
            
            <div className="dialog-actions">
              <button onClick={cancelReset} className="cancel-button">
                Cancel
              </button>
              <button 
                onClick={handleResetData} 
                className="confirm-reset-button"
                disabled={isResetting}
              >
                {isResetting ? 'Resetting...' : 'Yes, Reset All Data'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Settings;