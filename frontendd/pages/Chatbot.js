import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

function Chatbot() {
  const [messages, setMessages] = useState([
    { type: 'bot', text: "Hello! 👋 I'm your AI stress support assistant. How are you feeling today? I'm here to help with stress management, breathing exercises, and relaxation tips." }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = input.trim();
    setMessages(prev => [...prev, { type: 'user', text: userMessage }]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/chat`, { message: userMessage });
      setMessages(prev => [...prev, { type: 'bot', text: response.data.response }]);
    } catch (err) {
      setMessages(prev => [...prev, { type: 'bot', text: "I'm having trouble connecting. Please try again." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickReplies = [
    { text: "I'm feeling stressed", emoji: "😰" },
    { text: "I need breathing exercises", emoji: "🌬️" },
    { text: "Help me relax", emoji: "🧘" },
    { text: "I can't sleep", emoji: "😴" },
    { text: "Work is overwhelming", emoji: "💼" }
  ];

  const handleQuickReply = (text) => {
    setInput(text);
    setTimeout(() => handleSend(), 100);
  };

  return (
    <div className="chatbot-container">
      <div className="dashboard-header" style={{ marginBottom: '1rem' }}>
        <h1>🤖 AI Stress Support</h1>
        <p>Chat with our AI assistant for stress relief tips</p>
      </div>

      {/* Quick Replies */}
      <div style={{ 
        display: 'flex', 
        flexWrap: 'wrap', 
        gap: '0.5rem', 
        marginBottom: '1rem' 
      }}>
        {quickReplies.map((reply, index) => (
          <button
            key={index}
            onClick={() => handleQuickReply(reply.text)}
            style={{
              padding: '0.5rem 1rem',
              background: 'rgba(99, 102, 241, 0.1)',
              border: '1px solid rgba(99, 102, 241, 0.3)',
              borderRadius: '50px',
              color: '#818cf8',
              cursor: 'pointer',
              fontSize: '0.85rem',
              transition: 'all 0.3s ease'
            }}
            onMouseOver={(e) => {
              e.target.style.background = 'rgba(99, 102, 241, 0.2)';
              e.target.style.transform = 'translateY(-2px)';
            }}
            onMouseOut={(e) => {
              e.target.style.background = 'rgba(99, 102, 241, 0.1)';
              e.target.style.transform = 'translateY(0)';
            }}
          >
            {reply.emoji} {reply.text}
          </button>
        ))}
      </div>

      {/* Chat Messages */}
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`chat-message ${msg.type}`}>
            <div className="message-content">
              {msg.type === 'bot' && <span style={{ marginRight: '0.5rem' }}>🤖</span>}
              {msg.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="chat-message bot">
            <div className="message-content" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span>🤖</span>
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input */}
      <div className="chat-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          disabled={loading}
        />
        <button onClick={handleSend} disabled={loading || !input.trim()}>
          {loading ? '...' : 'Send 📤'}
        </button>
      </div>

      {/* Tips Footer */}
      <div style={{ 
        marginTop: '1rem', 
        padding: '1rem', 
        background: 'rgba(255,255,255,0.02)', 
        borderRadius: '12px',
        fontSize: '0.85rem',
        color: '#888'
      }}>
        💡 <strong>Tip:</strong> Try asking about breathing exercises, meditation, sleep tips, or just share how you're feeling. I'm here to help!
      </div>
    </div>
  );
}

export default Chatbot;
