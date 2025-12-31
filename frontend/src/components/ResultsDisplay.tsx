'use client';

import { memo, useMemo, useCallback } from 'react';
import { AnalysisResponse, DecisionContext, CustomizationParams } from '@/types/api';
import {
  Phase1Intent,
  Phase2Architecture,
  Phase3Specification,
  Phase4Pricing,
  Phase5Tradeoffs,
  Phase6Presentation,
  Phase7Decision,
  Phase8Learning,
} from './phases';

interface ResultsDisplayProps {
  results: AnalysisResponse;
  decisionContext: DecisionContext;
  originalInput?: string;
  isRerunning?: boolean;
  onAccept?: () => void;
  onCustomize?: (customizations: CustomizationParams) => void;
  onSelectAlternative?: (architecture: string) => void;
  onNewAnalysis?: () => void;
}

// ============================================================================
// DECISION STATE BANNER (Memoized)
// ============================================================================

const DecisionStateBanner = memo(function DecisionStateBanner({ 
  context, 
  onNewAnalysis 
}: { 
  context: DecisionContext; 
  onNewAnalysis?: () => void;
}) {
  const stateConfig = useMemo(() => ({
    RECOMMENDED: {
      bg: 'bg-gradient-to-r from-blue-600 to-indigo-600',
      icon: '🎯',
      label: 'System Recommendation Ready',
      description: 'Review all phases below and make your decision in Phase 7',
    },
    ACCEPTED: {
      bg: 'bg-gradient-to-r from-green-600 to-emerald-600',
      icon: '✅',
      label: 'Recommendation Accepted',
      description: 'Configuration locked. Learning signal generated.',
    },
    CUSTOMIZED: {
      bg: 'bg-gradient-to-r from-purple-600 to-violet-600',
      icon: '🔧',
      label: 'Configuration Customized',
      description: 'Modified parameters applied. Phases recalculated.',
    },
    OVERRIDDEN: {
      bg: 'bg-gradient-to-r from-amber-600 to-orange-600',
      icon: '🔄',
      label: 'Architecture Overridden',
      description: `Selected ${context.overrideArchitecture?.replace(/_/g, ' ')} architecture`,
    },
  }), [context.overrideArchitecture]);

  const config = stateConfig[context.state];

  return (
    <div className={`${config.bg} rounded-2xl p-6 mb-8 text-white shadow-xl`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <span className="text-4xl">{config.icon}</span>
          <div>
            <h2 className="text-2xl font-bold">{config.label}</h2>
            <p className="text-white/80">{config.description}</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          {(context.state === 'ACCEPTED' || context.state === 'CUSTOMIZED' || context.state === 'OVERRIDDEN') && (
            <>
              <div className="text-right text-sm text-white/80">
                <p>Decision Time</p>
                <p className="font-medium">
                  {context.decisionTimestamp 
                    ? new Date(context.decisionTimestamp).toLocaleTimeString()
                    : '-'}
                </p>
              </div>
              {onNewAnalysis && (
                <button
                  onClick={onNewAnalysis}
                  className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg font-medium transition-colors"
                >
                  Start New Analysis
                </button>
              )}
            </>
          )}
        </div>
      </div>

      {/* Baseline vs Modified indicator */}
      {context.state === 'CUSTOMIZED' && context.originalResults && (
        <div className="mt-4 pt-4 border-t border-white/20 flex items-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-gray-300"></span>
            <span className="text-white/80">Baseline (original)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-purple-300"></span>
            <span className="text-white/80">Modified (current)</span>
          </div>
        </div>
      )}
    </div>
  );
});

// ============================================================================
// PHASE NAVIGATION (Memoized)
// ============================================================================

const PhaseNavigation = memo(function PhaseNavigation({ 
  onNavigate,
  hasDecision 
}: { 
  onNavigate: (phase: number) => void;
  hasDecision: boolean;
}) {
  const phases = useMemo(() => [
    { num: 1, label: 'Intent', icon: '🎯', always: true },
    { num: 2, label: 'Architecture', icon: '🏗️', always: true },
    { num: 3, label: 'Specification', icon: '⚙️', always: true },
    { num: 4, label: 'Pricing', icon: '💰', always: true },
    { num: 5, label: 'Trade-offs', icon: '⚖️', always: true },
    { num: 6, label: 'Review', icon: '📊', always: true },
    { num: 7, label: 'Decision', icon: '✅', always: true },
    { num: 8, label: 'Learning', icon: '🧠', always: false }, // Only show after decision
  ], []);

  return (
    <div className="sticky top-0 z-40 bg-white/95 backdrop-blur-sm border-b border-gray-200 py-4 mb-8 -mx-4 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between gap-2">
          {phases.map((phase) => {
            const isVisible = phase.always || hasDecision;
            if (!isVisible) return null;
            return (
              <button
                key={phase.num}
                onClick={() => onNavigate(phase.num)}
                className="flex-1 flex flex-col items-center gap-1 py-2 px-1 rounded-lg hover:bg-gray-100 transition-colors group"
              >
                <div className="flex items-center justify-center w-10 h-10 rounded-full text-lg bg-gray-100 group-hover:bg-gray-200">
                  {phase.icon}
                </div>
                <span className="text-xs font-medium text-gray-500">
                  {phase.label}
                </span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
});

// ============================================================================
// MAIN RESULTS DISPLAY (Optimized with progressive rendering)
// ============================================================================

export default function ResultsDisplay({
  results,
  decisionContext,
  originalInput,
  isRerunning,
  onAccept,
  onCustomize,
  onSelectAlternative,
  onNewAnalysis,
}: ResultsDisplayProps) {
  const { phases } = results;
  
  // Memoize baseline phases to prevent recalculation
  const baselinePhases = useMemo(() => 
    decisionContext.originalResults?.phases, 
    [decisionContext.originalResults]
  );
  
  // Memoize isModified check
  const isModified = useMemo(() => 
    decisionContext.state === 'CUSTOMIZED' || decisionContext.state === 'OVERRIDDEN',
    [decisionContext.state]
  );
  
  // Memoize decision state for progressive rendering
  const hasDecision = useMemo(() => 
    decisionContext.state !== 'RECOMMENDED',
    [decisionContext.state]
  );

  // Memoize current architecture
  const currentArchitecture = useMemo(() => 
    phases.phase2?.architecture_analysis?.primary_architecture,
    [phases.phase2?.architecture_analysis?.primary_architecture]
  );

  // Memoize phase availability checks for progressive rendering
  const phaseAvailability = useMemo(() => ({
    phase1Ready: !!phases.phase1,
    phase2Ready: !!phases.phase2,
    phase3Ready: !!phases.phase3,
    phase4Ready: !!phases.phase4,
    phase5Ready: !!phases.phase5,
    phase6Ready: !!phases.phase6 && !!phases.phase1 && !!phases.phase2 && !!phases.phase3 && !!phases.phase4 && !!phases.phase5,
    phase7Ready: true, // Always show decision controls
    phase8Ready: hasDecision, // Only show after decision
  }), [phases.phase1, phases.phase2, phases.phase3, phases.phase4, phases.phase5, phases.phase6, hasDecision]);

  // Memoized scroll handler
  const scrollToPhase = useCallback((phaseNum: number) => {
    const element = document.getElementById(`phase-${phaseNum}`);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, []);

  return (
    <section className="py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Decision State Banner */}
        <DecisionStateBanner context={decisionContext} onNewAnalysis={onNewAnalysis} />

        {/* Phase Navigation */}
        <PhaseNavigation onNavigate={scrollToPhase} hasDecision={hasDecision} />

        {/* All 8 Phases - Progressive Rendering */}
        <div className="space-y-8">
          {/* Phase 1: Intent Capture - Renders immediately */}
          {phaseAvailability.phase1Ready && (
            <div id="phase-1">
              <Phase1Intent 
                data={phases.phase1!} 
                originalInput={originalInput}
              />
            </div>
          )}

          {/* Phase 2: Architecture Selection - Renders immediately */}
          {phaseAvailability.phase2Ready && (
            <div id="phase-2">
              <Phase2Architecture data={phases.phase2!} />
            </div>
          )}

          {/* Phase 3: Machine Specification - Renders when backend responds */}
          {phaseAvailability.phase3Ready && (
            <div id="phase-3">
              <Phase3Specification 
                data={phases.phase3!}
                baselineData={baselinePhases?.phase3}
                isModified={isModified}
                customizations={decisionContext.customizations}
              />
            </div>
          )}

          {/* Phase 4: Pricing - Renders when backend responds */}
          {phaseAvailability.phase4Ready && (
            <div id="phase-4">
              <Phase4Pricing 
                data={phases.phase4!}
                baselineData={baselinePhases?.phase4}
                isModified={isModified}
                currentArchitecture={currentArchitecture}
              />
            </div>
          )}

          {/* Phase 5: Trade-offs - Renders after analysis completes */}
          {phaseAvailability.phase5Ready && (
            <div id="phase-5">
              <Phase5Tradeoffs 
                data={phases.phase5!}
                isModified={isModified}
                architecture={currentArchitecture}
              />
            </div>
          )}

          {/* Phase 6: Presentation - READ-ONLY dashboard showing Phases 1-5 ONLY */}
          {phaseAvailability.phase6Ready && (
            <div id="phase-6">
              <Phase6Presentation 
                data={phases.phase6!}
                phase1={phases.phase1!}
                phase2={phases.phase2!}
                phase3={phases.phase3!}
                phase4={phases.phase4!}
                phase5={phases.phase5!}
              />
            </div>
          )}

          {/* Phase 7: User Decision - Always visible for interaction */}
          {phaseAvailability.phase7Ready && (
            <div id="phase-7">
              <Phase7Decision
                results={results}
                decisionContext={decisionContext}
                isRerunning={isRerunning}
                onAccept={onAccept}
                onCustomize={onCustomize}
                onSelectAlternative={onSelectAlternative}
              />
            </div>
          )}

          {/* Phase 8: Learning - ONLY after decision */}
          {phaseAvailability.phase8Ready && (
            <div id="phase-8">
              <Phase8Learning 
                decisionContext={decisionContext}
                sessionId={results.session_id}
              />
            </div>
          )}
        </div>

        {/* Footer Summary */}
        <div className="mt-12 pt-8 border-t border-gray-200 text-center text-sm text-gray-500">
          <p>
            Session: <span className="font-mono">{results.session_id}</span> • 
            Status: <span className="capitalize">{results.status}</span> • 
            Decision: <span className="font-medium">{decisionContext.state}</span>
          </p>
        </div>
      </div>
    </section>
  );
}
