import React, { useState, useEffect } from 'react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function WizBookApp() {
  const [step, setStep] = useState('home'); // home, generate, result
  const [formData, setFormData] = useState({
    topic: '',
    audience: 'beginners',
    style: 'professional'
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  // Auto-detect API URL based on environment
  const API_URL = BACKEND_URL;

  const handleGenerate = async () => {
    if (!formData.topic.trim()) {
      setError('Please enter a book topic');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_URL}/api/generate?topic=${encodeURIComponent(formData.topic)} for ${formData.audience} in ${formData.style} style`);
      
      if (!response.ok) {
        throw new Error(`Generation failed: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
      setStep('result');
    } catch (err) {
      setError('Failed to generate book. Please try again.');
      console.error('Error:', err);
    }

    setLoading(false);
  };

  const handleDownloadPDF = async () => {
    if (!result) return;

    try {
      const response = await fetch(`${API_URL}/api/pdf?topic=${encodeURIComponent(formData.topic)}`);
      
      if (!response.ok) {
        throw new Error('PDF generation failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${formData.topic.replace(/[^a-z0-9]/gi, '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('PDF download failed. Please try again.');
    }
  };

  const handlePayment = async () => {
    try {
      const response = await fetch(`${API_URL}/api/checkout?topic=${encodeURIComponent(formData.topic)}`);
      const data = await response.json();
      
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        setError('Payment setup required. Please add Stripe keys.');
      }
    } catch (err) {
      setError('Payment failed. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <h2 style={{color: 'white', marginBottom: '10px'}}>🤖 Creating your book...</h2>
        <p style={{color: 'rgba(255,255,255,0.8)'}}>This may take 10-30 seconds for quality content</p>
      </div>
    );
  }

  if (step === 'result' && result) {
    return (
      <div className="container">
        <div className="card">
          <div style={{textAlign: 'center', marginBottom: '30px'}}>
            <h2 style={{color: '#1f2937', fontSize: '2rem', marginBottom: '10px'}}>
              📚 Your Book is Ready!
            </h2>
            <div className="stats">
              <div className="stat">
                <span className="stat-number" style={{color: '#059669'}}>{result.word_count}</span>
                <div className="stat-label" style={{color: '#6b7280'}}>Words Generated</div>
              </div>
              <div className="stat">
                <span className="stat-number" style={{color: '#dc2626'}}>PDF</span>
                <div className="stat-label" style={{color: '#6b7280'}}>Ready to Download</div>
              </div>
            </div>
          </div>

          <div style={{textAlign: 'center', marginBottom: '30px'}}>
            <button className="btn btn-success" onClick={handleDownloadPDF} style={{marginRight: '15px'}}>
              📄 Download PDF
            </button>
            <button className="btn btn-primary" onClick={() => setStep('home')}>
              📝 Generate Another
            </button>
          </div>

          <div className="result">
            <pre>{result.book}</pre>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="hero">
        <h1>📖 WizBook.io</h1>
        <p className="tagline">Turn ideas into books in 60 seconds</p>
        
        <div className="features">
          <div className="feature">
            <span className="feature-icon">⚡</span>
            <h3>Lightning Fast</h3>
            <p>Professional books generated in under 60 seconds</p>
          </div>
          <div className="feature">
            <span className="feature-icon">🎨</span>
            <h3>AI-Powered</h3>
            <p>Advanced AI creates comprehensive, readable content</p>
          </div>
          <div className="feature">
            <span className="feature-icon">📄</span>
            <h3>PDF Ready</h3>
            <p>Download watermarked PDFs instantly</p>
          </div>
        </div>
      </div>

      <div className="container">
        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}

        <div className="card">
          <h2 style={{textAlign: 'center', marginBottom: '40px', color: '#1f2937', fontSize: '2.2rem'}}>
            Create Your Book
          </h2>

          <div className="input-group">
            <label htmlFor="topic">📚 What's your book about?</label>
            <input
              id="topic"
              type="text"
              value={formData.topic}
              onChange={(e) => setFormData({...formData, topic: e.target.value})}
              placeholder="e.g., Python Programming, Digital Marketing, Coffee Shop Business Plan"
              onKeyPress={(e) => e.key === 'Enter' && handleGenerate()}
            />
          </div>

          <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '25px'}}>
            <div className="input-group">
              <label htmlFor="audience">👥 Target Audience</label>
              <select
                id="audience"
                value={formData.audience}
                onChange={(e) => setFormData({...formData, audience: e.target.value})}
              >
                <option value="beginners">Complete Beginners</option>
                <option value="intermediate">Intermediate Level</option>
                <option value="advanced">Advanced Users</option>
                <option value="professionals">Business Professionals</option>
                <option value="students">Students</option>
              </select>
            </div>

            <div className="input-group">
              <label htmlFor="style">✍️ Writing Style</label>
              <select
                id="style"
                value={formData.style}
                onChange={(e) => setFormData({...formData, style: e.target.value})}
              >
                <option value="professional">Professional</option>
                <option value="casual">Casual & Friendly</option>
                <option value="academic">Academic</option>
                <option value="conversational">Conversational</option>
              </select>
            </div>
          </div>

          <div style={{textAlign: 'center'}}>
            <button 
              className="btn btn-primary" 
              onClick={handleGenerate}
              disabled={loading}
              style={{fontSize: '1.2rem', padding: '20px 50px'}}
            >
              🚀 Generate Book ($9.99)
            </button>
          </div>

          <div style={{textAlign: 'center', marginTop: '30px', fontSize: '0.9rem', color: '#6b7280'}}>
            <p>✨ Professional quality • Instant delivery • Watermarked PDFs</p>
          </div>
        </div>

        <div className="card" style={{textAlign: 'center', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)'}}>
          <h3 style={{color: 'white', marginBottom: '20px'}}>🔥 Popular Topics</h3>
          <div className="btn-grid">
            {[
              'Python Programming for Beginners',
              'Digital Marketing Strategy', 
              'Personal Finance Guide',
              'Content Creation Tips',
              'Small Business Planning',
              'AI and Machine Learning'
            ].map(topic => (
              <button 
                key={topic}
                className="btn btn-primary"
                onClick={() => setFormData({...formData, topic})}
                style={{fontSize: '0.95rem', padding: '12px 20px'}}
              >
                {topic}
              </button>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}

// Main App Component
function App() {
  return (
    <div className="App">
      <WizBookApp />
    </div>
  );
}

export default App;