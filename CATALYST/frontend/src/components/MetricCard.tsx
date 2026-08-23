import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: string;
  badge?: string;
  color?: 'blue' | 'emerald' | 'amber' | 'neutral';
}

export function MetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  badge,
  color = 'neutral',
}: MetricCardProps) {
  const iconColors = {
    blue: 'text-blue-600 bg-blue-50 border-blue-100',
    emerald: 'text-emerald-600 bg-emerald-50 border-emerald-100',
    amber: 'text-amber-600 bg-amber-50 border-amber-100',
    neutral: 'text-gray-600 bg-gray-50 border-gray-100',
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5 shadow-xs hover:border-gray-300 transition-colors">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wider text-gray-500">{title}</span>
        <div className={`p-2 rounded-md border ${iconColors[color]}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-2xl font-bold tracking-tight text-gray-900">{value}</span>
        {badge && (
          <span className="text-xs font-medium px-2 py-0.5 rounded bg-gray-100 text-gray-700">
            {badge}
          </span>
        )}
      </div>
      {(subtitle || trend) && (
        <div className="mt-2 text-xs text-gray-500 flex items-center gap-1.5">
          {trend && <span className="font-medium text-emerald-600">{trend}</span>}
          {subtitle && <span>{subtitle}</span>}
        </div>
      )}
    </div>
  );
}
