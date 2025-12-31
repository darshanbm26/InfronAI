'use client';

import { memo, useState, useMemo, useCallback } from 'react';
import { 
  AnalysisResponse, 
  DecisionContext, 
  CustomizationParams,
  Phase2Result,
  Phase3Result,
  Phase4Result
} from '@/types/api';
import PhaseCard from './PhaseCard';

interface Phase7DecisionProps {
  results: AnalysisResponse;
  decisionContext: DecisionContext;
  isRerunning?: boolean;
  onAccept?: () => void;
  onCustomize?: (customizations: CustomizationParams) => void;
  onSelectAlternative?: (architecture: string) => void;
}

type Tab = 'accept' | 'customize' | 'alternatives';

const Phase7Decision = memo(function Phase7Decision({
  results,
  decisionContext,
  isRerunning,
  onAccept,
  onCustomize,
  onSelectAlternative,
}: Phase7DecisionProps) {
  const [activeTab, setActiveTab] = useState<Tab>('accept');
  
  // Customization state
  const currentSpec = results.phases.phase3?.specification_analysis;
  const currentConfig = results.phases.phase3?.configuration;
  
  const [cpu, setCpu] = useState(currentSpec?.cpu || 4);
  const [ram, setRam] = useState(currentSpec?.ram || 16);
  const [region, setRegion] = useState(currentConfig?.region || 'us-east1');
  const [instances, setInstances] = useState(currentConfig?.instances || 2);
  const [minInstances, setMinInstances] = useState(currentConfig?.auto_scaling?.min_instances || 1);
  const [maxInstances, setMaxInstances] = useState(currentConfig?.auto_scaling?.max_instances || 10);

  const isDecided = decisionContext.state !== 'RECOMMENDED';
  const architecture = results.phases.phase2?.architecture_analysis;
  const alternatives = architecture?.alternatives || [];
  
  // Pricing for alternatives
  const altPricesRaw = results.phases.phase4?.alternative_prices || {};
  const primaryPrice = results.phases.phase4?.primary_price?.total_monthly_usd || 0;
  const alternativePrices = typeof altPricesRaw === 'object' && !Array.isArray(altPricesRaw)
    ? Object.entries(altPricesRaw).map(([arch, cost]) => ({
        architecture: arch,
        total_monthly_usd: cost as number,
        difference_percent: primaryPrice ? (((cost as number) - primaryPrice) / primaryPrice) * 100 : 0
      }))
    : [];

  const regions = [
    'us-east1', 'us-central1', 'us-west1', 'us-west2',
    'europe-west1', 'europe-west2', 'europe-west3',
    'asia-east1', 'asia-southeast1', 'asia-northeast1'
  ];

  const archIcons: Record<string, string> = {
    serverless: '⚡',
    containers: '📦',
    virtual_machines: '🖥️',
    kubernetes: '☸️',
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  // Calculate estimated cost change for customization preview
  const estimatedNewCost = (() => {
    const baseCpuCost = 30;
    const baseRamCost = 4;
    return (cpu * baseCpuCost + ram * baseRamCost) * instances;
  })();

  const costChange = estimatedNewCost - primaryPrice;
  const hasChanges = 
    cpu !== currentSpec?.cpu ||
    ram !== currentSpec?.ram ||
    region !== currentConfig?.region ||
    instances !== currentConfig?.instances ||
    minInstances !== currentConfig?.auto_scaling?.min_instances ||
    maxInstances !== currentConfig?.auto_scaling?.max_instances;

  const handleApplyCustomization = () => {
    onCustomize?.({
      cpu,
      ram,
      region,
      instances,
      minInstances,
      maxInstances,
    });
  };

  if (isDecided) {
    // Show decision summary instead of controls
    return (
      <PhaseCard
        phaseNumber={7}
        title="User Decision"
        subtitle="Your choice has been recorded"
        icon="✅"
        status="completed"
      >
        <div className="space-y-6">
          <div className={`rounded-xl p-6 ${
            decisionContext.state === 'ACCEPTED' ? 'bg-green-50 border-2 border-green-200' :
            decisionContext.state === 'CUSTOMIZED' ? 'bg-purple-50 border-2 border-purple-200' :
            'bg-amber-50 border-2 border-amber-200'
          }`}>
            <div className="flex items-center gap-4 mb-4">
              <span className="text-4xl">
                {decisionContext.state === 'ACCEPTED' ? '✅' :
                 decisionContext.state === 'CUSTOMIZED' ? '🔧' : '🔄'}
              </span>
              <div>
                <p className={`text-sm font-medium uppercase tracking-wide ${
                  decisionContext.state === 'ACCEPTED' ? 'text-green-600' :
                  decisionContext.state === 'CUSTOMIZED' ? 'text-purple-600' : 'text-amber-600'
                }`}>
                  Decision Recorded
                </p>
                <h3 className={`text-2xl font-bold ${
                  decisionContext.state === 'ACCEPTED' ? 'text-green-800' :
                  decisionContext.state === 'CUSTOMIZED' ? 'text-purple-800' : 'text-amber-800'
                }`}>
                  {decisionContext.state === 'ACCEPTED' ? 'Recommendation Accepted' :
                   decisionContext.state === 'CUSTOMIZED' ? 'Configuration Customized' :
                   `Architecture Overridden to ${decisionContext.overrideArchitecture?.replace(/_/g, ' ')}`}
                </h3>
              </div>
            </div>

            {/* Decision Details */}
            <div className="bg-white/50 rounded-lg p-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Decision Type</span>
                <span className="font-medium text-gray-900">{decisionContext.state}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Timestamp</span>
                <span className="font-medium text-gray-900">
                  {decisionContext.decisionTimestamp 
                    ? new Date(decisionContext.decisionTimestamp).toLocaleString()
                    : '-'}
                </span>
              </div>
              {decisionContext.customizations && (
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Parameters Changed</span>
                  <span className="font-medium text-gray-900">
                    {Object.keys(decisionContext.customizations).length} parameters
                  </span>
                </div>
              )}
              {decisionContext.overrideArchitecture && (
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">New Architecture</span>
                  <span className="font-medium text-gray-900 capitalize">
                    {decisionContext.overrideArchitecture.replace(/_/g, ' ')}
                  </span>
                </div>
              )}
            </div>
          </div>

          <div className="flex items-center gap-3 text-sm text-gray-500 bg-gray-50 rounded-lg p-3">
            <span className="text-lg">📡</span>
            <p>
              <span className="font-medium">Telemetry:</span> Decision logged to backend Phase 7 with 
              decision_type="{decisionContext.state === 'ACCEPTED' ? 'accepted' : 
                             decisionContext.state === 'CUSTOMIZED' ? 'customized' : 'rejected'}"
            </p>
          </div>
        </div>
      </PhaseCard>
    );
  }

  return (
    <PhaseCard
      phaseNumber={7}
      title="User Decision"
      subtitle="Choose how to proceed"
      icon="🎯"
      status="active"
    >
      <div className="space-y-6">
        {/* Decision Instructions */}
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
          <p className="text-blue-800">
            <span className="font-semibold">Your Turn:</span> Review the system recommendation above and choose one of the three options below.
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-2 p-1 bg-gray-100 rounded-xl">
          <button
            onClick={() => setActiveTab('accept')}
            className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
              activeTab === 'accept'
                ? 'bg-green-500 text-white shadow-md'
                : 'text-gray-600 hover:bg-gray-200'
            }`}
          >
            <span>✅</span> Accept
          </button>
          <button
            onClick={() => setActiveTab('customize')}
            className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
              activeTab === 'customize'
                ? 'bg-purple-500 text-white shadow-md'
                : 'text-gray-600 hover:bg-gray-200'
            }`}
          >
            <span>🔧</span> Customize
          </button>
          <button
            onClick={() => setActiveTab('alternatives')}
            className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
              activeTab === 'alternatives'
                ? 'bg-amber-500 text-white shadow-md'
                : 'text-gray-600 hover:bg-gray-200'
            }`}
          >
            <span>🔄</span> Alternatives
          </button>
        </div>

        {/* Tab Content */}
        <div className="min-h-[400px]">
          {/* ACCEPT TAB */}
          {activeTab === 'accept' && (
            <div className="space-y-6">
              <div className="bg-green-50 rounded-xl p-6 border-2 border-green-200">
                <div className="flex items-start gap-4">
                  <span className="text-5xl">✅</span>
                  <div className="flex-1">
                    <h4 className="text-xl font-bold text-green-800 mb-2">Accept System Recommendation</h4>
                    <p className="text-green-700 mb-4">
                      Proceed with the AI-recommended configuration. This option provides the best balance 
                      of cost, performance, and operational simplicity for your stated requirements.
                    </p>
                    
                    {/* Quick Summary */}
                    <div className="bg-white rounded-lg p-4 grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-gray-500">Architecture</p>
                        <p className="font-semibold capitalize">
                          {architecture?.primary_architecture?.replace(/_/g, ' ')}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-500">Compute</p>
                        <p className="font-semibold font-mono">{currentSpec?.exact_type}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Monthly Cost</p>
                        <p className="font-semibold">{formatCurrency(primaryPrice)}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <button
                onClick={onAccept}
                disabled={isRerunning}
                className="w-full py-4 bg-green-600 hover:bg-green-700 text-white font-bold text-lg rounded-xl transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
              >
                ✓ Accept Recommendation
              </button>

              {/* Consequences Micro-copy */}
              <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                <p className="text-sm font-semibold text-green-800 mb-2">⚡ What happens when you accept:</p>
                <ul className="text-sm text-green-700 space-y-1">
                  <li className="flex items-center gap-2"><span>•</span> Configuration is locked as the baseline</li>
                  <li className="flex items-center gap-2"><span>•</span> No further recalculations needed</li>
                  <li className="flex items-center gap-2"><span>•</span> Decision logged with decision_type="accepted"</li>
                  <li className="flex items-center gap-2"><span>•</span> Ready for immediate implementation</li>
                </ul>
              </div>
            </div>
          )}

          {/* CUSTOMIZE TAB */}
          {activeTab === 'customize' && (
            <div className="space-y-6">
              <div className="bg-purple-50 rounded-xl p-6 border-2 border-purple-200">
                <div className="flex items-start gap-4 mb-6">
                  <span className="text-4xl">🔧</span>
                  <div>
                    <h4 className="text-xl font-bold text-purple-800 mb-1">Customize Configuration</h4>
                    <p className="text-purple-700">
                      Modify machine specs while keeping the same architecture. 
                      Phases 3-6 will be recalculated.
                    </p>
                  </div>
                </div>

                {/* Customization Controls */}
                <div className="space-y-6 bg-white rounded-lg p-6 border border-purple-100">
                  {/* CPU & RAM */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        vCPU Cores
                        {cpu !== currentSpec?.cpu && (
                          <span className="ml-2 text-purple-600 text-xs">
                            (baseline: {currentSpec?.cpu})
                          </span>
                        )}
                      </label>
                      <input
                        type="range"
                        min="1"
                        max="64"
                        value={cpu}
                        onChange={(e) => setCpu(Number(e.target.value))}
                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
                      />
                      <div className="flex justify-between text-sm mt-1">
                        <span className="text-gray-400">1</span>
                        <span className="font-bold text-purple-600">{cpu} vCPU</span>
                        <span className="text-gray-400">64</span>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Memory (GB)
                        {ram !== currentSpec?.ram && (
                          <span className="ml-2 text-purple-600 text-xs">
                            (baseline: {currentSpec?.ram})
                          </span>
                        )}
                      </label>
                      <input
                        type="range"
                        min="1"
                        max="256"
                        value={ram}
                        onChange={(e) => setRam(Number(e.target.value))}
                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
                      />
                      <div className="flex justify-between text-sm mt-1">
                        <span className="text-gray-400">1 GB</span>
                        <span className="font-bold text-purple-600">{ram} GB</span>
                        <span className="text-gray-400">256 GB</span>
                      </div>
                    </div>
                  </div>

                  {/* Region */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Region
                      {region !== currentConfig?.region && (
                        <span className="ml-2 text-purple-600 text-xs">
                          (baseline: {currentConfig?.region})
                        </span>
                      )}
                    </label>
                    <select
                      value={region}
                      onChange={(e) => setRegion(e.target.value)}
                      className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    >
                      {regions.map(r => (
                        <option key={r} value={r}>{r}</option>
                      ))}
                    </select>
                  </div>

                  {/* Instances & Auto-scaling */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Base Instances</label>
                      <input
                        type="number"
                        min="1"
                        max="100"
                        value={instances}
                        onChange={(e) => setInstances(Number(e.target.value))}
                        className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Min (Auto-scale)</label>
                      <input
                        type="number"
                        min="0"
                        max={instances}
                        value={minInstances}
                        onChange={(e) => setMinInstances(Number(e.target.value))}
                        className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Max (Auto-scale)</label>
                      <input
                        type="number"
                        min={instances}
                        max="1000"
                        value={maxInstances}
                        onChange={(e) => setMaxInstances(Number(e.target.value))}
                        className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                  </div>
                </div>

                {/* Cost Impact Preview */}
                {hasChanges && (
                  <div className="mt-4 bg-purple-100 rounded-lg p-4">
                    <p className="text-sm font-medium text-purple-800 mb-2">Estimated Cost Impact</p>
                    <div className="flex items-center gap-4">
                      <span className="text-gray-600">
                        {formatCurrency(primaryPrice)} → {formatCurrency(estimatedNewCost)}
                      </span>
                      <span className={`font-bold ${costChange > 0 ? 'text-red-600' : 'text-green-600'}`}>
                        ({costChange > 0 ? '+' : ''}{formatCurrency(costChange)})
                      </span>
                    </div>
                  </div>
                )}
              </div>

              <button
                onClick={handleApplyCustomization}
                disabled={isRerunning || !hasChanges}
                className="w-full py-4 bg-purple-600 hover:bg-purple-700 text-white font-bold text-lg rounded-xl transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {isRerunning ? (
                  <>
                    <span className="animate-spin">⟳</span> Re-calculating Phases 3-6...
                  </>
                ) : (
                  <>🔧 Apply Customization</>
                )}
              </button>

              {/* Consequences Micro-copy */}
              <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                <p className="text-sm font-semibold text-purple-800 mb-2">⚡ What happens when you customize:</p>
                <ul className="text-sm text-purple-700 space-y-1">
                  <li className="flex items-center gap-2"><span>•</span> Same architecture, modified machine specs</li>
                  <li className="flex items-center gap-2"><span>•</span> Phases 3-6 are recalculated with your values</li>
                  <li className="flex items-center gap-2"><span>•</span> Baseline vs modified comparison shown</li>
                  <li className="flex items-center gap-2"><span>•</span> Decision logged with decision_type="customized"</li>
                </ul>
              </div>
            </div>
          )}

          {/* ALTERNATIVES TAB */}
          {activeTab === 'alternatives' && (
            <div className="space-y-6">
              <div className="bg-amber-50 rounded-xl p-6 border-2 border-amber-200">
                <div className="flex items-start gap-4 mb-6">
                  <span className="text-4xl">🔄</span>
                  <div>
                    <h4 className="text-xl font-bold text-amber-800 mb-1">Select Alternative Architecture</h4>
                    <p className="text-amber-700">
                      Override the AI recommendation with a different architecture. 
                      Phases 2-6 will be recalculated.
                    </p>
                  </div>
                </div>

                {/* Current Architecture */}
                <div className="bg-white rounded-lg p-4 border border-amber-200 mb-4">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-2xl">{archIcons[architecture?.primary_architecture || ''] || '🔧'}</span>
                    <div>
                      <p className="text-xs text-amber-600 font-medium uppercase">Current Recommendation</p>
                      <p className="font-semibold text-gray-900 capitalize">
                        {architecture?.primary_architecture?.replace(/_/g, ' ')}
                      </p>
                    </div>
                    <span className="ml-auto text-lg font-bold text-gray-900">
                      {formatCurrency(primaryPrice)}/mo
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">{architecture?.reasoning}</p>
                </div>

                {/* Alternative Options */}
                <div className="space-y-3">
                  {alternatives.map((alt, idx) => {
                    const pricing = alternativePrices.find(p => p.architecture === alt.architecture);
                    const isCurrent = alt.architecture === architecture?.primary_architecture;

                    return (
                      <div
                        key={idx}
                        className={`bg-white rounded-lg p-4 border-2 transition-all ${
                          isCurrent 
                            ? 'border-gray-200 opacity-50 cursor-not-allowed' 
                            : 'border-gray-200 hover:border-amber-400 cursor-pointer'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4">
                            <span className="text-3xl">{archIcons[alt.architecture] || '🔧'}</span>
                            <div>
                              <p className="font-semibold text-gray-900 capitalize">
                                {alt.architecture?.replace(/_/g, ' ')}
                                {isCurrent && <span className="ml-2 text-xs text-gray-500">(current)</span>}
                              </p>
                              <p className="text-sm text-gray-500">{alt.when_to_consider}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-4">
                            {pricing && (
                              <div className="text-right">
                                <p className="font-bold text-gray-900">
                                  {formatCurrency(pricing.total_monthly_usd)}/mo
                                </p>
                                <p className={`text-xs font-medium ${
                                  pricing.difference_percent > 0 ? 'text-red-600' : 'text-green-600'
                                }`}>
                                  {pricing.difference_percent > 0 ? '+' : ''}
                                  {pricing.difference_percent.toFixed(0)}% vs current
                                </p>
                              </div>
                            )}
                            <button
                              onClick={() => !isCurrent && onSelectAlternative?.(alt.architecture)}
                              disabled={isCurrent || isRerunning}
                              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                                isCurrent
                                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                  : 'bg-amber-500 text-white hover:bg-amber-600'
                              }`}
                            >
                              {isRerunning ? '...' : 'Select'}
                            </button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Consequences Micro-copy */}
              <div className="bg-amber-50 rounded-lg p-4 border border-amber-200">
                <p className="text-sm font-semibold text-amber-800 mb-2">⚠️ What happens when you select an alternative:</p>
                <ul className="text-sm text-amber-700 space-y-1">
                  <li className="flex items-center gap-2"><span>•</span> Different architecture chosen over AI recommendation</li>
                  <li className="flex items-center gap-2"><span>•</span> Phases 2-6 are fully recalculated</li>
                  <li className="flex items-center gap-2"><span>•</span> May increase operational complexity</li>
                  <li className="flex items-center gap-2"><span>•</span> Decision logged with decision_type="rejected"</li>
                </ul>
              </div>
            </div>
          )}
        </div>

        {/* Loading Overlay */}
        {isRerunning && (
          <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl p-8 shadow-2xl text-center">
              <div className="animate-spin w-12 h-12 border-4 border-purple-600 border-t-transparent rounded-full mx-auto mb-4"></div>
              <p className="text-lg font-semibold text-gray-900">Re-calculating...</p>
              <p className="text-sm text-gray-500">Updating phases based on your changes</p>
            </div>
          </div>
        )}
      </div>
    </PhaseCard>
  );
});

export default Phase7Decision;
