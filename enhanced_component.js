// /components/BookGenerator.js - Enhanced version with PDF export
import { useState } from 'react';

export default function BookGenerator() {
  const [output, setOutput] = useState('');
  const [loading, setLoading] = useState(false);

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

  const exportPDF = async () => {
    if (!output) return;
    
    try {
      const res = await fetch('/api/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: output })
      });
      
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'generated_book.pdf';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('PDF export failed:', error);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">AI Book Generator</h1>
      
      <div className="mb-4 space-x-2">
        <button 
          onClick={() => generate("Write a fantasy novel chapter")}
          disabled={loading}
          className="bg-blue-600 text-white px-6 py-3 rounded hover:bg-blue-700 disabled:bg-gray-400"
        >
          {loading ? 'Generating...' : 'Generate Fantasy Chapter'}
        </button>
        
        <button 
          onClick={() => generate("Write a beginner's guide to JavaScript programming")}
          disabled={loading}
          className="bg-green-600 text-white px-6 py-3 rounded hover:bg-green-700 disabled:bg-gray-400"
        >
          {loading ? 'Generating...' : 'Generate Programming Guide'}
        </button>
        
        <button 
          onClick={() => generate("Write a complete business plan for a coffee shop")}
          disabled={loading}
          className="bg-purple-600 text-white px-6 py-3 rounded hover:bg-purple-700 disabled:bg-gray-400"
        >
          {loading ? 'Generating...' : 'Generate Business Plan'}
        </button>
      </div>

      {output && (
        <div className="mb-4">
          <button 
            onClick={exportPDF}
            className="bg-red-600 text-white px-6 py-3 rounded hover:bg-red-700"
          >
            📄 Download PDF
          </button>
        </div>
      )}

      {output && (
        <div className="mt-6 p-6 border rounded-lg bg-white shadow-lg">
          <pre className="whitespace-pre-wrap text-sm font-mono leading-relaxed">
            {output}
          </pre>
        </div>
      )}
      
      {!output && !loading && (
        <div className="text-center text-gray-500 mt-8">
          <p>Click any button above to generate professional content instantly!</p>
        </div>
      )}
    </div>
  );
}


// Alternative: Keep your exact original component style
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

  const exportPDF = async () => {
    const res = await fetch('/api/export', {
      method: 'POST',
      body: JSON.stringify({ text: output })
    });
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'book.pdf';
    a.click();
  };

  return (
    <div>
      <button onClick={() => generate("Write a fantasy novel chapter")}>
        Generate
      </button>
      {output && (
        <button onClick={exportPDF}>Export PDF</button>
      )}
      <pre>{output}</pre>
    </div>
  );
}
*/