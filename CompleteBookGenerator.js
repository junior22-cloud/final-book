// Complete BookGenerator with Paywall Integration
import { useState } from 'react';
import { saveAs } from 'file-saver';
import { loadStripe } from '@stripe/stripe-js';

export default function BookGenerator() {
  const [output, setOutput] = useState('');
  const [loading, setLoading] = useState(false);
  const [hasPaid, setHasPaid] = useState(false);

  const generate = async (prompt) => {
    setLoading(true);
    try {
      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });
      const { text } = await res.json();
      setOutput(text);
    } catch (error) {
      setOutput('Error generating content. Please try again.');
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
      
      if (res.ok) {
        const blob = await res.blob();
        saveAs(blob, 'book.pdf');
      }
    } catch (error) {
      console.error('PDF export failed:', error);
    }
  };

  const handlePayment = async () => {
    try {
      const res = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      
      const { id, error } = await res.json();
      
      if (error) {
        console.error('Checkout error:', error);
        // For development, simulate successful payment
        if (id === "cs_test_mock_session_id_for_development") {
          setHasPaid(true);
          alert('🎉 Payment successful (Demo Mode)! You can now generate books.');
        }
        return;
      }
      
      const stripe = await loadStripe(process.env.NEXT_PUBLIC_STRIPE_KEY);
      await stripe.redirectToCheckout({ sessionId: id });
      
    } catch (error) {
      console.error('Payment failed:', error);
    }
  };

  // Check URL for successful payment
  React.useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    if (sessionId) {
      setHasPaid(true);
      // Clean URL
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ textAlign: 'center', color: '#1F2937' }}>🚀 AI Book Generator</h1>
      
      {!hasPaid ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <h2>Get Unlimited AI Book Generation</h2>
          <p style={{ color: '#6B7280', marginBottom: '30px' }}>
            Generate professional books, guides, and content with advanced AI
          </p>
          
          <button 
            onClick={handlePayment}
            style={{
              backgroundColor: '#4F46E5',
              color: 'white',
              padding: '15px 30px',
              border: 'none',
              borderRadius: '8px',
              fontSize: '18px',
              fontWeight: 'bold',
              cursor: 'pointer',
              marginBottom: '20px'
            }}
          >
            Buy Credits ($9.99)
          </button>
          
          <div style={{ marginTop: '30px', fontSize: '14px', color: '#6B7280' }}>
            <p>✅ Unlimited book generation</p>
            <p>✅ Professional PDF downloads</p>
            <p>✅ Multiple book formats</p>
            <p>✅ Instant delivery</p>
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
            ✅ <strong>Payment Successful!</strong> You now have unlimited book generation.
          </div>

          <div style={{ marginBottom: '20px' }}>
            <h3>Generate Your Book:</h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginBottom: '20px' }}>
              <button 
                onClick={() => generate("Write a fantasy novel chapter")}
                disabled={loading}
                style={{ 
                  backgroundColor: '#7C3AED', 
                  color: 'white', 
                  padding: '12px 20px', 
                  border: 'none', 
                  borderRadius: '6px',
                  cursor: 'pointer'
                }}
              >
                {loading ? 'Generating...' : '📚 Fantasy Chapter'}
              </button>
              
              <button 
                onClick={() => generate("Write a beginner's guide to Python programming")}
                disabled={loading}
                style={{ 
                  backgroundColor: '#059669', 
                  color: 'white', 
                  padding: '12px 20px', 
                  border: 'none', 
                  borderRadius: '6px',
                  cursor: 'pointer'
                }}
              >
                {loading ? 'Generating...' : '💻 Programming Guide'}
              </button>
              
              <button 
                onClick={() => generate("Write a complete business plan for a coffee shop")}
                disabled={loading}
                style={{ 
                  backgroundColor: '#DC2626', 
                  color: 'white', 
                  padding: '12px 20px', 
                  border: 'none', 
                  borderRadius: '6px',
                  cursor: 'pointer'
                }}
              >
                {loading ? 'Generating...' : '☕ Business Plan'}
              </button>
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
    </div>
  );
}

// Alternative: Keep your original minimal style
/*
export default function BookGenerator() {
  const [output, setOutput] = useState('');

  const generate = async (prompt) => {
    const res = await fetch('/api/generate', {
      method: 'POST',
      body: JSON.stringify({ prompt })
    });
    const { text } = await res.json();
    setOutput(text);
  };

  const downloadPDF = async () => {
    const res = await fetch('/api/export', {
      method: 'POST',
      body: JSON.stringify({ text: output })
    });
    const blob = await res.blob();
    saveAs(blob, 'book.pdf');
  };

  const handlePayment = async () => {
    const res = await fetch('/api/checkout');
    const { id } = await res.json();
    const stripe = await loadStripe(process.env.NEXT_PUBLIC_STRIPE_KEY);
    await stripe.redirectToCheckout({ sessionId: id });
  };

  return (
    <div>
      <button onClick={handlePayment}>Buy Credits ($9.99)</button>
      <button onClick={() => generate("Write a fantasy novel chapter")}>
        Generate
      </button>
      {output && <button onClick={downloadPDF}>Download PDF</button>}
      <pre>{output}</pre>
    </div>
  );
}
*/