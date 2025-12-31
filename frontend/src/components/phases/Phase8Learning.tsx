'use client';

import { memo, useMemo, useCallback } from 'react';
import { DecisionContext } from '@/types/api';
import PhaseCard from './PhaseCard';

interface Phase8LearningProps {
  decisionContext: DecisionContext;
  sessionId: string;
}

const Phase8Learning = memo(function Phase8Learning({ decisionContext, sessionId }: Phase8LearningProps) {
  const isDecided = decisionContext.state !== 'RECOMMENDED';

  // Guard: Don't render if no decision made yet
  if (!isDecided) {
    return null;
  }

  // Determine feedback category based on decision
  const getFeedbackCategory = () => {
    switch (decisionContext.state) {
      case 'ACCEPTED':
        return { category: 'perfect-fit', label: 'Perfect Fit', color: 'green', icon: '🎯' };
      case 'CUSTOMIZED':
        // Analyze what was customized
        const customizations = decisionContext.customizations;
        if (customizations?.cpu && customizations.cpu < 4) {
          return { category: 'over-provisioned', label: 'Over-Provisioned', color: 'amber', icon: '📉' };
        }
        if (customizations?.cpu && customizations.cpu > 8) {
          return { category: 'under-provisioned', label: 'Under-Provisioned', color: 'red', icon: '📈' };
        }
        return { category: 'preference-adjusted', label: 'Preference Adjusted', color: 'purple', icon: '🔧' };
      case 'OVERRIDDEN':
        return { category: 'architecture-mismatch', label: 'Architecture Mismatch', color: 'amber', icon: '🔄' };
      default:
        return { category: 'pending', label: 'Pending Decision', color: 'gray', icon: '⏳' };
    }
  };

  const feedback = getFeedbackCategory();

  const colorClasses = {
    green: { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-800', badge: 'bg-green-100 text-green-700' },
    amber: { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-800', badge: 'bg-amber-100 text-amber-700' },
    red: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-800', badge: 'bg-red-100 text-red-700' },
    purple: { bg: 'bg-purple-50', border: 'border-purple-200', text: 'text-purple-800', badge: 'bg-purple-100 text-purple-700' },
    gray: { bg: 'bg-gray-50', border: 'border-gray-200', text: 'text-gray-800', badge: 'bg-gray-100 text-gray-700' },
  };

  const colors = colorClasses[feedback.color as keyof typeof colorClasses];

  return (
    <PhaseCard
      phaseNumber={8}
      title="Learning & Feedback"
      subtitle="Improving future recommendations"
      icon="🧠"
      status={isDecided ? 'completed' : 'pending'}
    >
      <div className="space-y-6">
        {!isDecided ? (
          // Pending State
          <div className="bg-gray-50 rounded-xl p-6 border-2 border-gray-200 text-center">
            <span className="text-5xl mb-4 block">⏳</span>
            <h4 className="text-xl font-semibold text-gray-700 mb-2">Awaiting Your Decision</h4>
            <p className="text-gray-500">
              Once you make a decision in Phase 7, the system will generate a learning signal 
              to improve future recommendations.
            </p>
          </div>
        ) : (
          <>
            {/* Learning Signal Generated */}
            <div className={`rounded-xl p-6 border-2 ${colors.bg} ${colors.border}`}>
              <div className="flex items-center gap-4 mb-4">
                <span className="text-4xl">{feedback.icon}</span>
                <div className="flex-1">
                  <p className={`text-sm font-medium uppercase tracking-wide ${colors.text}`}>
                    Learning Signal Generated
                  </p>
                  <h4 className={`text-xl font-bold ${colors.text}`}>
                    {feedback.label}
                  </h4>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${colors.badge}`}>
                  Logged
                </span>
              </div>

              <p className={`${colors.text} mb-4`}>
                {decisionContext.state === 'ACCEPTED' && 
                  'The AI recommendation matched your needs exactly. This feedback reinforces the pattern matching for similar workloads.'}
                {decisionContext.state === 'CUSTOMIZED' && 
                  'You adjusted the configuration parameters. This feedback helps calibrate sizing recommendations for similar workload profiles.'}
                {decisionContext.state === 'OVERRIDDEN' && 
                  `You selected ${decisionContext.overrideArchitecture?.replace(/_/g, ' ')} instead of the recommended architecture. This feedback improves architecture selection for similar requirements.`}
              </p>

              {/* Learning Data */}
              <div className="bg-white/50 rounded-lg p-4 space-y-3">
                <h5 className={`font-semibold ${colors.text} text-sm`}>Learning Data Captured:</h5>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500">Session ID</p>
                    <p className="font-mono text-gray-900 text-xs">{sessionId}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Decision Type</p>
                    <p className="font-medium text-gray-900">{decisionContext.state}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Feedback Category</p>
                    <p className="font-medium text-gray-900">{feedback.category}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Timestamp</p>
                    <p className="font-medium text-gray-900">
                      {decisionContext.decisionTimestamp 
                        ? new Date(decisionContext.decisionTimestamp).toLocaleString()
                        : '-'}
                    </p>
                  </div>
                </div>

                {/* What was changed */}
                {decisionContext.customizations && (
                  <div className="pt-3 border-t border-gray-200">
                    <p className="text-gray-500 text-sm mb-2">Parameters Changed:</p>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(decisionContext.customizations).map(([key, value]) => (
                        <span key={key} className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs font-mono">
                          {key}: {value}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {decisionContext.overrideArchitecture && (
                  <div className="pt-3 border-t border-gray-200">
                    <p className="text-gray-500 text-sm mb-2">Architecture Override:</p>
                    <span className="px-3 py-1 bg-amber-100 text-amber-700 rounded-full text-sm font-medium capitalize">
                      {decisionContext.overrideArchitecture.replace(/_/g, ' ')}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Expected Future Impact */}
            <div className="bg-blue-50 rounded-lg p-5 border border-blue-200">
              <h4 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
                <span>🔮</span> Expected Future Impact
              </h4>
              <ul className="space-y-2 text-blue-800 text-sm">
                {decisionContext.state === 'ACCEPTED' && (
                  <>
                    <li className="flex items-start gap-2">
                      <span className="text-blue-500">•</span>
                      <span>Similar workload profiles will receive higher confidence scores for this architecture</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-blue-500">•</span>
                      <span>Sizing recommendations for comparable scale will be reinforced</span>
                    </li>
                  </>
                )}
                {decisionContext.state === 'CUSTOMIZED' && (
                  <>
                    <li className="flex items-start gap-2">
                      <span className="text-blue-500">•</span>
                      <span>Resource sizing model will be adjusted for similar workload profiles</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-blue-500">•</span>
                      <span>Future recommendations may suggest different baseline configurations</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-blue-500">•</span>
                      <span>Cost estimation accuracy will improve based on real-world preferences</span>
                    </li>
                  </>
                )}
                {decisionContext.state === 'OVERRIDDEN' && (
                  <>
                    <li className="flex items-start gap-2">
                      <span className="text-blue-500">•</span>
                      <span>Architecture selection model will be updated for similar requirement patterns</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-blue-500">•</span>
                      <span>The chosen architecture may receive higher priority in future recommendations</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-blue-500">•</span>
                      <span>Decision factors will be recalibrated to better match user preferences</span>
                    </li>
                  </>
                )}
              </ul>
            </div>

            {/* Telemetry Summary */}
            <div className="bg-slate-800 rounded-lg p-5 text-white">
              <h4 className="font-semibold text-slate-200 mb-3 flex items-center gap-2">
                <span>📡</span> Telemetry Summary
              </h4>
              <div className="font-mono text-xs space-y-1 text-slate-300">
                <p>{"{"}</p>
                <p className="pl-4">"event": "phase7_decision",</p>
                <p className="pl-4">"session_id": "{sessionId}",</p>
                <p className="pl-4">"decision_type": "{decisionContext.state === 'ACCEPTED' ? 'accepted' : 
                  decisionContext.state === 'CUSTOMIZED' ? 'customized' : 'rejected'}",</p>
                <p className="pl-4">"feedback_category": "{feedback.category}",</p>
                <p className="pl-4">"timestamp": "{decisionContext.decisionTimestamp}"</p>
                <p>{"}"}</p>
              </div>
            </div>
          </>
        )}

        {/* Info Note */}
        <div className="flex items-center gap-3 text-sm text-gray-500 bg-gray-50 rounded-lg p-3">
          <span className="text-lg">ℹ️</span>
          <p>
            <span className="font-medium">Note:</span> Learning signals are stored securely and used only to improve 
            recommendation quality. No personal data is collected.
          </p>
        </div>
      </div>
    </PhaseCard>
  );
});

export default Phase8Learning;
