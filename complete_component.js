// Your complete BookGenerator.js with PDF download
import { useState } from 'react';
import { saveAs } from 'file-saver';

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

  return (
    <div>
      <button onClick={() => generate("Write a fantasy novel chapter")}>
        Generate
      </button>
      {output && (
        <button onClick={downloadPDF}>Download PDF</button>
      )}
      <pre>{output}</pre>
    </div>
  );
}

// Package.json dependency needed:
// npm install file-saver