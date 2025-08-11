// Enhanced BookGenerator with Rate Limit Handling
import React, { useState, useEffect } from 'react';
import { saveAs } from 'file-saver';
import { loadStripe } from '@stripe/stripe-js';

export default function BookGenerator() {
  const [output, setOutput] = useState('');
  const [loading, setLoading] = useState(false);
  const [hasPaid, setHasPaid] = useState(false);
  const [error, setError] = useState('');
  const [rateLimited, setRateLimited] = useState(false);

  const generate = async (prompt) => {
    if (rateLimited) {
      setError('Rate limit active. Please wait before generating again.');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });
      
      if (res.status === 429) {
        setError('⏰ Rate limit exceeded. Please wait a minute before generating again.');
        setRateLimited(true);
        
        // Auto-reset rate limit warning after 60 seconds
        setTimeout(() => {
          setRateLimited(false);
          setError('');
        }, 60000);
        
        setLoading(false);
        return;
      }
      
      const data = await res.json();
      if (data.text) {
        setOutput(data.text);
      } else {
        setError('Failed to generate content. Please try again.');
      }
      
    } catch (error) {
      console.error('Generation failed:', error);
      setError('Network error. Please check your connection.');
    }
    
    setLoading(false);
  };

  const downloadPDF = async () => {
    if (!output) return;
    
    try {
      const res = await fetch('/api/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: output })
      });
      
      if (res.status === 429) {
        setError('⏰ PDF export rate limit exceeded. Please wait a minute.');
        return;
      }
      
      if (res.ok) {
        const blob = await res.blob();
        saveAs(blob, 'ai-generated-book.pdf');
        setError(''); // Clear any previous errors
      } else {
        setError('PDF generation failed. Please try again.');
      }
    } catch (error) {
      console.error('PDF export failed:', error);
      setError('PDF export failed. Please try again.');
    }
  };

  const handlePayment = async () => {
    try {
      const res = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      
      if (res.status === 429) {
        setError('⏰ Payment rate limit exceeded. Please wait a minute before trying again.');
        return;
      }
      
      const { id, error } = await res.json();
      
      if (error) {
        console.error('Checkout error:', error);
        // For development, simulate successful payment
        if (id === "cs_test_mock_session_id_for_development") {
          setHasPaid(true);
          setError('');
          alert('🎉 Payment successful (Demo Mode)! You can now generate books.');
        }
        return;
      }
      
      const stripe = await loadStripe(process.env.NEXT_PUBLIC_STRIPE_KEY);
      await stripe.redirectToCheckout({ sessionId: id });
      
    } catch (error) {
      console.error('Payment failed:', error);
      setError('Payment failed. Please try again.');
    }
  };

  // Check URL for successful payment
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    if (sessionId) {
      setHasPaid(true);
      setError('');
      // Clean URL
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ textAlign: 'center', color: '#1F2937' }}>🚀 AI Book Generator</h1>
      <p style={{ textAlign: 'center', color: '#6B7280', marginBottom: '30px' }}>
        Rate-limited and secure AI book generation
      </p>
      
      {/* Error Display */}
      {error && (
        <div style={{ 
          backgroundColor: '#FEE2E2', 
          border: '1px solid #F87171', 
          padding: '15px', 
          borderRadius: '8px', 
          marginBottom: '20px',
          color: '#B91C1C'
        }}>
          {error}
        </div>
      )}
      
      {!hasPaid ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <h2>Get Unlimited AI Book Generation</h2>
          <p style={{ color: '#6B7280', marginBottom: '30px' }}>
            Professional AI books with built-in rate limiting for quality control
          </p>
          
          <button 
            onClick={handlePayment}
            disabled={rateLimited}
            style={{
              backgroundColor: rateLimited ? '#9CA3AF' : '#4F46E5',
              color: 'white',
              padding: '15px 30px',
              border: 'none',
              borderRadius: '8px',
              fontSize: '18px',
              fontWeight: 'bold',
              cursor: rateLimited ? 'not-allowed' : 'pointer',
              marginBottom: '20px'
            }}
          >
            Buy Credits ($9.99)
          </button>
          
          <div style={{ marginTop: '30px', fontSize: '14px', color: '#6B7280' }}>
            <p>✅ 10 AI generations per minute</p>
            <p>✅ 20 PDF downloads per minute</p>
            <p>✅ Rate-limited for quality control</p>
            <p>✅ Professional-grade security</p>
          </div>
        </div>
      ) : (
        <div>
          <div style={{ 
            backgroundColor: '#D1FAE5', 
            border: '1px solid #10B981', 
            padding: '15px', 
            borderRadius: '8px', 
            marginBottom: '20px',
            textAlign: 'center'
          }}>
            ✅ <strong>Payment Successful!</strong> You have unlimited book generation (rate-limited for quality).
          </div>

          <div style={{ marginBottom: '20px' }}>
            <h3>Generate Your Book:</h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginBottom: '20px' }}>
              <button 
                onClick={() => generate("Write a fantasy novel chapter")}
                disabled={loading || rateLimited}
                style={{ 
                  backgroundColor: rateLimited ? '#9CA3AF' : '#7C3AED', 
                  color: 'white', 
                  padding: '12px 20px', 
                  border: 'none', 
                  borderRadius: '6px',
                  cursor: (loading || rateLimited) ? 'not-allowed' : 'pointer'
                }}
              >
                {loading ? 'Generating...' : '📚 Fantasy Chapter'}
              </button>
              
              <button 
                onClick={() => generate("Write a beginner's guide to Python programming")}
                disabled={loading || rateLimited}
                style={{ 
                  backgroundColor: rateLimited ? '#9CA3AF' : '#059669', 
                  color: 'white', 
                  padding: '12px 20px', 
                  border: 'none', 
                  borderRadius: '6px',
                  cursor: (loading || rateLimited) ? 'not-allowed' : 'pointer'
                }}
              >
                {loading ? 'Generating...' : '💻 Programming Guide'}
              </button>
              
              <button 
                onClick={() => generate("Write a complete business plan for a coffee shop")}
                disabled={loading || rateLimited}
                style={{ 
                  backgroundColor: rateLimited ? '#9CA3AF' : '#DC2626', 
                  color: 'white', 
                  padding: '12px 20px', 
                  border: 'none', 
                  borderRadius: '6px',
                  cursor: (loading || rateLimited) ? 'not-allowed' : 'pointer'
                }}
              >
                {loading ? 'Generating...' : '☕ Business Plan'}
              </button>
            </div>
            
            <div style={{ fontSize: '12px', color: '#6B7280', fontStyle: 'italic' }}>
              Rate limit: 10 generations per minute for optimal quality
            </div>
          </div>

          {output && (
            <div>
              <div style={{ marginBottom: '20px' }}>
                <button 
                  onClick={downloadPDF}
                  style={{ 
                    backgroundColor: '#059669', 
                    color: 'white', 
                    padding: '12px 24px', 
                    border: 'none', 
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '16px'
                  }}
                >
                  📄 Download PDF
                </button>
              </div>
              
              <div style={{ 
                backgroundColor: '#F9FAFB', 
                padding: '20px', 
                borderRadius: '8px', 
                border: '1px solid #E5E7EB',
                maxHeight: '400px',
                overflowY: 'auto'
              }}>
                <pre style={{ 
                  whiteSpace: 'pre-wrap', 
                  fontSize: '14px',
                  lineHeight: '1.6',
                  margin: 0,
                  fontFamily: 'ui-monospace, Monaco, "Cascadia Code", monospace'
                }}>
                  {output}
                </pre>
              </div>
            </div>
          )}
        </div>
      )}
      
      <div style={{ 
        marginTop: '40px', 
        padding: '20px', 
        backgroundColor: '#F3F4F6', 
        borderRadius: '8px',
        fontSize: '12px',
        color: '#6B7280'
      }}>
        <strong>Rate Limiting Info:</strong><br/>
        • Content Generation: 10 requests/minute<br/>
        • PDF Downloads: 20 requests/minute<br/>  
        • Payment Processing: 5 requests/minute<br/>
        • Protected against abuse and ensures quality service
      </div>
    </div>
  );
}