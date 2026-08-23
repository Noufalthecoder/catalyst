import React from 'react';

interface TrustScoreArcProps {
  score: number;
  size?: number;
  showBreakdown?: boolean;
}

export function TrustScoreArc({ score, size = 120, showBreakdown = true }: TrustScoreArcProps) {
  const cleanScore = Math.max(0, Math.min(1, score || 0));
  const scorePercent = (cleanScore * 100).toFixed(1);
  const strokeWidth = 8;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (cleanScore * circumference * 0.75); // 270 degree arc

  let strokeColor = '#62E6A7'; // Evidence Green
  let label = 'HIGH CONFIDENCE';
  if (cleanScore < 0.4) {
    strokeColor = '#FF667A'; // Danger Red
    label = 'CRITICAL REVIEW';
  } else if (cleanScore < 0.8) {
    strokeColor = '#F5B84B'; // Amber
    label = 'MED CONFIDENCE';
  }

  return (
    <div className="bg-[#151B23] border border-[#29313C] rounded-lg p-5 flex flex-col items-center justify-between">
      <div className="text-[10px] font-mono uppercase tracking-wider text-[#667180] mb-2 font-semibold">
        CATALYST TRUST SCORE
      </div>

      {/* SVG Arc Gauge */}
      <div className="relative flex items-center justify-center my-2" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-135">
          {/* Background Track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#1B222C"
            strokeWidth={strokeWidth}
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={circumference * 0.25}
            strokeLinecap="round"
          />
          {/* Foreground Active Arc */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-700 ease-out"
          />
        </svg>

        {/* Center Score Text */}
        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className="font-mono font-extrabold text-2xl text-[#F4F7FB] leading-none">
            {scorePercent}
          </span>
          <span className="text-[9px] font-mono font-bold uppercase tracking-wider text-[#98A3B3] mt-1">
            / 100
          </span>
        </div>
      </div>

      <div className="text-[10px] font-mono font-bold px-2.5 py-0.5 rounded bg-[#11161D] border border-[#29313C] text-[#98A3B3] mt-1 mb-4">
        {label}
      </div>

      {/* Sub-Score Breakdown */}
      {showBreakdown && (
        <div className="w-full space-y-2 pt-3 border-t border-[#1F2732] text-[11px] font-mono">
          {[
            { dim: 'Identity', val: 100, color: '#62E6A7' },
            { dim: 'Taxonomy', val: Math.round(cleanScore >= 0.8 ? 96 : 60), color: '#4D7CFF' },
            { dim: 'Sources', val: Math.round(cleanScore >= 0.8 ? 100 : 40), color: '#62E6A7' },
            { dim: 'Attributes', val: Math.round(cleanScore >= 0.8 ? 94 : 35), color: cleanScore >= 0.8 ? '#62E6A7' : '#F5B84B' },
            { dim: 'Content', val: 98, color: '#62E6A7' },
          ].map((item) => (
            <div key={item.dim} className="flex items-center justify-between">
              <span className="text-[#667180]">{item.dim}</span>
              <div className="flex items-center gap-2">
                <div className="w-16 bg-[#11161D] h-1.5 rounded-full overflow-hidden border border-[#29313C]">
                  <div className="h-full rounded-full" style={{ width: `${item.val}%`, backgroundColor: item.color }} />
                </div>
                <span className="text-[#F4F7FB] font-bold w-6 text-right">{item.val}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
