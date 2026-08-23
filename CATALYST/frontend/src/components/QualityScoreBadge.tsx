import React from 'react';

interface QualityScoreBadgeProps {
  score: number;
  showBar?: boolean;
}

export function QualityScoreBadge({ score, showBar = false }: QualityScoreBadgeProps) {
  const cleanScore = Math.max(0, Math.min(1, score || 0));
  const scorePercent = Math.round(cleanScore * 100);

  let colorClass = 'text-emerald-700 bg-emerald-50 border-emerald-200';
  let barColor = 'bg-emerald-500';
  let label = 'HIGH';

  if (cleanScore < 0.4) {
    colorClass = 'text-rose-700 bg-rose-50 border-rose-200';
    barColor = 'bg-rose-500';
    label = 'LOW';
  } else if (cleanScore < 0.8) {
    colorClass = 'text-amber-700 bg-amber-50 border-amber-200';
    barColor = 'bg-amber-500';
    label = 'MED';
  }

  return (
    <div className="inline-flex items-center gap-2">
      <span
        className={`px-2 py-0.5 text-xs font-mono font-semibold rounded border ${colorClass}`}
        title={`Quality Score: ${cleanScore.toFixed(2)} (${label})`}
      >
        {cleanScore.toFixed(2)}
      </span>
      {showBar && (
        <div className="w-12 h-1.5 bg-gray-200 rounded-full overflow-hidden">
          <div className={`h-full ${barColor}`} style={{ width: `${scorePercent}%` }} />
        </div>
      )}
    </div>
  );
}
