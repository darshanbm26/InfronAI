'use client';

import { memo, useMemo, useCallback } from 'react';
import { Phase6Result, Phase1Result, Phase2Result, Phase3Result, Phase4Result, Phase5Result } from '@/types/api';
import PhaseCard from './PhaseCard';

interface Phase6PresentationProps {
  data: Phase6Result;
  phase1?: Phase1Result;
  phase2?: Phase2Result;
  phase3?: Phase3Result;
  phase4?: Phase4Result;
  phase5?: Phase5Result;
}

const Phase6Presentation = memo(function Phase6Presentation({ 
  data,
  phase1,
  phase2,
  phase3,
  phase4,
  phase5 
}: Phase6PresentationProps) {
  const presentation = data.presentation || {};
  const recommendation = presentation?.recommendation || {};
  const visual = data.visual_components || {};
  const consolidated = data.consolidated_data || {};
  const processing = data.processing_metadata || {};

  // Memoize currency formatter
  const formatCurrency = useCallback((amount: number) => {
    if (!Number.isFinite(amount)) return '$0';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  }, []);

  // Memoize architecture icons
  const archIcons = useMemo<Record<string, string>>(() => ({
    serverless: '⚡',
    containers: '📦',
    virtual_machines: '🖥️',
    kubernetes: '☸️',
    hybrid: '🔀',
  }), []);

  // Guard: Don't render if no presentation data
  if (!presentation || !consolidated) {
    return null;
  }

  return (
    <PhaseCard
      phaseNumber={6}
      title="Presentation & Review Dashboard"
      subtitle="Complete recommendation overview"
      icon="📊"
      status="completed"
      confidence={recommendation?.confidence_score}
      processingTime={processing.processing_time_ms}
    >
      <div className="space-y-6">
        {/* Executive Summary Banner */}
        <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-xl p-6 text-white relative overflow-hidden">
          <div className="absolute inset-0 opacity-10">
            <div className="absolute inset-0" style={{
              backgroundImage: 'linear-gradient(45deg, white 25%, transparent 25%, transparent 75%, white 75%), linear-gradient(45deg, white 25%, transparent 25%, transparent 75%, white 75%)',
              backgroundSize: '20px 20px',
              backgroundPosition: '0 0, 10px 10px'
            }} />
          </div>
          
          <div className="relative z-10">
            <p className="text-indigo-200 text-sm font-medium uppercase tracking-wide mb-2">
              System Recommendation
            </p>
            <h3 className="text-2xl md:text-3xl font-bold mb-4">
              {recommendation?.headline || 'GCP Infrastructure Recommendation'}
            </h3>
            <p className="text-indigo-100 text-lg leading-relaxed">
              {recommendation?.summary || presentation?.executive_summary || 'Optimized configuration based on your requirements.'}
            </p>
            
            {/* Key Benefits */}
            {recommendation?.key_benefits && recommendation.key_benefits.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-4">
                {recommendation.key_benefits.map((benefit, idx) => (
                  <span 
                    key={idx}
                    className="px-3 py-1 bg-white/20 rounded-full text-sm font-medium"
                  >
                    ✓ {benefit}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Quick Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {/* Architecture */}
          <div className="bg-blue-50 rounded-xl p-4 border border-blue-100">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-2xl">{archIcons[consolidated.architecture || ''] || '🔧'}</span>
              <p className="text-xs font-medium text-blue-600 uppercase tracking-wide">Architecture</p>
            </div>
            <p className="font-bold text-gray-900 capitalize text-lg">
              {consolidated.architecture?.replace(/_/g, ' ')}
            </p>
          </div>

          {/* Machine Type */}
          <div className="bg-purple-50 rounded-xl p-4 border border-purple-100">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-2xl">⚙️</span>
              <p className="text-xs font-medium text-purple-600 uppercase tracking-wide">Compute</p>
            </div>
            <p className="font-bold text-gray-900 font-mono text-lg">
              {consolidated.machine_type}
            </p>
          </div>

          {/* Monthly Cost */}
          <div className="bg-green-50 rounded-xl p-4 border border-green-100">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-2xl">💰</span>
              <p className="text-xs font-medium text-green-600 uppercase tracking-wide">Monthly Cost</p>
            </div>
            <p className="font-bold text-gray-900 text-lg">
              {formatCurrency(consolidated.monthly_cost || 0)}
            </p>
          </div>

          {/* Region */}
          <div className="bg-amber-50 rounded-xl p-4 border border-amber-100">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-2xl">🌍</span>
              <p className="text-xs font-medium text-amber-600 uppercase tracking-wide">Region</p>
            </div>
            <p className="font-bold text-gray-900 font-mono text-lg">
              {consolidated.region}
            </p>
          </div>
        </div>

        {/* Phase Summary Cards */}
        <div className="bg-gray-50 rounded-xl p-5">
          <h4 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <span>📋</span> Decision Summary (Phases 1-5)
          </h4>
          
          <div className="space-y-3">
            {/* Phase 1 Summary */}
            <div className="bg-white rounded-lg p-4 border border-gray-200 flex items-center gap-4">
              <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center font-bold text-blue-600">1</div>
              <div className="flex-1">
                <p className="font-medium text-gray-900">Intent: {phase1?.intent_analysis?.workload_type?.replace(/_/g, ' ')}</p>
                <p className="text-sm text-gray-500">
                  {phase1?.intent_analysis?.scale?.estimated_rps} RPS • {phase1?.intent_analysis?.requirements?.latency} latency
                </p>
              </div>
              <span className="text-sm text-gray-400">{((phase1?.intent_analysis?.parsing_confidence || 0) * 100).toFixed(0)}% confidence</span>
            </div>

            {/* Phase 2 Summary */}
            <div className="bg-white rounded-lg p-4 border border-gray-200 flex items-center gap-4">
              <div className="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center font-bold text-indigo-600">2</div>
              <div className="flex-1">
                <p className="font-medium text-gray-900 capitalize">
                  Architecture: {phase2?.architecture_analysis?.primary_architecture?.replace(/_/g, ' ')}
                </p>
                <p className="text-sm text-gray-500">
                  {phase2?.architecture_analysis?.alternatives?.length || 0} alternatives considered
                </p>
              </div>
              <span className="text-sm text-gray-400">{((phase2?.architecture_analysis?.confidence || 0) * 100).toFixed(0)}% confidence</span>
            </div>

            {/* Phase 3 Summary */}
            <div className="bg-white rounded-lg p-4 border border-gray-200 flex items-center gap-4">
              <div className="w-8 h-8 rounded-lg bg-purple-100 flex items-center justify-center font-bold text-purple-600">3</div>
              <div className="flex-1">
                <p className="font-medium text-gray-900 font-mono">
                  Spec: {phase3?.specification_analysis?.exact_type}
                </p>
                <p className="text-sm text-gray-500">
                  {phase3?.specification_analysis?.cpu} vCPU • {phase3?.specification_analysis?.ram} GB RAM • {phase3?.configuration?.region}
                </p>
              </div>
              <span className="text-sm text-gray-400">{((phase3?.specification_analysis?.confidence || 0) * 100).toFixed(0)}% confidence</span>
            </div>

            {/* Phase 4 Summary */}
            <div className="bg-white rounded-lg p-4 border border-gray-200 flex items-center gap-4">
              <div className="w-8 h-8 rounded-lg bg-green-100 flex items-center justify-center font-bold text-green-600">4</div>
              <div className="flex-1">
                <p className="font-medium text-gray-900">
                  Pricing: {formatCurrency(phase4?.primary_price?.total_monthly_usd || 0)}/month
                </p>
                <p className="text-sm text-gray-500">
                  {formatCurrency((phase4?.primary_price?.total_monthly_usd || 0) * 12)}/year • {((phase4?.accuracy_estimate || 0) * 100).toFixed(0)}% accuracy
                </p>
              </div>
              <span className="text-sm text-gray-400">{phase4?.processing_metadata?.calculation_method}</span>
            </div>

            {/* Phase 5 Summary */}
            <div className="bg-white rounded-lg p-4 border border-gray-200 flex items-center gap-4">
              <div className="w-8 h-8 rounded-lg bg-amber-100 flex items-center justify-center font-bold text-amber-600">5</div>
              <div className="flex-1">
                <p className="font-medium text-gray-900 capitalize">
                  Trade-offs: {phase5?.tradeoff_analysis?.recommendation_strength || 'Moderate'} Recommendation
                </p>
                <p className="text-sm text-gray-500">
                  {phase5?.tradeoff_analysis?.pros?.length || 0} pros • {phase5?.tradeoff_analysis?.cons?.length || 0} cons • {phase5?.tradeoff_analysis?.risks?.length || 0} risks
                </p>
              </div>
              <span className="text-sm text-gray-400">Score: {((phase5?.tradeoff_analysis?.overall_score || 0) * 10).toFixed(1)}/10</span>
            </div>
          </div>
        </div>

        {/* Confidence & Implementation */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Confidence Score */}
          <div className="bg-blue-50 rounded-xl p-5 border border-blue-200">
            <h4 className="font-semibold text-blue-900 mb-4">Overall Confidence</h4>
            <div className="flex items-center gap-4">
              <div className="relative w-24 h-24">
                <svg className="w-24 h-24 transform -rotate-90" viewBox="0 0 36 36">
                  <path
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="#dbeafe"
                    strokeWidth="3"
                  />
                  <path
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="#3b82f6"
                    strokeWidth="3"
                    strokeDasharray={`${(recommendation?.confidence_score || 0) * 100}, 100`}
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-2xl font-bold text-blue-900">
                    {((recommendation?.confidence_score || 0) * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
              <div>
                <p className="text-blue-800 font-medium">
                  {(recommendation?.confidence_score || 0) >= 0.8 ? 'High Confidence' :
                   (recommendation?.confidence_score || 0) >= 0.6 ? 'Moderate Confidence' : 'Lower Confidence'}
                </p>
                <p className="text-sm text-blue-600">
                  Based on pattern matching and requirement analysis
                </p>
              </div>
            </div>
          </div>

          {/* Implementation Time */}
          <div className="bg-green-50 rounded-xl p-5 border border-green-200">
            <h4 className="font-semibold text-green-900 mb-4">Implementation Estimate</h4>
            <div className="flex items-center gap-4">
              <span className="text-4xl">⏱️</span>
              <div>
                <p className="text-2xl font-bold text-green-900">
                  {recommendation?.implementation_time || '1-2 weeks'}
                </p>
                <p className="text-sm text-green-600">
                  Estimated time to production deployment
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Cost Summary Visual */}
        {visual?.cost_summary && (
          <div className="bg-gradient-to-r from-slate-800 to-slate-900 rounded-xl p-6 text-white">
            <h4 className="font-semibold text-slate-200 mb-4">Cost Summary</h4>
            <div className="grid grid-cols-3 gap-6">
              <div>
                <p className="text-slate-400 text-sm">Monthly</p>
                <p className="text-3xl font-bold">{formatCurrency(visual.cost_summary.monthly_cost)}</p>
              </div>
              <div>
                <p className="text-slate-400 text-sm">Annual</p>
                <p className="text-3xl font-bold">{formatCurrency(visual.cost_summary.annual_cost)}</p>
              </div>
              <div>
                <p className="text-slate-400 text-sm">Cost Tier</p>
                <p className="text-xl font-bold capitalize">{visual.cost_summary.cost_tier}</p>
              </div>
            </div>
          </div>
        )}

        {/* Recommended Next Action */}
        <div className="bg-gradient-to-r from-indigo-100 to-purple-100 rounded-xl p-5 border-2 border-indigo-200">
          <div className="flex items-center gap-4">
            <span className="text-4xl">👇</span>
            <div>
              <p className="text-sm font-medium text-indigo-600 uppercase tracking-wide">Recommended Next Action</p>
              <h4 className="text-xl font-bold text-indigo-900">Review and Decide in Phase 7 Below</h4>
              <p className="text-indigo-700 mt-1">
                Scroll down to Phase 7 to accept, customize, or select an alternative architecture. 
                Your decision will finalize this configuration.
              </p>
            </div>
          </div>
        </div>

        {/* Read-Only Notice */}
        <div className="flex items-center gap-3 text-sm text-gray-500 bg-gray-50 rounded-lg p-3">
          <span className="text-lg">📖</span>
          <p>
            <span className="font-medium">Review Mode:</span> This is a read-only summary of the system recommendation. 
            Make your decision in Phase 7 below.
          </p>
        </div>
      </div>
    </PhaseCard>
  );
});

export default Phase6Presentation;
