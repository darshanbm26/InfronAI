'use client';

import { memo } from 'react';
import { Phase1Result } from '@/types/api';
import PhaseCard from './PhaseCard';

interface Phase1IntentProps {
  data: Phase1Result;
  originalInput?: string;
}

const Phase1Intent = memo(function Phase1Intent({ data, originalInput }: Phase1IntentProps) {
  const intent = data?.intent_analysis || {};
  const business = data?.business_context || {};
  const metadata = data?.input_metadata || {};
  const processing = data?.processing_metadata || {};

  // Guard: Don't render if no data
  if (!data || !intent) {
    return null;
  }

  return (
    <PhaseCard
      phaseNumber={1}
      title="Intent Capture & Parsing"
      subtitle="Understanding your requirements"
      icon="🎯"
      status="completed"
      confidence={intent.parsing_confidence || 0}
      processingTime={processing.processing_time_ms || 0}
    >
      <div className="space-y-6">
        {/* Original Input - Read Only */}
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Original Input</p>
            <span className="text-xs bg-gray-200 text-gray-600 px-2 py-0.5 rounded">Read-Only</span>
          </div>
          <p className="text-gray-800 italic">
            "{originalInput || metadata?.raw_input || 'No input captured'}"
          </p>
          <p className="text-xs text-gray-400 mt-2">{metadata?.word_count || 0} words analyzed</p>
        </div>

        {/* Parsed Results Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {/* Workload Type */}
          <div className="bg-blue-50 rounded-lg p-4">
            <p className="text-xs font-medium text-blue-600 uppercase tracking-wide mb-1">Workload Type</p>
            <p className="font-semibold text-gray-900 capitalize">{intent.workload_type?.replace(/_/g, ' ')}</p>
          </div>

          {/* Scale */}
          <div className="bg-green-50 rounded-lg p-4">
            <p className="text-xs font-medium text-green-600 uppercase tracking-wide mb-1">Scale</p>
            <p className="font-semibold text-gray-900">{intent.scale?.estimated_rps?.toLocaleString() || 0} RPS</p>
            <p className="text-xs text-gray-500">{intent.scale?.monthly_users?.toLocaleString() || 0} users/mo</p>
          </div>

          {/* Latency */}
          <div className="bg-amber-50 rounded-lg p-4">
            <p className="text-xs font-medium text-amber-600 uppercase tracking-wide mb-1">Latency</p>
            <p className="font-semibold text-gray-900 capitalize">{intent.requirements?.latency || 'Standard'}</p>
          </div>

          {/* Availability */}
          <div className="bg-purple-50 rounded-lg p-4">
            <p className="text-xs font-medium text-purple-600 uppercase tracking-wide mb-1">Availability</p>
            <p className="font-semibold text-gray-900 capitalize">{intent.requirements?.availability || 'Standard'}</p>
          </div>
        </div>

        {/* Requirements & Constraints */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Requirements */}
          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Requirements Parsed</h4>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Geography</span>
                <span className="font-medium text-gray-900 capitalize">{intent.requirements?.geography || 'Global'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Compliance</span>
                <span className="font-medium text-gray-900">
                  {intent.requirements?.compliance?.length > 0 
                    ? intent.requirements.compliance.join(', ') 
                    : 'None specified'}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Data Volume</span>
                <span className="font-medium text-gray-900">{intent.scale?.data_volume_gb || 0} GB</span>
              </div>
            </div>
          </div>

          {/* Constraints */}
          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Constraints Identified</h4>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Budget Sensitivity</span>
                <span className="font-medium text-gray-900 capitalize">{intent.constraints?.budget_sensitivity || 'Medium'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Team Experience</span>
                <span className="font-medium text-gray-900 capitalize">{intent.constraints?.team_experience || 'Medium'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Time to Market</span>
                <span className="font-medium text-gray-900 capitalize">{intent.constraints?.time_to_market || 'Standard'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Key Requirements Tags */}
        {intent.key_requirements && intent.key_requirements.length > 0 && (
          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Key Requirements Extracted</h4>
            <div className="flex flex-wrap gap-2">
              {intent.key_requirements.map((req, idx) => (
                <span 
                  key={idx}
                  className="px-3 py-1.5 bg-indigo-100 text-indigo-700 rounded-full text-sm font-medium"
                >
                  {req}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Business Context */}
        <div className="bg-gradient-to-r from-slate-50 to-gray-50 rounded-lg p-4 border border-gray-200">
          <h4 className="font-semibold text-gray-900 mb-3">Business Context Analysis</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-gray-500">Category</p>
              <p className="font-medium text-gray-900 capitalize">{business.workload_category || 'N/A'}</p>
            </div>
            <div>
              <p className="text-gray-500">Scale Tier</p>
              <p className="font-medium text-gray-900 capitalize">{business.scale_tier || 'N/A'}</p>
            </div>
            <div>
              <p className="text-gray-500">Complexity</p>
              <p className="font-medium text-gray-900">{business.complexity_score || 0}/10</p>
            </div>
            <div>
              <p className="text-gray-500">Risk Level</p>
              <p className="font-medium text-gray-900 capitalize">{business.risk_level || 'N/A'}</p>
            </div>
          </div>
          {business.estimated_cloud_spend && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-xs text-gray-500 mb-2">Estimated Cloud Spend Range</p>
              <div className="flex gap-4 text-sm">
                <span className="text-green-600">${business.estimated_cloud_spend.low?.toLocaleString()}/mo (low)</span>
                <span className="text-blue-600 font-semibold">${business.estimated_cloud_spend.medium?.toLocaleString()}/mo (likely)</span>
                <span className="text-amber-600">${business.estimated_cloud_spend.high?.toLocaleString()}/mo (high)</span>
              </div>
            </div>
          )}
        </div>

        {/* Assumptions Made by System */}
        <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
          <h4 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
            <span>💭</span> Assumptions Made by System
          </h4>
          <ul className="space-y-2 text-sm text-slate-700">
            <li className="flex items-start gap-2">
              <span className="text-slate-400">•</span>
              <span>Traffic pattern assumed: <span className="font-medium">steady</span> with typical daily variation</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-slate-400">•</span>
              <span>Workload type: <span className="font-medium capitalize">{intent.workload_type?.replace(/_/g, ' ') || 'web application'}</span> (no heavy batch processing)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-slate-400">•</span>
              <span>Data residency: <span className="font-medium capitalize">{intent.requirements?.geography || 'no strict'}</span> geographic constraints</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-slate-400">•</span>
              <span>State management: <span className="font-medium">Stateless preferred</span> application design</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-slate-400">•</span>
              <span>Team capability: <span className="font-medium capitalize">{intent.constraints?.team_experience || 'medium'}</span> cloud operations experience</span>
            </li>
          </ul>
          <p className="text-xs text-slate-500 mt-3 italic">
            These assumptions were inferred from your input. Override in Phase 7 if needed.
          </p>
        </div>

        {/* Confidence Indicator */}
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-500">Parsing Confidence</span>
              <span className="font-medium text-gray-900">{((intent.parsing_confidence || 0) * 100).toFixed(0)}%</span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all ${
                  (intent.parsing_confidence || 0) >= 0.8 ? 'bg-green-500' :
                  (intent.parsing_confidence || 0) >= 0.6 ? 'bg-amber-500' : 'bg-red-500'
                }`}
                style={{ width: `${(intent.parsing_confidence || 0) * 100}%` }}
              />
            </div>
          </div>
          <span className="text-xs text-gray-400">via {processing.gemini_mode || 'gemini'}</span>
        </div>
      </div>
    </PhaseCard>
  );
});

export default Phase1Intent;
