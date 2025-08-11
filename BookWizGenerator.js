// Final BookWiz Generator with Professional Watermarked PDFs
import React, { useState, useEffect } from 'react';
import { saveAs } from 'file-saver';
import { loadStripe } from '@stripe/stripe-js';

export default function BookWizGenerator() {
  const [output, setOutput] = useState('');
  const [loading, setLoading] = useState(false);
  const [hasPaid, setHasPaid] = useState(false);
  const [error, setError] = useState('');
  const [rateLimited, setRateLimited] = useState(false);
  const [pdfGenerating, setPdfGenerating] = useState(false);

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
        setError('⏰ Rate limit exceeded (10/min). Please wait a minute before generating again.');
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

  const downloadWatermarkedPDF = async () => {
    if (!output) return;
    
    setPdfGenerating(true);
    
    try {
      const res = await fetch('/api/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: output })
      });
      
      if (res.status === 429) {
        setError('⏰ PDF export rate limit exceeded (20/min). Please wait a minute.');
        setPdfGenerating(false);
        return;
      }
      
      if (res.ok) {
        const blob = await res.blob();
        saveAs(blob, `bookwiz-${Date.now()}.pdf`);
        setError(''); // Clear any previous errors
      } else {
        const errorData = await res.json();
        setError(`PDF generation failed: ${errorData.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('PDF export failed:', error);
      setError('PDF export failed. Please try again.');
    }
    
    setPdfGenerating(false);
  };

  const handlePayment = async () => {
    try {
      const res = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      
      if (res.status === 429) {
        setError('⏰ Payment rate limit exceeded (5/min). Please wait a minute before trying again.');
        return;
      }
      
      const { id, error } = await res.json();
      
      if (error) {
        console.error('Checkout error:', error);
        // For development, simulate successful payment
        if (id === "cs_test_mock_session_id_for_development") {
          setHasPaid(true);
          setError('');
          alert('🎉 Payment successful (Demo Mode)! You can now generate professional books with watermarks.');
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
    <div style={{ padding: '20px', maxWidth: '900px', margin: '0 auto', fontFamily: 'Arial, sans-serif' }}>
      <div style={{ textAlign: 'center', marginBottom: '30px' }}>
        <h1 style={{ color: '#1F2937', fontSize: '36px', margin: '0' }}>
          📚 BookWiz Generator
        </h1>
        <p style={{ color: '#6B7280', fontSize: '16px', marginTop: '10px' }}>
          Professional AI books with watermarked PDFs • Rate-limited for quality
        </p>
      </div>
      
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
          <h2 style={{ color: '#374151', marginBottom: '15px' }}>
            Get Professional AI Book Generation
          </h2>
          <p style={{ color: '#6B7280', marginBottom: '30px', lineHeight: '1.6' }}>
            Generate high-quality books with professional watermarked PDFs<br/>
            "Generated by BookWiz" watermark included for authenticity
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
              marginBottom: '30px'
            }}
          >
            Buy BookWiz Credits ($9.99)
          </button>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '20px',
            marginTop: '30px' 
          }}>
            <div style={{ padding: '15px', backgroundColor: '#F3F4F6', borderRadius: '8px' }}>
              <h4 style={{ margin: '0 0 10px 0', color: '#374151' }}>✨ Watermarked PDFs</h4>
              <p style={{ fontSize: '14px', color: '#6B7280', margin: 0 }}>
                Professional "Generated by BookWiz" watermarks on every page
              </p>
            </div>
            <div style={{ padding: '15px', backgroundColor: '#F3F4F6', borderRadius: '8px' }}>
              <h4 style={{ margin: '0 0 10px 0', color: '#374151' }}>⚡ Rate Protected</h4>
              <p style={{ fontSize: '14px', color: '#6B7280', margin: 0 }}>
                10 generations/min, 20 PDF exports/min for quality control
              </p>
            </div>
            <div style={{ padding: '15px', backgroundColor: '#F3F4F6', borderRadius: '8px' }}>
              <h4 style={{ margin: '0 0 10px 0', color: '#374151' }}>🔒 Secure Payments</h4>
              <p style={{ fontSize: '14px', color: '#6B7280', margin: 0 }}>
                Stripe-powered payments with 5/min rate limiting
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div>
          <div style={{ 
            backgroundColor: '#D1FAE5', 
            border: '1px solid #10B981', 
            padding: '15px', 
            borderRadius: '8px', 
            marginBottom: '25px',
            textAlign: 'center'
          }}>
            ✅ <strong>BookWiz Activated!</strong> Generate professional books with watermarked PDFs.
          </div>

          <div style={{ marginBottom: '25px' }}>
            <h3 style={{ color: '#374151', marginBottom: '15px' }}>Generate Your Professional Book:</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '15px', marginBottom: '20px' }}>
              <button 
                onClick={() => generate("Write an epic fantasy novel chapter with dragons and magic")}
                disabled={loading || rateLimited}
                style={{ 
                  backgroundColor: rateLimited ? '#9CA3AF' : '#7C3AED', 
                  color: 'white', 
                  padding: '15px 20px', 
                  border: 'none', 
                  borderRadius: '6px',
                  cursor: (loading || rateLimited) ? 'not-allowed' : 'pointer',
                  fontSize: '14px'
                }}
              >
                {loading ? '⏳ Generating...' : '🐉 Epic Fantasy Chapter'}
              </button>
              
              <button 
                onClick={() => generate("Write a comprehensive Python programming guide for beginners")}
                disabled={loading || rateLimited}
                style={{ 
                  backgroundColor: rateLimited ? '#9CA3AF' : '#059669', 
                  color: 'white', 
                  padding: '15px 20px', 
                  border: 'none', 
                  borderRadius: '6px',
                  cursor: (loading || rateLimited) ? 'not-allowed' : 'pointer',
                  fontSize: '14px'
                }}
              >
                {loading ? '⏳ Generating...' : '🐍 Python Programming Guide'}
              </button>
              
              <button 
                onClick={() => generate("Write a detailed business plan for opening a successful coffee shop")}
                disabled={loading || rateLimited}
                style={{ 
                  backgroundColor: rateLimited ? '#9CA3AF' : '#DC2626', 
                  color: 'white', 
                  padding: '15px 20px', 
                  border: 'none', 
                  borderRadius: '6px',
                  cursor: (loading || rateLimited) ? 'not-allowed' : 'pointer',
                  fontSize: '14px'
                }}
              >
                {loading ? '⏳ Generating...' : '☕ Coffee Shop Business Plan'}
              </button>
            </div>
            
            <div style={{ fontSize: '12px', color: '#6B7280', fontStyle: 'italic', textAlign: 'center' }}>
              Quality-controlled: 10 AI generations per minute maximum
            </div>
          </div>

          {output && (
            <div>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                marginBottom: '20px',
                padding: '15px',
                backgroundColor: '#F9FAFB',
                borderRadius: '8px',
                border: '1px solid #E5E7EB'
              }}>
                <div>
                  <h4 style={{ margin: '0', color: '#374151' }}>📄 Your Generated Book</h4>
                  <p style={{ margin: '5px 0 0 0', fontSize: '14px', color: '#6B7280' }}>
                    Ready for watermarked PDF export • "Generated by BookWiz" included
                  </p>
                </div>
                <button 
                  onClick={downloadWatermarkedPDF}
                  disabled={pdfGenerating}
                  style={{ 
                    backgroundColor: '#059669', 
                    color: 'white', 
                    padding: '12px 24px', 
                    border: 'none', 
                    borderRadius: '6px',
                    cursor: pdfGenerating ? 'not-allowed' : 'pointer',
                    fontSize: '16px',
                    fontWeight: 'bold'
                  }}
                >
                  {pdfGenerating ? '⏳ Creating PDF...' : '📄 Download Watermarked PDF'}
                </button>
              </div>
              
              <div style={{ 
                backgroundColor: '#FFFFFF', 
                padding: '25px', 
                borderRadius: '8px', 
                border: '1px solid #E5E7EB',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                maxHeight: '500px',
                overflowY: 'auto'
              }}>
                <pre style={{ 
                  whiteSpace: 'pre-wrap', 
                  fontSize: '14px',
                  lineHeight: '1.8',
                  margin: 0,
                  fontFamily: 'Georgia, "Times New Roman", serif',
                  color: '#374151'
                }}>
                  {output}
                </pre>
              </div>
            </div>
          )}
        </div>
      )}
      
      <div style={{ 
        marginTop: '50px', 
        padding: '25px', 
        backgroundColor: '#F8FAFC', 
        borderRadius: '8px',
        border: '1px solid #E2E8F0'
      }}>
        <h4 style={{ margin: '0 0 15px 0', color: '#1E293B', textAlign: 'center' }}>
          🏭 BookWiz Professional Features
        </h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', fontSize: '13px', color: '#475569' }}>
          <div>
            <strong>🔒 Rate Limiting:</strong><br/>
            • Content: 10 requests/min<br/>
            • PDFs: 20 exports/min<br/>  
            • Payments: 5 requests/min
          </div>
          <div>
            <strong>💎 Watermarking:</strong><br/>
            • "Generated by BookWiz"<br/>
            • 45° rotation, 50% opacity<br/>
            • Every page protected
          </div>
          <div>
            <strong>🎯 Quality Control:</strong><br/>
            • Professional formatting<br/>
            • Multi-page support<br/>
            • Abuse prevention built-in
          </div>
        </div>
      </div>
    </div>
  );
}