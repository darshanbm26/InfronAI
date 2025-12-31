'use client';

import { useState, useCallback } from 'react';
import Hero from '@/components/Hero';
import IntentCapture from '@/components/IntentCapture';
import PhaseOverview from '@/components/PhaseOverview';
import ResultsDisplay from '@/components/ResultsDisplay';
import { AnalysisResponse, DecisionState, DecisionContext, CustomizationParams } from '@/types/api';
import { apiClient } from '@/lib/api';

export default function Home() {
  // Core analysis results
  const [results, setResults] = useState<AnalysisResponse | null>(null);
  
  // Original user input (preserved for display in Phase 1)
  const [originalInput, setOriginalInput] = useState<string>('');
  
  // Decision state management - aligns with backend Phase 7
  const [decisionContext, setDecisionContext] = useState<DecisionContext>({
    state: 'RECOMMENDED',
    originalResults: null,
  });

  // Loading state for re-runs
  const [isRerunning, setIsRerunning] = useState(false);

  // Track decision start time for telemetry
  const [decisionStartTime, setDecisionStartTime] = useState<number>(Date.now());

  // Handle initial analysis results
  const handleResults = useCallback((newResults: AnalysisResponse, userInput?: string) => {
    console.log('[STATE] New analysis received, state: RECOMMENDED');
    setResults(newResults);
    if (userInput) setOriginalInput(userInput);
    setDecisionStartTime(Date.now());
    setDecisionContext({
      state: 'RECOMMENDED',
      originalResults: newResults,
    });
  }, []);

  // Handle user accepting the recommendation
  const handleAccept = useCallback(async () => {
    if (!results) return;

    console.log('[STATE] User ACCEPTED recommendation');
    setDecisionContext(prev => ({
      ...prev,
      state: 'ACCEPTED',
      decisionTimestamp: new Date().toISOString(),
    }));

    // Submit to backend Phase 7
    const decisionTimeSeconds = Math.floor((Date.now() - decisionStartTime) / 1000);
    await apiClient.submitDecision(results.session_id, 'accepted', {
      decisionTimeSeconds,
    });
  }, [results, decisionStartTime]);

  // Handle user customizing parameters (Phases 3-6 re-run)
  const handleCustomize = useCallback(async (customizations: CustomizationParams) => {
    if (!results?.phases.phase1 || !results?.phases.phase2) return;

    console.log('[STATE] User CUSTOMIZING with:', customizations);
    setIsRerunning(true);

    try {
      // Try to use customize endpoint, fallback to local modification
      try {
        const updatedResults = await apiClient.rerunWithCustomization(
          results.session_id,
          results.phases.phase1,
          results.phases.phase2,
          customizations
        );
        setResults(updatedResults);
      } catch {
        // Fallback: Update results locally with customizations
        console.log('[STATE] Using local customization fallback');
        const updatedResults = applyLocalCustomizations(results, customizations);
        setResults(updatedResults);
      }

      setDecisionContext(prev => ({
        ...prev,
        state: 'CUSTOMIZED',
        customizations,
        decisionTimestamp: new Date().toISOString(),
      }));

      // Submit to backend Phase 7
      const decisionTimeSeconds = Math.floor((Date.now() - decisionStartTime) / 1000);
      await apiClient.submitDecision(results.session_id, 'customized', {
        customizations,
        decisionTimeSeconds,
      });
    } finally {
      setIsRerunning(false);
    }
  }, [results, decisionStartTime]);

  // Handle user selecting alternative architecture (Phases 2-6 re-run)
  const handleSelectAlternative = useCallback(async (architecture: string) => {
    if (!results?.phases.phase1) return;

    console.log('[STATE] User OVERRIDING to architecture:', architecture);
    setIsRerunning(true);

    try {
      // Try to use override endpoint, fallback to full re-run
      try {
        const updatedResults = await apiClient.rerunWithArchitecture(
          results.session_id,
          results.phases.phase1,
          architecture
        );
        setResults(updatedResults);
      } catch {
        // Fallback: Update architecture locally and recalculate
        console.log('[STATE] Using local override fallback');
        const updatedResults = applyLocalArchitectureOverride(results, architecture);
        setResults(updatedResults);
      }

      setDecisionContext(prev => ({
        ...prev,
        state: 'OVERRIDDEN',
        overrideArchitecture: architecture,
        decisionTimestamp: new Date().toISOString(),
        decisionReason: `User selected ${architecture} instead of recommended architecture`,
      }));

      // Submit to backend Phase 7 as rejected (selected alternative)
      const decisionTimeSeconds = Math.floor((Date.now() - decisionStartTime) / 1000);
      await apiClient.submitDecision(results.session_id, 'rejected', {
        selectedAlternative: architecture,
        decisionTimeSeconds,
      });
    } finally {
      setIsRerunning(false);
    }
  }, [results, decisionStartTime]);

  // Handle starting a completely new analysis
  const handleNewAnalysis = useCallback(() => {
    console.log('[STATE] User starting NEW analysis');
    setResults(null);
    setOriginalInput('');
    setDecisionContext({
      state: 'RECOMMENDED',
      originalResults: null,
    });
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <Hero />
      
      {/* Only show IntentCapture if no results yet */}
      {!results && <IntentCapture onResults={handleResults} />}
      
      {results ? (
        <ResultsDisplay 
          results={results}
          decisionContext={decisionContext}
          originalInput={originalInput}
          isRerunning={isRerunning}
          onAccept={handleAccept}
          onCustomize={handleCustomize}
          onSelectAlternative={handleSelectAlternative}
          onNewAnalysis={handleNewAnalysis}
        />
      ) : (
        <PhaseOverview />
      )}
    </main>
  );
}

// Local fallback: Apply customizations without backend
function applyLocalCustomizations(
  results: AnalysisResponse, 
  customizations: CustomizationParams
): AnalysisResponse {
  const updated = JSON.parse(JSON.stringify(results)) as AnalysisResponse;
  
  if (updated.phases.phase3) {
    const spec = updated.phases.phase3.specification_analysis;
    if (customizations.cpu) spec.cpu = customizations.cpu;
    if (customizations.ram) spec.ram = customizations.ram;
    
    // Update machine type based on new specs
    const newMachineType = `n2-custom-${customizations.cpu || spec.cpu}-${(customizations.ram || spec.ram) * 1024}`;
    spec.exact_type = newMachineType;
    
    // Update configuration
    const config = updated.phases.phase3.configuration;
    if (customizations.region) config.region = customizations.region;
    if (customizations.instances) config.instances = customizations.instances;
    if (customizations.minInstances) config.auto_scaling.min_instances = customizations.minInstances;
    if (customizations.maxInstances) config.auto_scaling.max_instances = customizations.maxInstances;
  }

  // Recalculate pricing (rough estimate)
  if (updated.phases.phase4 && customizations.cpu && customizations.ram) {
    const baseCpuCost = 30; // ~$30/month per vCPU
    const baseRamCost = 4;  // ~$4/month per GB RAM
    const instances = customizations.instances || updated.phases.phase3?.configuration?.instances || 1;
    
    const newMonthlyCost = (customizations.cpu * baseCpuCost + customizations.ram * baseRamCost) * instances;
    updated.phases.phase4.primary_price.total_monthly_usd = Math.round(newMonthlyCost);
  }

  // Update consolidated data in Phase 6
  if (updated.phases.phase6?.consolidated_data) {
    if (customizations.cpu) updated.phases.phase6.consolidated_data.machine_type = `n2-custom-${customizations.cpu}-${(customizations.ram || 8) * 1024}`;
    if (customizations.region) updated.phases.phase6.consolidated_data.region = customizations.region;
    if (updated.phases.phase4) {
      updated.phases.phase6.consolidated_data.monthly_cost = updated.phases.phase4.primary_price.total_monthly_usd;
    }
  }

  return updated;
}

// Local fallback: Apply architecture override without backend
function applyLocalArchitectureOverride(
  results: AnalysisResponse,
  newArchitecture: string
): AnalysisResponse {
  const updated = JSON.parse(JSON.stringify(results)) as AnalysisResponse;
  
  // Update Phase 2
  if (updated.phases.phase2) {
    updated.phases.phase2.architecture_analysis.primary_architecture = newArchitecture;
    updated.phases.phase2.architecture_analysis.reasoning = `User selected ${newArchitecture} architecture`;
    updated.phases.phase2.architecture_analysis.confidence = 1.0; // User decision
  }

  // Update Phase 4 pricing based on architecture
  if (updated.phases.phase4) {
    const altPrices = updated.phases.phase4.alternative_prices as Record<string, number>;
    const newPrice = altPrices[newArchitecture];
    if (newPrice) {
      updated.phases.phase4.primary_price.total_monthly_usd = newPrice;
    }
  }

  // Update Phase 6 consolidated
  if (updated.phases.phase6?.consolidated_data) {
    updated.phases.phase6.consolidated_data.architecture = newArchitecture;
    if (updated.phases.phase4) {
      updated.phases.phase6.consolidated_data.monthly_cost = updated.phases.phase4.primary_price.total_monthly_usd;
    }
  }

  return updated;
}
