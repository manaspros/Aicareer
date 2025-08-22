import React, { useState, useEffect } from 'react';
import { Brain, Target, TrendingUp, Award, Play, RefreshCw, Download } from 'lucide-react';
import ApiService from '../services/api';

interface CareerAnalysisProps {
  userId: string;
}

interface AnalysisResult {
  request_id: string;
  analysis_type: string;
  results: any;
  confidence: number;
  processing_time_ms: number;
}

const CareerAnalysis: React.FC<CareerAnalysisProps> = ({ userId }) => {
  const [selectedAnalysis, setSelectedAnalysis] = useState<string>('personality_assessment');
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<AnalysisResult | null>(null);
  const [recommendations, setRecommendations] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const analysisTypes = [
    {
      id: 'personality_assessment',
      name: 'Personality Assessment',
      description: 'Discover your Big Five personality traits and how they relate to career success',
      icon: Brain
    },
    {
      id: 'interest_analysis',
      name: 'Interest Analysis', 
      description: 'Explore your interests using the Holland Code (RIASEC) framework',
      icon: Target
    },
    {
      id: 'skill_gap_analysis',
      name: 'Skill Gap Analysis',
      description: 'Identify skill gaps and opportunities for professional development',
      icon: TrendingUp
    },
    {
      id: 'career_matching',
      name: 'Career Matching',
      description: 'Find careers that match your personality, interests, and skills',
      icon: Award
    }
  ];

  useEffect(() => {
    loadRecommendations();
  }, [userId]);

  const loadRecommendations = async () => {
    try {
      const recs = await ApiService.getCareerRecommendations(userId);
      setRecommendations(recs);
    } catch (error) {
      console.error('Failed to load recommendations:', error);
    }
  };

  const runAnalysis = async () => {
    setIsRunning(true);
    setError(null);
    setResults(null);

    try {
      const result = await ApiService.performCareerAnalysis({
        user_id: userId,
        analysis_type: selectedAnalysis
      });
      
      setResults(result);
      
      // Reload recommendations after analysis
      await loadRecommendations();
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Analysis failed');
      console.error('Analysis error:', error);
    } finally {
      setIsRunning(false);
    }
  };

  const renderPersonalityResults = (results: any) => {
    const traits = results.personality_scores || {};
    return (
      <div className="personality-results">
        <h3>Big Five Personality Traits</h3>
        <div className="trait-bars">
          {Object.entries(traits).map(([trait, score]: [string, any]) => (
            <div key={trait} className="trait-bar">
              <div className="trait-label">
                {trait.charAt(0).toUpperCase() + trait.slice(1)}
              </div>
              <div className="progress-container">
                <div 
                  className="progress-bar"
                  style={{ width: `${(score as number) * 100}%` }}
                />
                <span className="score-text">{Math.round((score as number) * 100)}%</span>
              </div>
            </div>
          ))}
        </div>
        {results.personality_analysis && (
          <div className="analysis-text">
            <h4>Analysis</h4>
            <p>{results.personality_analysis}</p>
          </div>
        )}
      </div>
    );
  };

  const renderInterestResults = (results: any) => {
    const interests = results.interest_scores || {};
    const codes = ['Realistic', 'Investigative', 'Artistic', 'Social', 'Enterprising', 'Conventional'];
    
    return (
      <div className="interest-results">
        <h3>Holland Code (RIASEC) Analysis</h3>
        <div className="interest-grid">
          {codes.map(code => (
            <div key={code} className="interest-item">
              <div className="interest-name">{code}</div>
              <div className="interest-score">
                {Math.round((interests[code.toLowerCase()] || 0) * 100)}%
              </div>
              <div className="interest-bar">
                <div 
                  className="interest-fill"
                  style={{ width: `${(interests[code.toLowerCase()] || 0) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
        {results.interest_analysis && (
          <div className="analysis-text">
            <h4>Interest Profile</h4>
            <p>{results.interest_analysis}</p>
          </div>
        )}
      </div>
    );
  };

  const renderCareerMatches = (results: any) => {
    const matches = results.career_matches || [];
    return (
      <div className="career-matches">
        <h3>Career Matches</h3>
        <div className="matches-list">
          {matches.slice(0, 5).map((match: any, index: number) => (
            <div key={index} className="match-item">
              <div className="match-header">
                <h4>{match.career_title}</h4>
                <div className="match-score">
                  {Math.round(match.match_score)}% match
                </div>
              </div>
              <p className="match-reasoning">{match.reasoning}</p>
              {match.recommended_actions && match.recommended_actions.length > 0 && (
                <div className="recommended-actions">
                  <strong>Next steps:</strong>
                  <ul>
                    {match.recommended_actions.slice(0, 3).map((action: string, i: number) => (
                      <li key={i}>{action}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderSkillGapResults = (results: any) => {
    const assessmentStage = results.assessment_stage;
    
    if (assessmentStage === 'skill_questions') {
      return (
        <div className="skill-gap-results">
          <h3>Skill Assessment</h3>
          <div className="assessment-stage">
            <p>Ready to begin your skill assessment! Please provide information about your current skills and experience level.</p>
            <div className="assessment-prompt">
              <h4>Next Steps:</h4>
              <ol>
                <li>Describe your current technical skills</li>
                <li>Rate your experience level in each area</li>
                <li>Share any relevant projects or work experience</li>
                <li>Specify your target role or career goals</li>
              </ol>
            </div>
          </div>
        </div>
      );
    }
    
    // Handle skill gaps if provided
    const skillGaps = results.skill_gaps || [];
    const recommendations = results.recommendations || [];
    
    if (skillGaps.length > 0 || recommendations.length > 0) {
      return (
        <div className="skill-gap-results">
          <h3>Skill Gap Analysis</h3>
          {skillGaps.length > 0 && (
            <div className="skill-gaps">
              <h4>Identified Skill Gaps</h4>
              <div className="gaps-list">
                {skillGaps.map((gap: any, index: number) => (
                  <div key={index} className="gap-item">
                    <div className="gap-skill">{gap.skill}</div>
                    <div className="gap-level">Current: {gap.current_level} → Target: {gap.target_level}</div>
                    <div className="gap-priority">{gap.priority} priority</div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {recommendations.length > 0 && (
            <div className="skill-recommendations">
              <h4>Recommendations</h4>
              <ul>
                {recommendations.map((rec: string, index: number) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      );
    }
    
    return (
      <div className="skill-gap-results">
        <h3>Skill Gap Analysis</h3>
        <p>Complete the skill assessment to receive detailed gap analysis and recommendations.</p>
      </div>
    );
  };

  const renderResults = () => {
    if (!results) return null;

    return (
      <div className="analysis-results">
        <div className="results-header">
          <h2>Analysis Results</h2>
          <div className="results-meta">
            <span className="confidence">
              Confidence: {Math.round(results.confidence)}%
            </span>
            <span className="processing-time">
              Processed in {results.processing_time_ms}ms
            </span>
          </div>
        </div>

        <div className="results-content">
          {selectedAnalysis === 'personality_assessment' && renderPersonalityResults(results.results)}
          {selectedAnalysis === 'interest_analysis' && renderInterestResults(results.results)}
          {selectedAnalysis === 'career_matching' && renderCareerMatches(results.results)}
          {selectedAnalysis === 'skill_gap_analysis' && renderSkillGapResults(results.results)}
        </div>
      </div>
    );
  };

  return (
    <div className="career-analysis">
      <div className="analysis-header">
        <Brain size={48} className="analysis-icon" />
        <div>
          <h1>Career Analysis</h1>
          <p>Discover insights about your personality, interests, and career potential</p>
        </div>
      </div>

      <div className="analysis-content">
        <div className="analysis-selector">
          <h2>Choose Analysis Type</h2>
          <div className="analysis-types">
            {analysisTypes.map((type) => (
              <div
                key={type.id}
                className={`analysis-type ${selectedAnalysis === type.id ? 'selected' : ''}`}
                onClick={() => setSelectedAnalysis(type.id)}
              >
                <type.icon size={24} />
                <div className="type-info">
                  <h3>{type.name}</h3>
                  <p>{type.description}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="analysis-controls">
            <button
              onClick={runAnalysis}
              disabled={isRunning}
              className="run-analysis-btn"
            >
              {isRunning ? (
                <>
                  <RefreshCw size={20} className="spinning" />
                  Running Analysis...
                </>
              ) : (
                <>
                  <Play size={20} />
                  Run Analysis
                </>
              )}
            </button>
          </div>

          {error && (
            <div className="error-message">
              <p>Error: {error}</p>
            </div>
          )}
        </div>

        {renderResults()}

        {recommendations && (
          <div className="recommendations-section">
            <h2>
              <Target size={24} />
              Career Recommendations
            </h2>
            {recommendations.recommendations?.length > 0 ? (
              <div className="recommendations-content">
                <div className="recommendations-list">
                  {recommendations.recommendations.map((rec: string, index: number) => (
                    <div key={index} className="recommendation-item">
                      <Award size={16} />
                      <span>{rec}</span>
                    </div>
                  ))}
                </div>
                <div className="recommendations-meta">
                  <p><strong>Explanation:</strong> {recommendations.explanation}</p>
                  <p><strong>Confidence:</strong> {Math.round(recommendations.confidence * 100)}%</p>
                </div>
              </div>
            ) : (
              <p>Complete an analysis to get personalized recommendations.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default CareerAnalysis;