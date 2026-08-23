import React from 'react';
import { PipelineStage } from '@/lib/api';
import { CheckCircle2, ArrowRight } from 'lucide-react';

interface PipelineVisualizerProps {
  stages: PipelineStage[];
}

export function PipelineVisualizer({ stages }: PipelineVisualizerProps) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-xs">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="text-base font-bold text-gray-900">Enrichment Pipeline Lifecycle</h2>
          <p className="text-xs text-gray-500 mt-0.5">
            End-to-end automated processing stages from raw input to 252-column delivery
          </p>
        </div>
        <span className="text-xs font-semibold px-2.5 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-md inline-flex items-center gap-1">
          <CheckCircle2 className="w-3.5 h-3.5" />
          Pipeline Verified
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
        {stages.map((stage, idx) => (
          <div
            key={stage.id}
            className="border border-gray-200 rounded-lg p-3 bg-gray-50/50 hover:bg-white hover:border-blue-300 transition-all flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between text-xs text-gray-400 font-mono mb-1">
                <span>0{idx + 1}</span>
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              </div>
              <h3 className="text-xs font-bold text-gray-900 leading-tight mb-2 truncate" title={stage.name}>
                {stage.name}
              </h3>
            </div>
            <div>
              <div className="text-xs font-mono font-semibold text-blue-600 truncate">{stage.badge}</div>
              <div className="w-full bg-gray-200 h-1 rounded-full mt-1.5 overflow-hidden">
                <div className="bg-blue-600 h-full rounded-full" style={{ width: `${stage.percentage}%` }} />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
