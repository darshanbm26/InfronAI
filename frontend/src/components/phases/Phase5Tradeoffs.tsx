'use client';

import { memo, useMemo } from 'react';
import { Phase5Result } from '@/types/api';
import PhaseCard from './PhaseCard';

interface Phase5TradeoffsProps {
  data: Phase5Result;
  isModified?: boolean;
  architecture?: string;
}

const Phase5Tradeoffs = memo(function Phase5Tradeoffs({ 
  data, 
  isModified,
  architecture 
}: Phase5TradeoffsProps) {
  const analysis = data.tradeoff_analysis || {};
  const scores = data.tradeoff_scores || [];
  const factors = data.decision_factors || {};
  const processing = data.processing_metadata || {};

  // Memoize strength colors lookup
  const strengthColors = useMemo(() => ({
    strong: { bg: 'bg-green-100', text: 'text-green-800', border: 'border-green-300' },
    moderate: { bg: 'bg-amber-100', text: 'text-amber-800', border: 'border-amber-300' },
    weak: { bg: 'bg-red-100', text: 'text-red-800', border: 'border-red-300' },
  }), []);

  const strength = useMemo(() => 
    strengthColors[(analysis.recommendation_strength || 'moderate') as keyof typeof strengthColors] 
    || strengthColors.moderate,
    [strengthColors, analysis.recommendation_strength]
  );

  const severityColors = useMemo(() => ({
    low: 'bg-green-100 text-green-700',
    medium: 'bg-amber-100 text-amber-700',
    high: 'bg-red-100 text-red-700',
  }), []);

  // Guard: Don't render if no trade-off data
  if (!analysis || (Object.keys(analysis).length === 0 && scores.length === 0)) {
    return null;
  }

  return (
    <PhaseCard
      phaseNumber={5}
      title="Trade-off Analysis"
      subtitle="Weighing pros, cons, and risks"
      icon="⚖️"
      status={isModified ? 'modified' : 'completed'}
      processingTime={processing.processing_time_ms}
    >
      <div className="space-y-6">
        {/* Recommendation Strength Banner */}
        <div className={`rounded-xl p-6 border-2 ${strength.bg} ${strength.border}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <span className="text-4xl">
                {analysis.recommendation_strength === 'strong' ? '💪' : 
                 analysis.recommendation_strength === 'moderate' ? '🤔' : '⚠️'}
              </span>
              <div>
                <p className={`text-sm font-medium ${strength.text} uppercase tracking-wide`}>
                  Recommendation Strength
                </p>
                <h3 className={`text-2xl font-bold ${strength.text} capitalize`}>
                  {analysis.recommendation_strength || 'Moderate'} Recommendation
                </h3>
              </div>
            </div>
            <div className="text-right">
              <p className={`text-sm ${strength.text}`}>Overall Score</p>
              <p className={`text-3xl font-bold ${strength.text}`}>
                {analysis.overall_score != null && !isNaN(analysis.overall_score) 
                  ? `${(analysis.overall_score * 10).toFixed(1)}/10`
                  : <span className="text-lg">{analysis.recommendation_strength === 'strong' ? 'Strong' : analysis.recommendation_strength === 'moderate' ? 'Good' : 'Fair'}</span>}
              </p>
            </div>
          </div>
          {isModified && (
            <p className={`mt-4 text-sm ${strength.text} bg-white/50 rounded-lg p-3`}>
              ⚠️ Trade-offs have been recalculated based on your customizations
            </p>
          )}
        </div>

        {/* Trade-offs Tied to Intent */}
        <div className="bg-indigo-50 rounded-lg p-5 border border-indigo-200">
          <h4 className="font-semibold text-indigo-900 mb-3 flex items-center gap-2">
            <span>🎯</span> How This Aligns With Your Requirements
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            {factors.primary_factors?.slice(0, 4).map((factor, idx) => (
              <div key={idx} className="flex items-start gap-2 text-indigo-800">
                <span className="text-indigo-500 mt-0.5">✓</span>
                <span>Optimized for: <span className="font-medium">{factor}</span></span>
              </div>
            ))}
          </div>
          <p className="text-xs text-indigo-600 mt-3 italic">
            These trade-offs are directly tied to the requirements you specified in Phase 1.
          </p>
        </div>

        {/* Pros and Cons Side by Side */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Pros */}
          <div className="bg-green-50 rounded-xl p-5 border border-green-200">
            <h4 className="font-semibold text-green-900 mb-4 flex items-center gap-2">
              <span className="text-xl">✅</span> What You Gain ({analysis.pros?.length || 0})
            </h4>
            <div className="space-y-3">
              {analysis.pros && analysis.pros.length > 0 ? (
                analysis.pros.map((pro, idx) => (
                  <div key={idx} className="bg-white rounded-lg p-3 border border-green-100">
                    <p className="font-medium text-green-900">{pro.point}</p>
                    <p className="text-sm text-green-700 mt-1">
                      <span className="font-medium">Impact:</span> {pro.impact}
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-green-700 italic">No specific advantages noted</p>
              )}
            </div>
          </div>

          {/* Cons */}
          <div className="bg-red-50 rounded-xl p-5 border border-red-200">
            <h4 className="font-semibold text-red-900 mb-4 flex items-center gap-2">
              <span className="text-xl">⚠️</span> What You Accept ({analysis.cons?.length || 0})
            </h4>
            <div className="space-y-3">
              {analysis.cons && analysis.cons.length > 0 ? (
                analysis.cons.map((con, idx) => (
                  <div key={idx} className="bg-white rounded-lg p-3 border border-red-100">
                    <p className="font-medium text-red-900">{con.point}</p>
                    <p className="text-sm text-red-700 mt-1">
                      <span className="font-medium">Impact:</span> {con.impact}
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-red-700 italic">No significant trade-offs identified</p>
              )}
            </div>
          </div>
        </div>

        {/* Risk Assessment */}
        {analysis.risks && analysis.risks.length > 0 && (
          <div className="bg-amber-50 rounded-xl p-5 border border-amber-200">
            <h4 className="font-semibold text-amber-900 mb-4 flex items-center gap-2">
              <span className="text-xl">🛡️</span> Risk Assessment
            </h4>
            <div className="space-y-4">
              {analysis.risks.map((risk, idx) => (
                <div key={idx} className="bg-white rounded-lg p-4 border border-amber-100">
                  <div className="flex items-start justify-between mb-2">
                    <p className="font-medium text-amber-900 flex-1">{risk.risk}</p>
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ml-3 ${
                      severityColors[risk.severity as keyof typeof severityColors] || severityColors.medium
                    }`}>
                      {risk.severity?.toUpperCase()}
                    </span>
                  </div>
                  <div className="bg-amber-50 rounded-lg p-3 mt-2">
                    <p className="text-xs font-medium text-amber-700 uppercase tracking-wide mb-1">Mitigation</p>
                    <p className="text-sm text-amber-800">{risk.mitigation}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Trade-off Scores */}
        {scores && scores.length > 0 && (
          <div>
            <h4 className="font-semibold text-gray-900 mb-4">Factor Scores</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {scores.map((score, idx) => {
                const scoreValue = score.score != null && !isNaN(score.score) ? score.score : 0.5;
                const weightValue = score.weight != null && !isNaN(score.weight) ? score.weight : 0.25;
                return (
                <div key={idx} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  <p className="text-sm text-gray-500 mb-1 capitalize">{score.factor}</p>
                  <div className="flex items-end gap-2">
                    <p className="text-2xl font-bold text-gray-900">{(scoreValue * 10).toFixed(1)}</p>
                    <p className="text-sm text-gray-400 mb-1">/10</p>
                  </div>
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden mt-2">
                    <div 
                      className={`h-full rounded-full ${
                        scoreValue >= 0.8 ? 'bg-green-500' :
                        scoreValue >= 0.6 ? 'bg-amber-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${scoreValue * 100}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-400 mt-1">
                    Weight: {(weightValue * 100).toFixed(0)}%
                  </p>
                </div>
              )})}
            </div>
          </div>
        )}

        {/* Decision Factors */}
        {factors && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Primary Factors */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <span>🎯</span> Primary Decision Factors
              </h4>
              <div className="flex flex-wrap gap-2">
                {factors.primary_factors?.map((factor, idx) => (
                  <span 
                    key={idx}
                    className="px-3 py-1.5 bg-indigo-100 text-indigo-700 rounded-full text-sm font-medium"
                  >
                    {factor}
                  </span>
                ))}
              </div>
            </div>

            {/* Secondary Factors */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <span>📋</span> Secondary Considerations
              </h4>
              <div className="flex flex-wrap gap-2">
                {factors.secondary_factors?.map((factor, idx) => (
                  <span 
                    key={idx}
                    className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-full text-sm"
                  >
                    {factor}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Analysis Method */}
        <div className="flex items-center gap-3 text-sm text-gray-500 bg-gray-50 rounded-lg p-3">
          <span className="text-lg">🔬</span>
          <p>
            <span className="font-medium">Analysis Method:</span> {analysis.analysis_method || 'Multi-factor weighted analysis'}
            {architecture && <span className="ml-2 text-gray-400">• Architecture: {architecture}</span>}
          </p>
        </div>
      </div>
    </PhaseCard>
  );
});

export default Phase5Tradeoffs;
