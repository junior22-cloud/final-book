import React, { useState } from 'react';
import './App.css';

function App() {
  const [topic, setTopic] = useState('');

  // Simplified Payment Redirect Function
  const redirectToPayment = (tier = null) => {
    // Simple validation - ensure topic is entered
    if (!topic || topic.trim() === '') {
      alert("Please enter a book topic first!");
      document.getElementById('topic').focus();
      return;
    }

    // If no tier specified, show pricing first
    if (!tier) {
      // Show pricing section logic would go here
      return;
    }

    // DIRECTLY go to checkout with topic and tier
    const encodedTopic = encodeURIComponent(topic.trim());
    window.location.href = `/api/checkout?topic=${encodedTopic}&tier=${tier}`;
  };

  return (
    <div className="App">
      {/* Countdown Banner */}
      <div className="countdown-banner">
        <h4>🔥 LIMITED TIME OFFER</h4>
        <div className="countdown-timer">
          5 DAYS LEFT AT CURRENT PRICES
        </div>
      </div>

      {/* Hero Section */}
      <div className="hero">
        <h1>📖 WizBook.io</h1>
        <p>Professional AI Books for Business Leaders</p>
        
        <div className="features">
          <div className="feature">
            <span className="feature-icon">⚡</span>
            <h3>Enterprise Quality</h3>
            <p>Professional books with audio narration and premium covers</p>
          </div>
          <div className="feature">
            <span className="feature-icon">🎨</span>
            <h3>White Label Ready</h3>
            <p>Remove branding and get commercial rights for your business</p>
          </div>
          <div className="feature">
            <span className="feature-icon">📄</span>
            <h3>Multi-Format</h3>
            <p>PDF, DOCX, and AI audio narration included</p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container">
        <div className="card">
          <h2>Create Your Book</h2>

          <div className="input-group">
            <label htmlFor="topic">📚 What's your book about?</label>
            <input
              id="topic"
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Python Programming, Digital Marketing, Coffee Shop Business Plan"
            />
          </div>

          <div className="button-section">
            <button 
              className="btn btn-primary" 
              onClick={() => redirectToPayment()}
            >
              📖 Create My Book →
            </button>
          </div>
        </div>

        {/* Pricing Section */}
        <div className="card">
          <h2>Choose Your Book Package</h2>
          <p>Topic: <strong>{topic || 'Enter topic above'}</strong></p>

          <div className="pricing-grid">
            {/* Basic Tier */}
            <div className="pricing-card" onClick={() => redirectToPayment('basic')}>
              <h3>BASIC</h3>
              <div className="price">$47 <span className="old-price">$67</span></div>
              <div className="delivery-time">24hr delivery</div>
              <ul>
                <li>AI-generated PDF</li>
                <li>Standard cover</li>
                <li>Watermarked footer</li>
                <li>Email delivery</li>
              </ul>
              <button className="btn">Get Started</button>
            </div>

            {/* Pro Tier */}
            <div className="pricing-card highlighted" onClick={() => redirectToPayment('pro')}>
              <div className="badge">BEST VALUE - SAVE $50</div>
              <h3>PROFESSIONAL</h3>
              <div className="price">$97 <span className="old-price">$147</span></div>
              <div className="delivery-time">12hr delivery</div>
              <ul>
                <li><strong>Everything in Basic +</strong></li>
                <li>AI Audio narration</li>
                <li>Editable DOCX files</li>
                <li>3 premium covers</li>
                <li>Priority support</li>
              </ul>
              <button className="btn btn-primary">Get Pro</button>
            </div>

            {/* White Label Tier */}
            <div className="pricing-card" onClick={() => redirectToPayment('whitelabel')}>
              <div className="badge business">BUSINESS - SAVE $200</div>
              <h3>WHITE LABEL</h3>
              <div className="price">$497 <span className="old-price">$697</span></div>
              <div className="delivery-time">Instant access</div>
              <ul>
                <li><strong>Everything in Pro +</strong></li>
                <li>Remove all branding</li>
                <li>Full commercial rights</li>
                <li>100 books/month license</li>
                <li>API access</li>
              </ul>
              <button className="btn business">Start Business</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;