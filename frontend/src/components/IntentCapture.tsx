'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api';
import { AnalysisResponse } from '@/types/api';

interface IntentCaptureProps {
  onResults?: (results: AnalysisResponse, userInput?: string) => void;
}

export default function IntentCapture({ onResults }: IntentCaptureProps) {
  const [input, setInput] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!input.trim()) return;
    
    setIsAnalyzing(true);
    setError(null);

    try {
      const results = await apiClient.analyzeComplete(input);
      if (onResults) {
        onResults(results, input);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed. Please try again.');
      console.error('Analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const examples = [
    "I need to deploy a REST API with PostgreSQL that handles 1000 requests per second",
    "Build a microservices architecture for an e-commerce platform with 50K daily users",
    "Deploy a machine learning model serving endpoint with GPU support",
  ];

  return (
    <section className="py-16 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Describe Your Application
          </h2>
          <p className="text-gray-600 mb-6">
            Tell us what you're building in plain English. Our AI will analyze and recommend the optimal GCP architecture.
          </p>

          <div className="space-y-4">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Example: I'm building a real-time chat application with websockets, expecting 10,000 concurrent users, needs Redis for caching, and PostgreSQL for message history..."
              className="w-full h-40 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-gray-900 placeholder-gray-400"
              disabled={isAnalyzing}
            />

            <button
              onClick={handleAnalyze}
              disabled={!input.trim() || isAnalyzing}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
            >
              {isAnalyzing ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Analyzing...
                </span>
              ) : (
                'Analyze & Recommend'
              )}
            </button>

            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-800 text-sm">
                  <span className="font-semibold">Error:</span> {error}
                </p>
              </div>
            )}
          </div>

          <div className="mt-8">
            <p className="text-sm font-semibold text-gray-700 mb-3">Try these examples:</p>
            <div className="space-y-2">
              {examples.map((example, idx) => (
                <button
                  key={idx}
                  onClick={() => setInput(example)}
                  className="block w-full text-left text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 px-4 py-2 rounded-lg transition-colors duration-150"
                >
                  💡 {example}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
