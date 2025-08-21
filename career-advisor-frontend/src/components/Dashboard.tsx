import React, { useState, useEffect } from 'react';
import { Brain, MessageSquare, TrendingUp, User, Target, Award, CheckCircle, AlertCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import ApiService from '../services/api';
import OnboardingQuestionnaire from './OnboardingQuestionnaire';

interface DashboardProps {
  userId: string;
}

interface DashboardData {
  userProfile: any;
  recentConversations: any[];
  systemMetrics: any;
  recommendations: any;
  questionnaireStatus: any;
}

const Dashboard: React.FC<DashboardProps> = ({ userId }) => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showQuestionnaire, setShowQuestionnaire] = useState(false);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [userProfile, conversations, metrics, recommendations, questionnaireStatus] = await Promise.allSettled([
          ApiService.getUserProfile(userId),
          ApiService.getConversationHistory(userId, 5),
          ApiService.getSystemMetrics(),
          ApiService.getCareerRecommendations(userId),
          ApiService.getQuestionnaireStatus(userId)
        ]);

        setData({
          userProfile: userProfile.status === 'fulfilled' ? userProfile.value : null,
          recentConversations: conversations.status === 'fulfilled' ? conversations.value.conversations : [],
          systemMetrics: metrics.status === 'fulfilled' ? metrics.value : null,
          recommendations: recommendations.status === 'fulfilled' ? recommendations.value : null,
          questionnaireStatus: questionnaireStatus.status === 'fulfilled' ? questionnaireStatus.value : null
        });
      } catch (error: any) {
        setError('Failed to load dashboard data');
        console.error('Dashboard error:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, [userId]);

  const handleQuestionnaireComplete = (analysis: any) => {
    setShowQuestionnaire(false);
    // Refresh dashboard data after questionnaire completion
    window.location.reload();
  };

  if (isLoading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading your dashboard...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="dashboard-error">
        <p>Error loading dashboard: {error}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  // Check questionnaire completion status
  const questionnaireCompleted = data?.questionnaireStatus?.completed || 
                                  data?.userProfile?.questionnaire_completed || 
                                  data?.recommendations?.questionnaire_status === 'completed';

  if (showQuestionnaire) {
    return (
      <div className="dashboard">
        <OnboardingQuestionnaire
          userId={userId}
          onComplete={handleQuestionnaireComplete}
        />
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Welcome back, {data.userProfile?.name || 'User'}!</h1>
        <p>Your AI-powered career development hub</p>
      </div>

      {/* Questionnaire Status Banner */}
      {!questionnaireCompleted && (
        <div className="questionnaire-banner">
          <div className="banner-content">
            <AlertCircle size={24} className="banner-icon warning" />
            <div className="banner-text">
              <h3>Complete Your Career Profile</h3>
              <p>Unlock personalized AI recommendations by completing our career questionnaire.</p>
            </div>
            <button 
              onClick={() => setShowQuestionnaire(true)}
              className="start-questionnaire-btn"
            >
              Start Questionnaire
            </button>
          </div>
        </div>
      )}

      {questionnaireCompleted && (
        <div className="questionnaire-banner completed">
          <div className="banner-content">
            <CheckCircle size={24} className="banner-icon success" />
            <div className="banner-text">
              <h3>Career Profile Complete!</h3>
              <p>Your personalized AI recommendations are now available.</p>
            </div>
          </div>
        </div>
      )}

      <div className="dashboard-grid">
        {/* Quick Actions */}
        <div className="dashboard-card quick-actions">
          <h2>Quick Actions</h2>
          <div className="action-buttons">
            <Link to="/analysis" className="action-btn">
              <Brain size={24} />
              <div>
                <h3>Career Analysis</h3>
                <p>Get AI insights about your career path</p>
              </div>
            </Link>
            
            <Link to="/chat" className="action-btn">
              <MessageSquare size={24} />
              <div>
                <h3>AI Chat</h3>
                <p>Get instant career advice</p>
              </div>
            </Link>
            
            <Link to="/analytics" className="action-btn">
              <TrendingUp size={24} />
              <div>
                <h3>Market Trends</h3>
                <p>Explore industry analytics</p>
              </div>
            </Link>
          </div>
        </div>

        {/* Profile Summary */}
        <div className="dashboard-card profile-summary">
          <h2>
            <User size={20} />
            Profile Summary
          </h2>
          {data.userProfile ? (
            <div className="profile-info">
              <div className="profile-item">
                <strong>Education:</strong>
                <span>{data.userProfile.education_level || 'Not specified'}</span>
              </div>
              <div className="profile-item">
                <strong>Career Stage:</strong>
                <span>{data.userProfile.career_stage || 'Not specified'}</span>
              </div>
              <div className="profile-item">
                <strong>Location:</strong>
                <span>{data.userProfile.location || 'Not specified'}</span>
              </div>
              <Link to="/profile" className="edit-profile-btn">
                Edit Profile
              </Link>
            </div>
          ) : (
            <p>Profile information not available</p>
          )}
        </div>

        {/* Recent Activity */}
        <div className="dashboard-card recent-activity">
          <h2>
            <MessageSquare size={20} />
            Recent Conversations
          </h2>
          {data.recentConversations.length > 0 ? (
            <div className="conversation-list">
              {data.recentConversations.slice(0, 3).map((conv, index) => (
                <div key={index} className="conversation-item">
                  <div className="conversation-agent">
                    {conv.agent_name || 'AI Assistant'}
                  </div>
                  <div className="conversation-preview">
                    {conv.user_message?.substring(0, 60)}...
                  </div>
                  <div className="conversation-time">
                    {new Date(conv.timestamp).toLocaleDateString()}
                  </div>
                </div>
              ))}
              <Link to="/chat" className="view-all-btn">
                View All Conversations
              </Link>
            </div>
          ) : (
            <div className="no-activity">
              <p>No recent conversations</p>
              <Link to="/chat" className="start-chat-btn">
                Start Your First Chat
              </Link>
            </div>
          )}
        </div>

        {/* System Status */}
        <div className="dashboard-card system-status">
          <h2>
            <Award size={20} />
            System Status
          </h2>
          {data.systemMetrics ? (
            <div className="metrics-grid">
              <div className="metric">
                <div className="metric-value">
                  {data.systemMetrics.agent_metrics ? 
                    Object.keys(data.systemMetrics.agent_metrics).length : 0}
                </div>
                <div className="metric-label">Active Agents</div>
              </div>
              <div className="metric">
                <div className="metric-value status-operational">
                  ✓
                </div>
                <div className="metric-label">System Health</div>
              </div>
            </div>
          ) : (
            <p>System metrics not available</p>
          )}
        </div>

        {/* Recommendations Preview */}
        {data.recommendations && (
          <div className="dashboard-card recommendations-preview">
            <h2>
              <Target size={20} />
              Career Recommendations
            </h2>
            <div className="recommendations-content">
              {data.recommendations.requires_questionnaire ? (
                <div className="questionnaire-required">
                  <AlertCircle size={20} className="warning-icon" />
                  <div>
                    <strong>Questionnaire Required</strong>
                    <p>Complete your career questionnaire to unlock personalized AI recommendations</p>
                    <button 
                      onClick={() => setShowQuestionnaire(true)}
                      className="complete-questionnaire-btn"
                    >
                      Complete Questionnaire
                    </button>
                  </div>
                </div>
              ) : data.recommendations.recommendations?.length > 0 ? (
                <>
                  <div className="recommendation-highlight">
                    <strong>{questionnaireCompleted ? 'Personalized Recommendation:' : 'Top Recommendation:'}</strong>
                    <p>{data.recommendations.recommendations[0]}</p>
                  </div>
                  <div className="recommendation-meta">
                    <span className="confidence-score">
                      Confidence: {Math.round((data.recommendations.confidence || 0) * 100)}%
                    </span>
                    {data.recommendations.personalized && (
                      <span className="personalized-badge">
                        <CheckCircle size={16} />
                        Personalized
                      </span>
                    )}
                  </div>
                  <Link to="/analysis" className="view-all-recommendations">
                    View All Recommendations
                  </Link>
                </>
              ) : (
                <div className="no-recommendations">
                  <p>Complete your career analysis to get personalized recommendations</p>
                  <Link to="/analysis" className="get-recommendations-btn">
                    Get Recommendations
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;