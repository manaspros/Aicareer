import React, { useState, useEffect } from 'react';
import ApiService from '../services/api';

interface Question {
  id: string;
  question: string;
  question_type: string;
  options?: string[];
  scale_min?: number;
  scale_max?: number;
  category: string;
  importance: number;
}

interface QuestionnaireProps {
  userId: string;
  onComplete: (analysis: any) => void;
}

const OnboardingQuestionnaire: React.FC<QuestionnaireProps> = ({ userId, onComplete }) => {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [responses, setResponses] = useState<{[key: string]: any}>({});
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadQuestionnaire();
  }, [userId]);

  const loadQuestionnaire = async () => {
    try {
      setIsLoading(true);
      const data = await ApiService.generateQuestionnaire(userId);
      setQuestions(data.questions);
      setIsLoading(false);
    } catch (err: any) {
      setError('Failed to load questionnaire. Please try again.');
      setIsLoading(false);
    }
  };

  const handleResponse = (questionId: string, response: any) => {
    setResponses(prev => ({
      ...prev,
      [questionId]: response
    }));
  };

  const goToNext = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  };

  const goToPrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  const submitQuestionnaire = async () => {
    try {
      setIsSubmitting(true);
      
      // Convert responses to expected format
      const responseArray = Object.entries(responses).map(([questionId, response]) => ({
        question_id: questionId,
        response: response,
        timestamp: new Date().toISOString()
      }));

      const submission = {
        questions: questions,
        responses: responseArray
      };

      const result = await ApiService.submitQuestionnaire(userId, submission);
      onComplete(result.analysis);
      
    } catch (err: any) {
      setError('Failed to submit questionnaire. Please try again.');
      setIsSubmitting(false);
    }
  };

  const renderQuestion = (question: Question) => {
    const currentResponse = responses[question.id];

    switch (question.question_type) {
      case 'multiple_choice':
        return (
          <div className="question-options">
            {question.options?.map((option, index) => (
              <label key={index} className="option-label">
                <input
                  type="radio"
                  name={question.id}
                  value={option}
                  checked={currentResponse === option}
                  onChange={(e) => handleResponse(question.id, e.target.value)}
                />
                <span className="option-text">{option}</span>
              </label>
            ))}
          </div>
        );

      case 'scale':
        return (
          <div className="scale-question">
            <div className="scale-labels">
              <span>{question.scale_min}</span>
              <span>{question.scale_max}</span>
            </div>
            <input
              type="range"
              min={question.scale_min}
              max={question.scale_max}
              value={currentResponse || Math.floor(((question.scale_max || 10) + (question.scale_min || 1)) / 2)}
              onChange={(e) => handleResponse(question.id, parseInt(e.target.value))}
              className="scale-slider"
            />
            <div className="scale-value">
              Current value: {currentResponse || Math.floor(((question.scale_max || 10) + (question.scale_min || 1)) / 2)}
            </div>
          </div>
        );

      case 'text':
      default:
        return (
          <div className="text-question">
            <textarea
              value={currentResponse || ''}
              onChange={(e) => handleResponse(question.id, e.target.value)}
              placeholder="Share your thoughts here..."
              className="response-textarea"
              rows={4}
            />
          </div>
        );
    }
  };

  if (isLoading) {
    return (
      <div className="questionnaire-container">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Generating your personalized questionnaire...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="questionnaire-container">
        <div className="error-state">
          <h2>⚠️ Something went wrong</h2>
          <p>{error}</p>
          <button onClick={loadQuestionnaire} className="retry-btn">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div className="questionnaire-container">
        <div className="empty-state">
          <h2>No questions available</h2>
          <p>Please try again later.</p>
        </div>
      </div>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;
  const isLastQuestion = currentQuestionIndex === questions.length - 1;
  const canProceed = responses[currentQuestion.id] !== undefined && responses[currentQuestion.id] !== '';

  return (
    <div className="questionnaire-container">
      <div className="questionnaire-header">
        <h1>🎯 Career Profile Builder</h1>
        <p>Help us understand you better to provide personalized career guidance</p>
        
        <div className="progress-section">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <div className="progress-text">
            Question {currentQuestionIndex + 1} of {questions.length}
          </div>
        </div>
      </div>

      <div className="question-card">
        <div className="question-category">
          {currentQuestion.category.replace('_', ' ').toUpperCase()}
        </div>
        
        <h2 className="question-text">
          {currentQuestion.question}
        </h2>

        <div className="question-content">
          {renderQuestion(currentQuestion)}
        </div>
      </div>

      <div className="questionnaire-navigation">
        <button 
          onClick={goToPrevious}
          disabled={currentQuestionIndex === 0}
          className="nav-btn prev-btn"
        >
          ← Previous
        </button>

        <div className="nav-center">
          {isLastQuestion ? (
            <button 
              onClick={submitQuestionnaire}
              disabled={!canProceed || isSubmitting}
              className="submit-btn"
            >
              {isSubmitting ? 'Analyzing...' : 'Complete Questionnaire 🚀'}
            </button>
          ) : (
            <button 
              onClick={goToNext}
              disabled={!canProceed}
              className="nav-btn next-btn"
            >
              Next →
            </button>
          )}
        </div>

        <div className="question-counter">
          {currentQuestionIndex + 1}/{questions.length}
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
    </div>
  );
};

export default OnboardingQuestionnaire;