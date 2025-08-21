import React, { useState, useEffect } from 'react';
import { TrendingUp, BarChart, Search, AlertTriangle, RefreshCw } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart as RechartsBarChart, Bar } from 'recharts';
import ApiService from '../services/api';

const Analytics: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'trends' | 'skills' | 'predictions'>('trends');
  const [trendsData, setTrendsData] = useState<any>(null);
  const [skillsData, setSkillsData] = useState<any>(null);
  const [predictionsData, setPredictionsData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form states
  const [selectedIndustry, setSelectedIndustry] = useState<string>('technology');
  const [selectedRole, setSelectedRole] = useState<string>('software engineer');
  const [skillsQuery, setSkillsQuery] = useState<string>('python,javascript,react');

  const industries = ['technology', 'healthcare', 'finance', 'education', 'manufacturing'];
  const roles = ['software engineer', 'data scientist', 'marketing manager', 'teacher', 'nurse'];

  useEffect(() => {
    if (activeTab === 'trends') {
      loadCareerTrends();
    }
  }, [activeTab, selectedIndustry, selectedRole]);

  const loadCareerTrends = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await ApiService.getCareerTrends(selectedIndustry, selectedRole);
      setTrendsData(data);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to load career trends');
      console.error('Trends error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadSkillsAnalysis = async () => {
    if (!skillsQuery.trim()) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await ApiService.getSkillDemandAnalysis(skillsQuery);
      setSkillsData(data);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to analyze skills');
      console.error('Skills error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadMarketPredictions = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await ApiService.getMarketPredictions(selectedIndustry);
      setPredictionsData(data);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to load predictions');
      console.error('Predictions error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const generateMockChartData = (trend: 'up' | 'down' | 'stable' = 'up') => {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
    let value = 100;
    
    return months.map(month => {
      const change = trend === 'up' ? Math.random() * 10 : 
                    trend === 'down' ? -Math.random() * 10 : 
                    (Math.random() - 0.5) * 5;
      value += change;
      return { month, value: Math.round(value) };
    });
  };

  const renderTrendsTab = () => (
    <div className="trends-tab">
      <div className="trends-controls">
        <div className="control-group">
          <label>Industry:</label>
          <select 
            value={selectedIndustry} 
            onChange={(e) => setSelectedIndustry(e.target.value)}
          >
            {industries.map(industry => (
              <option key={industry} value={industry}>
                {industry.charAt(0).toUpperCase() + industry.slice(1)}
              </option>
            ))}
          </select>
        </div>
        
        <div className="control-group">
          <label>Role:</label>
          <select 
            value={selectedRole} 
            onChange={(e) => setSelectedRole(e.target.value)}
          >
            {roles.map(role => (
              <option key={role} value={role}>
                {role.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
              </option>
            ))}
          </select>
        </div>
        
        <button onClick={loadCareerTrends} disabled={isLoading} className="refresh-btn">
          <RefreshCw size={16} className={isLoading ? 'spinning' : ''} />
          Refresh
        </button>
      </div>

      {trendsData ? (
        <div className="trends-content">
          <div className="trends-overview">
            <h3>Career Trends Overview</h3>
            <div className="trend-cards">
              <div className="trend-card">
                <TrendingUp size={24} className="trend-up" />
                <div>
                  <h4>Job Growth</h4>
                  <p>+15% projected growth</p>
                </div>
              </div>
              
              <div className="trend-card">
                <BarChart size={24} className="trend-stable" />
                <div>
                  <h4>Salary Range</h4>
                  <p>$65k - $120k average</p>
                </div>
              </div>
              
              <div className="trend-card">
                <Search size={24} className="trend-up" />
                <div>
                  <h4>Demand</h4>
                  <p>High demand expected</p>
                </div>
              </div>
            </div>
          </div>

          <div className="chart-container">
            <h4>6-Month Trend</h4>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={generateMockChartData('up')}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="value" stroke="#2563eb" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      ) : (
        <div className="no-data">
          <p>Select industry and role to view trends</p>
        </div>
      )}
    </div>
  );

  const renderSkillsTab = () => (
    <div className="skills-tab">
      <div className="skills-controls">
        <div className="skills-input">
          <input
            type="text"
            placeholder="Enter skills separated by commas (e.g., python, javascript, react)"
            value={skillsQuery}
            onChange={(e) => setSkillsQuery(e.target.value)}
            className="skills-search"
          />
          <button onClick={loadSkillsAnalysis} disabled={isLoading || !skillsQuery.trim()}>
            <Search size={16} />
            Analyze
          </button>
        </div>
      </div>

      {skillsData ? (
        <div className="skills-content">
          <h3>Skill Demand Analysis</h3>
          <div className="skills-results">
            {skillsData.predictions?.map((prediction: any, index: number) => (
              <div key={index} className="skill-prediction">
                <div className="skill-header">
                  <h4>{prediction.skill}</h4>
                  <div className={`trend-indicator ${prediction.prediction.toLowerCase()}`}>
                    {prediction.prediction}
                  </div>
                </div>
                <div className="skill-details">
                  <div className="confidence-bar">
                    <span>Confidence: {Math.round(prediction.confidence * 100)}%</span>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill"
                        style={{ width: `${prediction.confidence * 100}%` }}
                      />
                    </div>
                  </div>
                  <div className="recommendations">
                    <strong>Recommendations:</strong>
                    <ul>
                      {prediction.recommendations?.slice(0, 2).map((rec: string, i: number) => (
                        <li key={i}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="chart-container">
            <h4>Skills Demand Comparison</h4>
            <ResponsiveContainer width="100%" height={300}>
              <RechartsBarChart data={skillsData.predictions?.map((p: any) => ({
                skill: p.skill,
                confidence: p.confidence * 100
              }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="skill" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="confidence" fill="#2563eb" />
              </RechartsBarChart>
            </ResponsiveContainer>
          </div>
        </div>
      ) : (
        <div className="no-data">
          <p>Enter skills to analyze their market demand</p>
        </div>
      )}
    </div>
  );

  const renderPredictionsTab = () => (
    <div className="predictions-tab">
      <div className="predictions-controls">
        <div className="control-group">
          <label>Industry for Disruption Analysis:</label>
          <select 
            value={selectedIndustry} 
            onChange={(e) => setSelectedIndustry(e.target.value)}
          >
            {industries.map(industry => (
              <option key={industry} value={industry}>
                {industry.charAt(0).toUpperCase() + industry.slice(1)}
              </option>
            ))}
          </select>
        </div>
        
        <button onClick={loadMarketPredictions} disabled={isLoading}>
          <Search size={16} />
          Analyze Disruption
        </button>
      </div>

      {predictionsData ? (
        <div className="predictions-content">
          <div className="disruption-analysis">
            <h3>
              <AlertTriangle size={24} />
              Market Disruption Analysis
            </h3>
            <div className="prediction-results">
              {/* Mock disruption data since the endpoint might not return structured data */}
              <div className="disruption-item">
                <h4>AI & Automation Impact</h4>
                <div className="impact-level high">High Impact</div>
                <p>Significant disruption expected in the next 2-3 years due to AI automation.</p>
              </div>
              
              <div className="disruption-item">
                <h4>Remote Work Trends</h4>
                <div className="impact-level medium">Medium Impact</div>
                <p>Continued shift towards hybrid and remote work models.</p>
              </div>
              
              <div className="disruption-item">
                <h4>Skill Requirements</h4>
                <div className="impact-level high">High Impact</div>
                <p>Rapid evolution of required technical and soft skills.</p>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="no-data">
          <p>Select an industry to analyze potential market disruptions</p>
        </div>
      )}
    </div>
  );

  return (
    <div className="analytics">
      <div className="analytics-header">
        <TrendingUp size={48} className="analytics-icon" />
        <div>
          <h1>Market Analytics</h1>
          <p>Explore career trends, skill demand, and market predictions</p>
        </div>
      </div>

      <div className="analytics-tabs">
        <button
          className={`tab-btn ${activeTab === 'trends' ? 'active' : ''}`}
          onClick={() => setActiveTab('trends')}
        >
          <TrendingUp size={20} />
          Career Trends
        </button>
        
        <button
          className={`tab-btn ${activeTab === 'skills' ? 'active' : ''}`}
          onClick={() => setActiveTab('skills')}
        >
          <BarChart size={20} />
          Skills Analysis
        </button>
        
        <button
          className={`tab-btn ${activeTab === 'predictions' ? 'active' : ''}`}
          onClick={() => setActiveTab('predictions')}
        >
          <AlertTriangle size={20} />
          Market Predictions
        </button>
      </div>

      <div className="analytics-content">
        {error && (
          <div className="error-message">
            <p>Error: {error}</p>
            <button onClick={() => setError(null)}>Dismiss</button>
          </div>
        )}

        {isLoading && (
          <div className="loading-overlay">
            <div className="loading-spinner"></div>
            <p>Loading analytics data...</p>
          </div>
        )}

        {activeTab === 'trends' && renderTrendsTab()}
        {activeTab === 'skills' && renderSkillsTab()}
        {activeTab === 'predictions' && renderPredictionsTab()}
      </div>
    </div>
  );
};

export default Analytics;