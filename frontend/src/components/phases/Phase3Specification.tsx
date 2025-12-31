'use client';

import { memo, useCallback } from 'react';
import { Phase3Result, CustomizationParams } from '@/types/api';
import PhaseCard from './PhaseCard';

interface Phase3SpecificationProps {
  data: Phase3Result;
  baselineData?: Phase3Result;
  isModified?: boolean;
  customizations?: CustomizationParams;
}

const Phase3Specification = memo(function Phase3Specification({ 
  data, 
  baselineData, 
  isModified,
  customizations 
}: Phase3SpecificationProps) {
  const spec = data?.specification_analysis || {};
  const config = data?.configuration || {};
  const processing = data?.processing_metadata || {};
  
  // Baseline comparison data
  const baseSpec = baselineData?.specification_analysis;
  const baseConfig = baselineData?.configuration;

  // Guard: Don't render if no data
  if (!data || !spec) {
    return null;
  }

  const showDelta = (current: number | string, baseline?: number | string) => {
    if (!isModified || baseline === undefined || current === baseline) return null;
    
    if (typeof current === 'number' && typeof baseline === 'number') {
      const diff = current - baseline;
      const color = diff > 0 ? 'text-green-600' : 'text-red-600';
      return <span className={`text-xs ${color} ml-1`}>({diff > 0 ? '+' : ''}{diff})</span>;
    }
    return <span className="text-xs text-purple-600 ml-1">(changed)</span>;
  };

  return (
    <PhaseCard
      phaseNumber={3}
      title="Machine / Service Specification"
      subtitle="Compute sizing and configuration"
      icon="⚙️"
      status={isModified ? 'modified' : 'completed'}
      confidence={spec.confidence || 0}
      processingTime={processing.processing_time_ms || 0}
    >
      <div className="space-y-6">
        {/* Modified Banner */}
        {isModified && (
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 flex items-center gap-3">
            <span className="text-2xl">🔧</span>
            <div>
              <p className="font-semibold text-purple-800">User Customization Applied</p>
              <p className="text-sm text-purple-600">
                You modified the baseline specification. Changes are highlighted below.
              </p>
            </div>
          </div>
        )}

        {/* Primary Specification Card */}
        <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-6 text-white">
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-slate-400 text-sm mb-1">Compute Type</p>
              <h3 className="text-2xl font-mono font-bold">{spec.exact_type}</h3>
              {isModified && baseSpec?.exact_type !== spec.exact_type && (
                <p className="text-xs text-purple-400 mt-1">
                  Baseline: {baseSpec?.exact_type}
                </p>
              )}
            </div>
            <div className="text-right">
              <p className="text-slate-400 text-sm mb-1">Catalog Match</p>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                spec.catalog_match === 'exact' ? 'bg-green-500/20 text-green-400' :
                spec.catalog_match === 'close' ? 'bg-amber-500/20 text-amber-400' :
                'bg-red-500/20 text-red-400'
              }`}>
                {spec.catalog_match?.toUpperCase() || 'APPROXIMATE'}
              </span>
            </div>
          </div>

          {/* CPU / RAM / Family Grid */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white/10 rounded-lg p-4">
              <p className="text-slate-400 text-xs uppercase tracking-wide mb-1">vCPU</p>
              <p className="text-3xl font-bold">
                {spec.cpu}
                {showDelta(spec.cpu, baseSpec?.cpu)}
              </p>
              <p className="text-slate-400 text-sm">cores</p>
            </div>
            <div className="bg-white/10 rounded-lg p-4">
              <p className="text-slate-400 text-xs uppercase tracking-wide mb-1">Memory</p>
              <p className="text-3xl font-bold">
                {spec.ram}
                {showDelta(spec.ram, baseSpec?.ram)}
              </p>
              <p className="text-slate-400 text-sm">GB RAM</p>
            </div>
            <div className="bg-white/10 rounded-lg p-4">
              <p className="text-slate-400 text-xs uppercase tracking-wide mb-1">Family</p>
              <p className="text-xl font-bold uppercase">{spec.machine_family}</p>
              <p className="text-slate-400 text-sm capitalize">{spec.machine_size}</p>
            </div>
          </div>
        </div>

        {/* Configuration Details */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Region & Instances */}
          <div className="bg-gray-50 rounded-lg p-5">
            <h4 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <span>🌍</span> Deployment Configuration
            </h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Region</span>
                <span className="font-mono font-medium text-gray-900">
                  {config.region}
                  {showDelta(config.region, baseConfig?.region)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Base Instances</span>
                <span className="font-mono font-medium text-gray-900">
                  {config.instances}
                  {showDelta(config.instances, baseConfig?.instances)}
                </span>
              </div>
            </div>
          </div>

          {/* Auto-Scaling */}
          <div className="bg-gray-50 rounded-lg p-5">
            <h4 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <span>📈</span> Auto-Scaling Configuration
            </h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Auto-Scaling</span>
                <span className={`font-medium ${config.auto_scaling?.enabled ? 'text-green-600' : 'text-gray-500'}`}>
                  {config.auto_scaling?.enabled ? 'Enabled' : 'Disabled'}
                </span>
              </div>
              {config.auto_scaling?.enabled && (
                <>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Min Instances</span>
                    <span className="font-mono font-medium text-gray-900">
                      {config.auto_scaling.min_instances}
                      {showDelta(config.auto_scaling.min_instances, baseConfig?.auto_scaling?.min_instances)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Max Instances</span>
                    <span className="font-mono font-medium text-gray-900">
                      {config.auto_scaling.max_instances}
                      {showDelta(config.auto_scaling.max_instances, baseConfig?.auto_scaling?.max_instances)}
                    </span>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Storage */}
          <div className="bg-gray-50 rounded-lg p-5">
            <h4 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <span>💾</span> Storage Configuration
            </h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Storage Type</span>
                <span className="font-medium text-gray-900 uppercase">{config.storage?.type || 'SSD'}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Size</span>
                <span className="font-mono font-medium text-gray-900">{config.storage?.size_gb || 100} GB</span>
              </div>
            </div>
          </div>

          {/* Networking */}
          <div className="bg-gray-50 rounded-lg p-5">
            <h4 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <span>🌐</span> Networking
            </h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">VPC</span>
                <span className={`font-medium ${config.networking?.vpc ? 'text-green-600' : 'text-gray-500'}`}>
                  {config.networking?.vpc ? 'Enabled' : 'Default'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Load Balancer</span>
                <span className={`font-medium ${config.networking?.load_balancer ? 'text-green-600' : 'text-gray-500'}`}>
                  {config.networking?.load_balancer ? 'Enabled' : 'None'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Sizing Rationale */}
        <div className="bg-blue-50 rounded-lg p-5 border border-blue-200">
          <h4 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
            <span>🧠</span> Sizing Rationale
          </h4>
          <p className="text-blue-800">
            {spec.sizing_rationale || 'Sizing determined based on workload type, scale requirements, and cost optimization.'}
          </p>
        </div>

        {/* Headroom / Utilization Indicator */}
        <div className="bg-gradient-to-r from-emerald-50 to-teal-50 rounded-lg p-5 border border-emerald-200">
          <h4 className="font-semibold text-emerald-900 mb-3 flex items-center gap-2">
            <span>📊</span> Capacity & Headroom Analysis
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-emerald-700 mb-1">Target Utilization</p>
              <div className="flex items-center gap-3">
                <div className="flex-1 h-4 bg-emerald-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full"
                    style={{ width: '65%' }}
                  />
                </div>
                <span className="font-bold text-emerald-900">65%</span>
              </div>
              <p className="text-xs text-emerald-600 mt-1">
                Optimal range: 60-70% for balanced performance
              </p>
            </div>
            <div>
              <p className="text-sm text-emerald-700 mb-1">Available Headroom</p>
              <div className="bg-white rounded-lg p-3 border border-emerald-100">
                <p className="text-2xl font-bold text-emerald-800">
                  35%
                </p>
                <p className="text-xs text-emerald-600">
                  ✓ Moderate headroom for traffic spikes
                </p>
              </div>
            </div>
          </div>
          <p className="text-xs text-emerald-600 mt-3 italic">
            This configuration provides sufficient capacity for typical 2-3x traffic bursts.
          </p>
        </div>

        {/* Confidence Indicator */}
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-500">Specification Confidence</span>
              <span className="font-medium text-gray-900">{((spec.confidence || 0) * 100).toFixed(0)}%</span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all ${
                  (spec.confidence || 0) >= 0.8 ? 'bg-green-500' :
                  (spec.confidence || 0) >= 0.6 ? 'bg-amber-500' : 'bg-red-500'
                }`}
                style={{ width: `${(spec.confidence || 0) * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Customizable Overlay Notice */}
        <div className="flex items-center gap-3 text-sm text-gray-500 bg-gray-50 rounded-lg p-3">
          <span className="text-lg">💡</span>
          <p>
            <span className="font-medium">Customizable:</span> You can adjust these specifications in Phase 7. 
            The system will recalculate pricing and trade-offs.
          </p>
        </div>
      </div>
    </PhaseCard>
  );
});

export default Phase3Specification;
