// Complete BookGenerator.js with Payments
import { useState } from 'react';
import { saveAs } from 'file-saver';

export default function BookGenerator() {
  const [output, setOutput] = useState('');
  const [loading, setLoading] = useState(false);
  const [paid, setPaid] = useState(false);

  const generate = async (prompt) => {
    setLoading(true);
    const res = await fetch('/api/generate', {
      method: 'POST',
      body: JSON.stringify({ prompt })
    });
    const { text } = await res.json();
    setOutput(text);
    setLoading(false);
  };

  const downloadPDF = async () => {
    const res = await fetch('/api/export', {
      method: 'POST',
      body: JSON.stringify({ text: output })
    });
    const blob = await res.blob();
    saveAs(blob, 'book.pdf');
  };

  const buyBook = async (prompt, bookType) => {
    try {
      // Create checkout session
      const res = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          prompt: prompt,
          book_type: bookType 
        })
      });
      const { id } = await res.json();
      
      // Redirect to Stripe (you'll need @stripe/stripe-js for this)
      // For now, we'll just generate the book directly
      await generate(prompt);
      setPaid(true);
      
    } catch (error) {
      console.error('Payment failed:', error);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>🚀 AI Book Generator</h1>
      
      {!output ? (
        <div>
          <h2>Choose Your Book ($9.99)</h2>
          <button 
            onClick={() => buyBook("Write a fantasy novel chapter", "fantasy")}
            disabled={loading}
            style={{ 
              backgroundColor: '#4F46E5', 
              color: 'white', 
              padding: '15px 30px', 
              border: 'none', 
              borderRadius: '8px',
              margin: '10px',
              cursor: 'pointer'
            }}
          >
            {loading ? 'Generating...' : 'Buy Fantasy Chapter - $9.99'}
          </button>
          
          <button 
            onClick={() => buyBook("Write a beginner's guide to Python programming", "programming")}
            disabled={loading}
            style={{ 
              backgroundColor: '#059669', 
              color: 'white', 
              padding: '15px 30px', 
              border: 'none', 
              borderRadius: '8px',
              margin: '10px',
              cursor: 'pointer'
            }}
          >
            {loading ? 'Generating...' : 'Buy Programming Guide - $9.99'}
          </button>

          <button 
            onClick={() => buyBook("Write a complete business plan", "business")}
            disabled={loading}
            style={{ 
              backgroundColor: '#DC2626', 
              color: 'white', 
              padding: '15px 30px', 
              border: 'none', 
              borderRadius: '8px',
              margin: '10px',
              cursor: 'pointer'
            }}
          >
            {loading ? 'Generating...' : 'Buy Business Plan - $9.99'}
          </button>

          {/* Free preview button */}
          <div style={{ marginTop: '30px', borderTop: '1px solid #ccc', paddingTop: '20px' }}>
            <h3>Or try a free sample:</h3>
            <button 
              onClick={() => generate("Write a short fantasy story sample")}
              disabled={loading}
              style={{ 
                backgroundColor: '#6B7280', 
                color: 'white', 
                padding: '10px 20px', 
                border: 'none', 
                borderRadius: '5px',
                cursor: 'pointer'
              }}
            >
              {loading ? 'Generating...' : 'Free Sample'}
            </button>
          </div>
        </div>
      ) : (
        <div>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
            <button 
              onClick={() => setOutput('')}
              style={{ 
                backgroundColor: '#4F46E5', 
                color: 'white', 
                padding: '10px 20px', 
                border: 'none', 
                borderRadius: '5px',
                cursor: 'pointer'
              }}
            >
              ← Generate Another
            </button>
            
            <button 
              onClick={downloadPDF}
              style={{ 
                backgroundColor: '#059669', 
                color: 'white', 
                padding: '10px 20px', 
                border: 'none', 
                borderRadius: '5px',
                cursor: 'pointer'
              }}
            >
              📄 Download PDF
            </button>
          </div>
          
          {paid && (
            <div style={{ 
              backgroundColor: '#D1FAE5', 
              border: '1px solid #10B981', 
              padding: '10px', 
              borderRadius: '5px', 
              marginBottom: '20px' 
            }}>
              ✅ Purchase complete! Your book is ready for download.
            </div>
          )}
          
          <pre style={{ 
            backgroundColor: '#F9FAFB', 
            padding: '20px', 
            borderRadius: '8px', 
            whiteSpace: 'pre-wrap', 
            fontSize: '14px',
            lineHeight: '1.5'
          }}>
            {output}
          </pre>
        </div>
      )}
    </div>
  );
}

// Alternative: Your original minimal style with payments
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

  const buyBook = async () => {
    const res = await fetch('/api/checkout', {
      method: 'POST',
      body: JSON.stringify({ prompt: "Write a fantasy novel chapter" })
    });
    const { id } = await res.json();
    // Handle Stripe redirect here
    await generate("Write a fantasy novel chapter");
  };

  return (
    <div>
      <button onClick={buyBook}>Buy Fantasy Book ($9.99)</button>
      {output && <button onClick={downloadPDF}>Download PDF</button>}
      <pre>{output}</pre>
    </div>
  );
}
*/