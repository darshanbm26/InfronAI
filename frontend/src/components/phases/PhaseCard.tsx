'use client';

import { memo, ReactNode } from 'react';

interface PhaseCardProps {
  phaseNumber: number;
  title: string;
  subtitle?: string;
  icon: string;
  status: 'pending' | 'active' | 'completed' | 'modified';
  children: ReactNode;
  confidence?: number;
  processingTime?: number;
}

// Memoized PhaseCard to prevent unnecessary re-renders
const PhaseCard = memo(function PhaseCard({
  phaseNumber,
  title,
  subtitle,
  icon,
  status,
  children,
  confidence,
  processingTime,
}: PhaseCardProps) {
  const statusStyles = {
    pending: 'border-gray-200 bg-gray-50',
    active: 'border-blue-400 bg-blue-50 ring-2 ring-blue-200',
    completed: 'border-green-200 bg-white',
    modified: 'border-purple-400 bg-purple-50 ring-2 ring-purple-200',
  };

  const statusBadge = {
    pending: { bg: 'bg-gray-100', text: 'text-gray-500', label: 'Pending' },
    active: { bg: 'bg-blue-100', text: 'text-blue-700', label: 'Processing' },
    completed: { bg: 'bg-green-100', text: 'text-green-700', label: 'Complete' },
    modified: { bg: 'bg-purple-100', text: 'text-purple-700', label: 'Modified' },
  };

  const badge = statusBadge[status];

  return (
    <div className={`rounded-xl border-2 ${statusStyles[status]} transition-all duration-300`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 text-white font-bold text-sm">
            {phaseNumber}
          </div>
          <div className="flex items-center gap-3">
            <span className="text-2xl">{icon}</span>
            <div>
              <h3 className="font-bold text-gray-900">{title}</h3>
              {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {confidence !== undefined && (
            <div className="text-right">
              <p className="text-xs text-gray-500">Confidence</p>
              <p className="font-semibold text-gray-900">{(confidence * 100).toFixed(0)}%</p>
            </div>
          )}
          {processingTime !== undefined && (
            <div className="text-right">
              <p className="text-xs text-gray-500">Time</p>
              <p className="font-mono text-sm text-gray-600">{processingTime}ms</p>
            </div>
          )}
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${badge.bg} ${badge.text}`}>
            {badge.label}
          </span>
        </div>
      </div>
      
      {/* Content */}
      <div className="p-6">
        {children}
      </div>
    </div>
  );
});

export default PhaseCard;
