'use client';

import { memo, useMemo, useCallback } from 'react';
import { Phase4Result } from '@/types/api';
import PhaseCard from './PhaseCard';

interface Phase4PricingProps {
  data: Phase4Result;
  baselineData?: Phase4Result;
  isModified?: boolean;
  currentArchitecture?: string;
}

const Phase4Pricing = memo(function Phase4Pricing({ 
  data, 
  baselineData, 
  isModified,
  currentArchitecture 
}: Phase4PricingProps) {
  const price = data.primary_price;
  const savings = data.savings_analysis;
  const processing = data.processing_metadata;
  
  const basePrice = baselineData?.primary_price;
  
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

  // Memoize cost delta calculations
  const { costDelta, costDeltaPercent } = useMemo(() => {
    const delta = isModified && basePrice 
      ? price.total_monthly_usd - basePrice.total_monthly_usd 
      : 0;
    const deltaPercent = basePrice && basePrice.total_monthly_usd > 0
      ? (delta / basePrice.total_monthly_usd) * 100
      : 0;
    return { costDelta: delta, costDeltaPercent: deltaPercent };
  }, [isModified, basePrice, price.total_monthly_usd]);

  // Memoize alternative prices conversion
  const alternativePrices = useMemo(() => {
    const altPricesRaw = data.alternative_prices || {};
    if (typeof altPricesRaw === 'object' && !Array.isArray(altPricesRaw)) {
      return Object.entries(altPricesRaw).map(([arch, cost]) => ({
        architecture: arch,
        total_monthly_usd: cost as number,
        difference_percent: price.total_monthly_usd > 0 
          ? (((cost as number) - price.total_monthly_usd) / price.total_monthly_usd) * 100 
          : 0
      }));
    }
    return (altPricesRaw as { architecture: string; total_monthly_usd: number; difference_percent: number }[]);
  }, [data.alternative_prices, price.total_monthly_usd]);

  // Guard: Don't render if essential price data is missing
  if (!price || !Number.isFinite(price.total_monthly_usd)) {
    return null;
  }

  return (
    <PhaseCard
      phaseNumber={4}
      title="Pricing Calculation"
      subtitle="Cost analysis and comparison"
      icon="💰"
      status={isModified ? 'modified' : 'completed'}
      processingTime={processing.processing_time_ms}
    >
      <div className="space-y-6">
        {/* Main Cost Display */}
        <div className="bg-gradient-to-br from-green-600 to-emerald-700 rounded-xl p-6 text-white relative overflow-hidden">
          {/* Background Pattern */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute inset-0" style={{
              backgroundImage: 'radial-gradient(circle at 75% 75%, white 1px, transparent 1px)',
              backgroundSize: '24px 24px'
            }} />
          </div>

          <div className="relative z-10">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-green-200 text-sm mb-1">
                  {isModified ? 'Modified Monthly Cost' : 'Estimated Monthly Cost'}
                </p>
                <p className="text-5xl font-bold">{formatCurrency(price.total_monthly_usd)}</p>
              </div>
              <div className="text-right">
                <p className="text-green-200 text-sm mb-1">Annual Estimate</p>
                <p className="text-2xl font-semibold">{formatCurrency(price.total_monthly_usd * 12)}</p>
              </div>
            </div>

            {/* Cost Delta from Baseline */}
            {isModified && basePrice && (
              <div className="mt-4 pt-4 border-t border-white/20 flex items-center justify-between">
                <div>
                  <p className="text-green-200 text-sm">Baseline Cost</p>
                  <p className="text-xl font-semibold">{formatCurrency(basePrice.total_monthly_usd)}/mo</p>
                </div>
                <div className={`px-4 py-2 rounded-lg ${
                  costDelta > 0 ? 'bg-red-500/30' : costDelta < 0 ? 'bg-green-500/30' : 'bg-white/20'
                }`}>
                  <p className="text-sm text-center">
                    {costDelta > 0 ? '📈 Increase' : costDelta < 0 ? '📉 Savings' : '= No Change'}
                  </p>
                  <p className="text-xl font-bold text-center">
                    {costDelta > 0 ? '+' : ''}{formatCurrency(costDelta)}
                  </p>
                  <p className="text-xs text-center">
                    ({costDeltaPercent > 0 ? '+' : ''}{costDeltaPercent.toFixed(1)}%)
                  </p>
                </div>
              </div>
            )}

            {/* Accuracy Estimate */}
            <div className="mt-4 flex items-center gap-2">
              <span className="text-xs bg-white/20 rounded-full px-3 py-1">
                Accuracy: {((data.accuracy_estimate || 0) * 100).toFixed(0)}% • {processing?.calculation_method || 'estimated'}
              </span>
            </div>
          </div>
        </div>

        {/* Cost Breakdown */}
        {price.breakdown && (
          <div className="bg-gray-50 rounded-lg p-5">
            <h4 className="font-semibold text-gray-900 mb-4">Cost Breakdown</h4>
            <div className="space-y-3">
              {[
                { label: 'Compute', value: price.breakdown.compute || 0, icon: '🖥️', color: 'bg-blue-500' },
                { label: 'Storage', value: price.breakdown.storage || 0, icon: '💾', color: 'bg-purple-500' },
                { label: 'Networking', value: price.breakdown.networking || 0, icon: '🌐', color: 'bg-green-500' },
                { label: 'Other', value: price.breakdown.other || 0, icon: '📦', color: 'bg-gray-500' },
              ].map((item) => {
                const percent = price.total_monthly_usd > 0 
                  ? (item.value / price.total_monthly_usd) * 100 
                  : 0;
                return (
                  <div key={item.label} className="flex items-center gap-3">
                    <span className="text-xl w-8">{item.icon}</span>
                    <div className="flex-1">
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600">{item.label}</span>
                        <span className="font-medium text-gray-900">{formatCurrency(item.value)}</span>
                      </div>
                      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${item.color} rounded-full transition-all`}
                          style={{ width: `${percent}%` }}
                        />
                      </div>
                    </div>
                    <span className="text-sm text-gray-500 w-12 text-right">{percent.toFixed(0)}%</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Alternative Pricing Comparison */}
        {alternativePrices.length > 0 && (
          <div>
            <h4 className="font-semibold text-gray-900 mb-4">Architecture Cost Comparison</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {alternativePrices.map((alt) => {
                const isCurrent = alt.architecture === currentArchitecture;
                const isCheaper = alt.difference_percent < 0;
                
                return (
                  <div 
                    key={alt.architecture}
                    className={`rounded-lg p-4 border-2 transition-all ${
                      isCurrent 
                        ? 'border-blue-400 bg-blue-50' 
                        : 'border-gray-200 bg-white hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <p className="font-semibold text-gray-900 capitalize">
                        {alt.architecture.replace(/_/g, ' ')}
                      </p>
                      {isCurrent && (
                        <span className="text-xs bg-blue-500 text-white px-2 py-0.5 rounded">Current</span>
                      )}
                    </div>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatCurrency(alt.total_monthly_usd)}
                    </p>
                    <p className={`text-sm font-medium ${
                      isCheaper ? 'text-green-600' : alt.difference_percent > 0 ? 'text-red-600' : 'text-gray-500'
                    }`}>
                      {alt.difference_percent > 0 ? '+' : ''}{alt.difference_percent.toFixed(1)}% vs current
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Savings Analysis */}
        {savings && (
          <div className="bg-amber-50 rounded-lg p-5 border border-amber-200">
            <h4 className="font-semibold text-amber-900 mb-3 flex items-center gap-2">
              <span>💡</span> Savings Opportunities
            </h4>
            
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-sm text-amber-700">Potential Savings</p>
                <p className="text-2xl font-bold text-amber-900">
                  {savings.potential_savings_percent?.toFixed(0) || 0}%
                </p>
              </div>
              <div>
                <p className="text-sm text-amber-700">Cheapest Alternative</p>
                <p className="text-lg font-semibold text-amber-900 capitalize">
                  {savings.cheapest_alternative?.replace(/_/g, ' ') || 'Current'}
                </p>
              </div>
            </div>

            {savings.savings_recommendations && savings.savings_recommendations.length > 0 && (
              <div>
                <p className="text-sm text-amber-700 mb-2">Recommendations:</p>
                <ul className="space-y-1">
                  {savings.savings_recommendations.map((rec, idx) => (
                    <li key={idx} className="text-sm text-amber-800 flex items-start gap-2">
                      <span className="text-amber-600">•</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Pricing Note */}
        <div className="flex items-center gap-3 text-sm text-gray-500 bg-gray-50 rounded-lg p-3">
          <span className="text-lg">📊</span>
          <p>
            <span className="font-medium">Note:</span> Prices are estimates based on {price.billing_period} billing. 
            Actual costs may vary based on usage patterns and GCP pricing changes.
          </p>
        </div>
      </div>
    </PhaseCard>
  );
});

export default Phase4Pricing;
