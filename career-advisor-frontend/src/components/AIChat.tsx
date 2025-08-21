import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Loader, MessageSquare, RefreshCw } from 'lucide-react';
import ApiService from '../services/api';

interface AIChatProps {
  userId: string;
}

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  metadata?: any;
}

const AIChat: React.FC<AIChatProps> = ({ userId }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadChatHistory();
  }, [userId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadChatHistory = async () => {
    try {
      const response = await ApiService.getConversationHistory(userId, 20);
      const historyMessages: ChatMessage[] = response.conversations.map((conv: any, index: number) => [
        {
          id: `${conv.message_id}-user`,
          type: 'user' as const,
          content: conv.user_message,
          timestamp: new Date(conv.timestamp),
        },
        {
          id: `${conv.message_id}-assistant`,
          type: 'assistant' as const,
          content: conv.agent_response,
          timestamp: new Date(conv.timestamp),
          metadata: conv.metadata,
        }
      ]).flat();

      // Sort by timestamp
      historyMessages.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
      setMessages(historyMessages);
    } catch (error) {
      console.error('Failed to load chat history:', error);
      setError('Failed to load chat history');
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await ApiService.chatWithCounselor({
        user_id: userId,
        message: inputMessage
      });

      const assistantMessage: ChatMessage = {
        id: `${Date.now()}-assistant`,
        type: 'assistant',
        content: response.response,
        timestamp: new Date(),
        metadata: response.sentiment_analysis,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to send message');
      console.error('Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  if (isLoadingHistory) {
    return (
      <div className="chat-loading">
        <div className="loading-spinner"></div>
        <p>Loading chat history...</p>
      </div>
    );
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="chat-title">
          <MessageSquare size={24} />
          <h1>AI Career Counselor</h1>
        </div>
        <div className="chat-actions">
          <button onClick={loadChatHistory} className="refresh-btn" title="Refresh">
            <RefreshCw size={18} />
          </button>
          <button onClick={clearChat} className="clear-btn" title="Clear Chat">
            Clear
          </button>
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && !isLoading && (
          <div className="welcome-message">
            <Bot size={48} className="welcome-icon" />
            <h2>Welcome to AI Career Counseling!</h2>
            <p>Ask me anything about your career development, job search, skills, or professional goals.</p>
            <div className="sample-questions">
              <p>Try asking:</p>
              <ul>
                <li>"What career path suits my interests?"</li>
                <li>"How can I improve my resume?"</li>
                <li>"What skills should I develop for my field?"</li>
                <li>"I'm feeling stuck in my career, what should I do?"</li>
              </ul>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div key={message.id} className={`message ${message.type}`}>
            <div className="message-avatar">
              {message.type === 'user' ? (
                <User size={20} />
              ) : (
                <Bot size={20} />
              )}
            </div>
            <div className="message-content">
              <div className="message-text">
                {message.content}
              </div>
              {message.metadata && (
                <div className="message-metadata">
                  <small>
                    Sentiment: {message.metadata.sentiment || 'neutral'} 
                    {message.metadata.confidence_level && 
                      ` (${Math.round(message.metadata.confidence_level * 100)}% confidence)`
                    }
                  </small>
                </div>
              )}
              <div className="message-time">
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message assistant">
            <div className="message-avatar">
              <Bot size={20} />
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <Loader size={16} className="spinning" />
                AI is thinking...
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="chat-error">
          <p>Error: {error}</p>
          <button onClick={() => setError(null)} className="dismiss-btn">
            Dismiss
          </button>
        </div>
      )}

      <form onSubmit={handleSendMessage} className="chat-input-form">
        <div className="chat-input-container">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Ask me about your career development..."
            disabled={isLoading}
            className="chat-input"
            maxLength={500}
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || isLoading}
            className="send-btn"
          >
            {isLoading ? (
              <Loader size={18} className="spinning" />
            ) : (
              <Send size={18} />
            )}
          </button>
        </div>
        <div className="input-helper">
          <small>{inputMessage.length}/500 characters</small>
        </div>
      </form>
    </div>
  );
};

export default AIChat;