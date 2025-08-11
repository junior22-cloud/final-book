import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Book Generator Component
const BookGenerator = () => {
  const [formData, setFormData] = useState({
    topic: 'Python Programming',
    audience: 'complete beginners',
    style: 'casual',
    length: 'medium',
    tier: 'pro',
    email: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [generatedBook, setGeneratedBook] = useState(null);
  const [pricingTiers, setPricingTiers] = useState([]);
  const [error, setError] = useState('');

  // Fetch pricing tiers on component mount
  useEffect(() => {
    fetchPricingTiers();
  }, []);

  const fetchPricingTiers = async () => {
    try {
      const response = await axios.get(`${API}/pricing`);
      setPricingTiers(response.data.tiers);
    } catch (error) {
      console.error('Failed to fetch pricing:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const generateBook = async () => {
    if (!formData.topic.trim()) {
      setError('Please enter a book topic');
      return;
    }

    setLoading(true);
    setError('');
    setGeneratedBook(null);

    try {
      const response = await axios.post(`${API}/generate-book`, formData);
      setGeneratedBook(response.data);
    } catch (error) {
      console.error('Book generation failed:', error);
      setError('Failed to generate book. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const selectedTier = pricingTiers.find(tier => tier.id === formData.tier) || pricingTiers[1];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            🚀 AI Book Generator
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Generate professional books in minutes using advanced AI. 
            Perfect for entrepreneurs, educators, and content creators.
          </p>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
            <div className="p-8">
              {/* Book Generation Form */}
              <div className="grid md:grid-cols-2 gap-8">
                {/* Left Column - Form */}
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">
                    Create Your Book
                  </h2>
                  
                  {/* Topic Input */}
                  <div className="mb-6">
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      📚 Book Topic *
                    </label>
                    <input
                      type="text"
                      name="topic"
                      value={formData.topic}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="e.g., Python Programming, Digital Marketing, Personal Finance"
                    />
                  </div>

                  {/* Audience Input */}
                  <div className="mb-6">
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      👥 Target Audience *
                    </label>
                    <input
                      type="text"
                      name="audience"
                      value={formData.audience}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="e.g., complete beginners, business professionals, students"
                    />
                  </div>

                  {/* Writing Style */}
                  <div className="mb-6">
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      ✍️ Writing Style
                    </label>
                    <select
                      name="style"
                      value={formData.style}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="casual">Casual & Friendly</option>
                      <option value="professional">Professional</option>
                      <option value="academic">Academic</option>
                      <option value="storytelling">Storytelling</option>
                    </select>
                  </div>

                  {/* Email Input */}
                  <div className="mb-6">
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      📧 Email (for delivery)
                    </label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="your@email.com"
                    />
                  </div>

                  {error && (
                    <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                      <p className="text-red-600 text-sm">{error}</p>
                    </div>
                  )}

                  {/* Generate Button */}
                  <button
                    onClick={generateBook}
                    disabled={loading}
                    className={`w-full py-4 px-6 rounded-lg font-semibold text-lg transition-all duration-200 ${
                      loading 
                        ? 'bg-gray-400 cursor-not-allowed' 
                        : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg hover:shadow-xl transform hover:-translate-y-1'
                    }`}
                  >
                    {loading ? (
                      <div className="flex items-center justify-center">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                        Generating Your Book...
                      </div>
                    ) : (
                      `🎯 Generate Book - $${selectedTier?.price || '9.99'}`
                    )}
                  </button>
                </div>

                {/* Right Column - Pricing */}
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">
                    Choose Your Plan
                  </h2>
                  
                  <div className="space-y-4">
                    {pricingTiers.map((tier) => (
                      <div
                        key={tier.id}
                        onClick={() => setFormData(prev => ({ ...prev, tier: tier.id }))}
                        className={`cursor-pointer p-6 rounded-xl border-2 transition-all duration-200 ${
                          formData.tier === tier.id
                            ? 'border-blue-500 bg-blue-50 shadow-lg'
                            : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
                        } ${tier.recommended ? 'ring-2 ring-blue-400 ring-opacity-50' : ''}`}
                      >
                        <div className="flex justify-between items-start mb-3">
                          <div>
                            <h3 className="text-lg font-bold text-gray-900">
                              {tier.name}
                              {tier.recommended && (
                                <span className="ml-2 inline-block px-2 py-1 text-xs font-semibold text-blue-600 bg-blue-100 rounded-full">
                                  RECOMMENDED
                                </span>
                              )}
                            </h3>
                            <p className="text-gray-600 text-sm">{tier.description}</p>
                          </div>
                          <div className="text-right">
                            <div className="text-2xl font-bold text-blue-600">
                              ${tier.price}
                            </div>
                          </div>
                        </div>
                        <ul className="space-y-1">
                          {tier.features.map((feature, index) => (
                            <li key={index} className="text-sm text-gray-600 flex items-center">
                              <span className="text-green-500 mr-2">✓</span>
                              {feature}
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Generated Book Preview */}
          {generatedBook && (
            <div className="mt-8 bg-white rounded-2xl shadow-xl overflow-hidden">
              <div className="bg-gradient-to-r from-green-500 to-emerald-500 px-8 py-6">
                <h2 className="text-2xl font-bold text-white mb-2">
                  🎉 Your Book is Ready!
                </h2>
                <div className="flex items-center text-green-100 text-sm">
                  <span className="mr-4">📄 {generatedBook.word_count.toLocaleString()} words</span>
                  <span className="mr-4">⏱️ Generated in seconds</span>
                  <span>💡 {generatedBook.tier} tier</span>
                </div>
              </div>
              
              <div className="p-8">
                <div className="mb-6 flex justify-between items-center">
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">
                      {generatedBook.topic}
                    </h3>
                    <p className="text-gray-600">For {generatedBook.audience}</p>
                  </div>
                  <div className="flex gap-3">
                    <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                      📧 Email Book
                    </button>
                    <button className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                      📄 Download PDF
                    </button>
                  </div>
                </div>

                {/* Book Content Preview */}
                <div className="bg-gray-50 rounded-xl p-6 max-h-96 overflow-y-auto">
                  <div className="prose max-w-none">
                    <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono leading-relaxed">
                      {generatedBook.content.substring(0, 2000)}
                      {generatedBook.content.length > 2000 && '\n\n... (content continues) ...'}
                    </pre>
                  </div>
                </div>

                <div className="mt-4 text-center">
                  <p className="text-sm text-gray-500">
                    Complete book delivered to your email • Full commercial rights included
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-16 text-center">
          <div className="max-w-3xl mx-auto">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              ⚡ How It Works
            </h3>
            <div className="grid md:grid-cols-3 gap-6 text-center">
              <div className="bg-white p-6 rounded-xl shadow-md">
                <div className="text-4xl mb-3">📝</div>
                <h4 className="font-bold text-gray-900 mb-2">1. Fill Details</h4>
                <p className="text-sm text-gray-600">
                  Enter your topic, audience, and preferences
                </p>
              </div>
              <div className="bg-white p-6 rounded-xl shadow-md">
                <div className="text-4xl mb-3">🤖</div>
                <h4 className="font-bold text-gray-900 mb-2">2. AI Generates</h4>
                <p className="text-sm text-gray-600">
                  Advanced AI creates your custom book in seconds
                </p>
              </div>
              <div className="bg-white p-6 rounded-xl shadow-md">
                <div className="text-4xl mb-3">📚</div>
                <h4 className="font-bold text-gray-900 mb-2">3. Get Your Book</h4>
                <p className="text-sm text-gray-600">
                  Download PDF and start sharing your knowledge
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <div className="App">
      <BookGenerator />
    </div>
  );
}

export default App;