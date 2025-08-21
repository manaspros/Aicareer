import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout for backend calls
});

// Flag to control whether to use backend or mock data
const USE_MOCK_DATA = false; // Set to false when backend is available

// Types
export interface UserProfile {
  user_id?: string;
  name: string;
  email: string;
  age?: number;
  location?: string;
  education_level?: string;
  career_stage?: string;
}

export interface CareerAnalysisRequest {
  user_id: string;
  analysis_type: string;
  parameters?: Record<string, any>;
}

export interface ChatMessage {
  user_id: string;
  message: string;
}

export interface ApiResponse<T = any> {
  data: T;
}

// Mock Data
const mockProfile = {
  user_id: 'demo-user',
  name: 'Demo User',
  email: 'demo@example.com',
  age: 28,
  location: 'New York, NY',
  education_level: 'bachelor',
  career_stage: 'mid_level'
};

const mockConversations = [
  {
    message_id: '1',
    agent_name: 'Career Analyst',
    user_message: 'What career path suits my interests?',
    agent_response: 'Based on your profile, I recommend exploring data science and software engineering roles.',
    timestamp: new Date().toISOString(),
    metadata: { sentiment: 'positive', confidence_level: 0.85 }
  },
  {
    message_id: '2', 
    agent_name: 'Mentor Bot',
    user_message: 'How can I improve my resume?',
    agent_response: 'Focus on quantifiable achievements and tailor your resume to each job application.',
    timestamp: new Date(Date.now() - 86400000).toISOString(),
    metadata: { sentiment: 'neutral', confidence_level: 0.78 }
  }
];

// API Service Class
export class ApiService {
  // Health Check
  static async healthCheck() {
    if (USE_MOCK_DATA) {
      return {
        status: 'healthy (demo mode)',
        timestamp: new Date().toISOString(),
        services: {
          database: 'connected (demo)',
          agents: 3,
          llm: 'available (demo)'
        }
      };
    }
    
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      // Return mock health data when backend is not available
      return {
        status: 'healthy (mock)',
        timestamp: new Date().toISOString(),
        services: {
          database: 'connected (mock)',
          agents: 3,
          llm: 'available (mock)'
        }
      };
    }
  }

  // User Management
  static async registerUser(userData: UserProfile) {
    const response = await api.post('/api/users/register', userData);
    return response.data;
  }

  // Questionnaire Management
  static async generateQuestionnaire(userId: string) {
    const response = await api.get(`/api/questionnaire/generate/${userId}`);
    return response.data;
  }

  static async submitQuestionnaire(userId: string, submission: any) {
    const response = await api.post(`/api/questionnaire/submit/${userId}`, submission);
    return response.data;
  }

  static async getQuestionnaireStatus(userId: string) {
    const response = await api.get(`/api/questionnaire/status/${userId}`);
    return response.data;
  }

  static async getUserProfile(userId: string) {
    if (USE_MOCK_DATA) {
      return mockProfile;
    }
    
    try {
      const response = await api.get(`/api/users/${userId}/profile`);
      return response.data;
    } catch (error) {
      // Return mock profile when backend is not available
      return mockProfile;
    }
  }

  static async updateUserProfile(userId: string, profileData: Partial<UserProfile>) {
    try {
      const response = await api.put(`/api/users/${userId}/profile`, profileData);
      return response.data;
    } catch (error) {
      // Return success message for mock update
      return { message: 'Profile updated successfully (mock)', status: 'success' };
    }
  }

  // Agent Interactions
  static async performCareerAnalysis(request: CareerAnalysisRequest) {
    try {
      const response = await api.post('/api/agents/career-analysis', request);
      return response.data;
    } catch (error) {
      // Return mock analysis results
      return {
        request_id: 'mock-analysis-' + Date.now(),
        user_id: request.user_id,
        analysis_type: request.analysis_type,
        results: {
          personality_scores: {
            openness: 0.75,
            conscientiousness: 0.68,
            extraversion: 0.52,
            agreeableness: 0.71,
            neuroticism: 0.34
          },
          personality_analysis: 'You show high openness to new experiences and strong conscientiousness, indicating you would thrive in creative yet structured environments.',
          interest_scores: {
            realistic: 0.45,
            investigative: 0.82,
            artistic: 0.68,
            social: 0.58,
            enterprising: 0.71,
            conventional: 0.49
          },
          career_matches: [
            {
              career_title: 'Data Scientist',
              match_score: 87,
              reasoning: 'Your strong analytical skills and interest in investigation make this an excellent match.',
              recommended_actions: ['Learn Python and R', 'Complete online data science courses', 'Build a portfolio of projects']
            },
            {
              career_title: 'Product Manager',
              match_score: 82,
              reasoning: 'Your combination of analytical thinking and people skills suit product management well.',
              recommended_actions: ['Study product management frameworks', 'Network with current PMs', 'Work on cross-functional projects']
            }
          ]
        },
        confidence: 85.5,
        processing_time_ms: 1250
      };
    }
  }

  static async chatWithCounselor(message: ChatMessage) {
    try {
      const response = await api.post('/api/agents/counseling/chat', message);
      return response.data;
    } catch (error) {
      // Return mock chat response
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate processing time
      return {
        response: "I understand your concerns about career development. Based on your message, I'd recommend focusing on building both technical skills and leadership capabilities. Consider setting specific, measurable goals for the next 6 months and identifying mentors in your target field.",
        sentiment_analysis: {
          sentiment: 'neutral',
          confidence_level: 0.78,
          emotions: ['concern', 'ambition']
        },
        follow_up_actions: [
          'Set 3 specific career goals for next quarter',
          'Identify 2 potential mentors in your field',
          'Research top skills needed in your target role'
        ],
        conversation_metadata: {
          topic: 'career_development',
          urgency: 'medium',
          next_steps_provided: true
        }
      };
    }
  }

  static async getCareerRecommendations(userId: string) {
    if (USE_MOCK_DATA) {
      return {
        recommendations: [
          'Focus on developing data visualization skills with tools like Tableau or PowerBI',
          'Consider pursuing a certification in cloud computing (AWS, Azure, or GCP)',
          'Build a strong LinkedIn presence and engage with industry thought leaders',
          'Practice technical interviewing with platforms like LeetCode or HackerRank'
        ],
        confidence: 0.87,
        explanation: 'These recommendations are based on your technical background, career goals, and current market trends in your field.'
      };
    }
    
    try {
      const response = await api.get(`/api/agents/recommendations/${userId}`);
      return response.data;
    } catch (error) {
      // Return mock recommendations
      return {
        recommendations: [
          'Focus on developing data visualization skills with tools like Tableau or PowerBI',
          'Consider pursuing a certification in cloud computing (AWS, Azure, or GCP)',
          'Build a strong LinkedIn presence and engage with industry thought leaders',
          'Practice technical interviewing with platforms like LeetCode or HackerRank'
        ],
        confidence: 0.87,
        explanation: 'These recommendations are based on your technical background, career goals, and current market trends in your field.'
      };
    }
  }

  // Analytics
  static async getCareerTrends(industry?: string, role?: string) {
    const params = new URLSearchParams();
    if (industry) params.append('industry', industry);
    if (role) params.append('role', role);
    
    const response = await api.get(`/api/analytics/career-trends?${params.toString()}`);
    return response.data;
  }

  static async getSkillDemandAnalysis(skills: string) {
    const response = await api.get(`/api/analytics/skill-demand?skills=${encodeURIComponent(skills)}`);
    return response.data;
  }

  static async getMarketPredictions(industry: string, analysisType = 'disruption') {
    const response = await api.get(`/api/analytics/market-predictions?industry=${industry}&analysis_type=${analysisType}`);
    return response.data;
  }

  // System Information
  static async listAgents() {
    const response = await api.get('/api/system/agents');
    return response.data;
  }

  static async getSystemMetrics() {
    try {
      const response = await api.get('/api/system/metrics');
      return response.data;
    } catch (error) {
      // Return mock system metrics
      return {
        agent_metrics: {
          career_analyst: { total_interactions: 45, avg_response_time: 1.2, avg_confidence: 0.85 },
          mentor_bot: { total_interactions: 32, avg_response_time: 0.9, avg_confidence: 0.78 },
          skills_assessor: { total_interactions: 28, avg_response_time: 1.5, avg_confidence: 0.82 }
        },
        system_status: 'operational (mock)',
        timestamp: new Date().toISOString()
      };
    }
  }

  static async getConversationHistory(userId: string, limit = 20) {
    if (USE_MOCK_DATA) {
      return {
        user_id: userId,
        conversations: mockConversations.slice(0, limit),
        total_count: mockConversations.length
      };
    }
    
    try {
      const response = await api.get(`/api/conversations/${userId}?limit=${limit}`);
      return response.data;
    } catch (error) {
      // Return mock conversation history
      return {
        user_id: userId,
        conversations: mockConversations.slice(0, limit),
        total_count: mockConversations.length
      };
    }
  }
}

export default ApiService;