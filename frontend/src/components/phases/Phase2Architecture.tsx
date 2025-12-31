'use client';

import { memo, useState, useMemo } from 'react';
import { Phase2Result } from '@/types/api';
import PhaseCard from './PhaseCard';

interface Phase2ArchitectureProps {
  data: Phase2Result;
}

const Phase2Architecture = memo(function Phase2Architecture({ data }: Phase2ArchitectureProps) {
  const [showAlternatives, setShowAlternatives] = useState(false);
  const analysis = data?.architecture_analysis || {};
  const processing = data?.processing_metadata || {};

  // Memoize static lookups
  const archIcons = useMemo<Record<string, string>>(() => ({
    serverless: '⚡',
    containers: '📦',
    virtual_machines: '🖥️',
    kubernetes: '☸️',
    hybrid: '🔀',
  }), []);

  const archDescriptions = useMemo<Record<string, string>>(() => ({
    serverless: 'Fully managed, pay-per-execution compute with automatic scaling',
    containers: 'Containerized workloads with orchestrated deployment',
    virtual_machines: 'Traditional VMs with full control over infrastructure',
    kubernetes: 'Container orchestration for complex microservices',
    hybrid: 'Combination of multiple compute paradigms',
  }), []);

  // Guard: Don't render if no data
  if (!data || !analysis) {
    return null;
  }

  return (
    <PhaseCard
      phaseNumber={2}
      title="Architecture Selection"
      subtitle="AI-driven architecture decision"
      icon="🏗️"
      status="completed"
      confidence={analysis.confidence || 0}
      processingTime={processing.processing_time_ms || 0}
    >
      <div className="space-y-6">
        {/* Primary Recommendation - Highlighted */}
        <div className="bg-gradient-to-br from-indigo-600 via-purple-600 to-blue-700 rounded-xl p-6 text-white relative overflow-hidden">
          {/* Background Pattern */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute inset-0" style={{
              backgroundImage: 'radial-gradient(circle at 25% 25%, white 1px, transparent 1px)',
              backgroundSize: '20px 20px'
            }} />
          </div>
          
          <div className="relative z-10">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-4">
                <span className="text-5xl">{archIcons[analysis.primary_architecture || ''] || '🔧'}</span>
                <div>
                  <p className="text-indigo-200 text-sm font-medium uppercase tracking-wide">Recommended Architecture</p>
                  <h3 className="text-3xl font-bold capitalize">
                    {analysis.primary_architecture?.replace(/_/g, ' ')}
                  </h3>
                </div>
              </div>
              <div className="text-right">
                <p className="text-indigo-200 text-sm">Confidence</p>
                <p className="text-3xl font-bold">{((analysis.confidence || 0) * 100).toFixed(0)}%</p>
              </div>
            </div>
            
            <p className="text-indigo-100 text-lg mb-4">
              {archDescriptions[analysis.primary_architecture || ''] || 'Optimized architecture for your workload'}
            </p>

            {/* Selection Method Badge */}
            <div className="inline-flex items-center gap-2 bg-white/20 rounded-full px-3 py-1">
              <span className="text-xs">Selection Method:</span>
              <span className="text-xs font-semibold uppercase">{analysis.selection_method}</span>
            </div>
          </div>
        </div>

        {/* Why This Architecture */}
        <div className="bg-blue-50 rounded-lg p-5 border border-blue-200">
          <h4 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
            <span>💡</span> Why This Architecture?
          </h4>
          <p className="text-blue-800 leading-relaxed mb-3">
            {analysis.reasoning || 'Architecture selected based on workload requirements, scale needs, and operational constraints.'}
          </p>
          {/* Explicit Comparison Sentence */}
          {analysis.alternatives && analysis.alternatives.length > 0 && (
            <div className="bg-white/60 rounded-lg p-3 border border-blue-100">
              <p className="text-blue-900 text-sm font-medium">
                📊 Compared to {analysis.alternatives[0]?.architecture?.replace(/_/g, ' ')}, 
                <span className="capitalize"> {analysis.primary_architecture?.replace(/_/g, ' ')}</span> was selected because it 
                {(analysis.confidence || 0) >= 0.8 
                  ? ' reduces operational complexity and provides better cost efficiency for your scale requirements.'
                  : (analysis.confidence || 0) >= 0.6 
                    ? ' offers a better balance of flexibility and manageability for your workload type.'
                    : ' is more suitable given the constraints and requirements specified.'}
              </p>
            </div>
          )}
        </div>

        {/* Confidence Breakdown */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <h4 className="font-semibold text-gray-900">Decision Confidence</h4>
            <span className={`text-sm font-medium ${
              (analysis.confidence || 0) >= 0.8 ? 'text-green-600' :
              (analysis.confidence || 0) >= 0.6 ? 'text-amber-600' : 'text-red-600'
            }`}>
              {(analysis.confidence || 0) >= 0.8 ? 'High Confidence' :
               (analysis.confidence || 0) >= 0.6 ? 'Medium Confidence' : 'Low Confidence'}
            </span>
          </div>
          <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className={`h-full rounded-full transition-all ${
                (analysis.confidence || 0) >= 0.8 ? 'bg-gradient-to-r from-green-400 to-green-600' :
                (analysis.confidence || 0) >= 0.6 ? 'bg-gradient-to-r from-amber-400 to-amber-600' : 
                'bg-gradient-to-r from-red-400 to-red-600'
              }`}
              style={{ width: `${(analysis.confidence || 0) * 100}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Based on pattern matching, workload analysis, and cost optimization
          </p>
        </div>

        {/* Alternatives Section */}
        {analysis.alternatives && analysis.alternatives.length > 0 && (
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <button
              onClick={() => setShowAlternatives(!showAlternatives)}
              className="w-full px-5 py-4 bg-gray-50 hover:bg-gray-100 transition-colors flex items-center justify-between"
            >
              <div className="flex items-center gap-2">
                <span className="text-gray-600">🔄</span>
                <span className="font-semibold text-gray-900">
                  Alternative Architectures Considered ({analysis.alternatives.length})
                </span>
              </div>
              <span className={`transform transition-transform ${showAlternatives ? 'rotate-180' : ''}`}>
                ▼
              </span>
            </button>
            
            {showAlternatives && (
              <div className="divide-y divide-gray-100">
                {analysis.alternatives.map((alt, idx) => (
                  <div key={idx} className="p-5 hover:bg-gray-50 transition-colors">
                    <div className="flex items-start gap-4">
                      <span className="text-3xl">{archIcons[alt.architecture || ''] || '🔧'}</span>
                      <div className="flex-1">
                        <h5 className="font-semibold text-gray-900 capitalize mb-1">
                          {alt.architecture?.replace(/_/g, ' ')}
                        </h5>
                        <p className="text-gray-600 text-sm mb-3">
                          {archDescriptions[alt.architecture] || 'Alternative compute option'}
                        </p>
                        <div className="bg-amber-50 rounded-lg p-3 border border-amber-200">
                          <p className="text-xs font-medium text-amber-700 uppercase tracking-wide mb-1">
                            When to Consider
                          </p>
                          <p className="text-amber-800 text-sm">{alt.when_to_consider}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* System Decision Notice */}
        <div className="flex items-center gap-3 text-sm text-gray-500 bg-gray-50 rounded-lg p-3">
          <span className="text-lg">🔒</span>
          <p>
            <span className="font-medium">System Decision:</span> Architecture selection is AI-determined based on your requirements. 
            You can override this in Phase 7 if needed.
          </p>
        </div>
      </div>
    </PhaseCard>
  );
});

export default Phase2Architecture;
