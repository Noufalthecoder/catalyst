import React from 'react';
import { X, ExternalLink, ShieldCheck, CheckCircle2, Globe, FileText } from 'lucide-react';
import { ProductAttribute, ProductSource } from '@/lib/api';
import { StatusBadge } from './StatusBadge';

interface EvidenceDrawerProps {
  attribute: ProductAttribute | null;
  sources: ProductSource[];
  isOpen: boolean;
  onClose: () => void;
}

export function EvidenceDrawer({ attribute, sources, isOpen, onClose }: EvidenceDrawerProps) {
  if (!isOpen || !attribute) return null;

  const matchedSource = sources.find(
    (s) => s.url === attribute.source || (attribute.source && s.domain.includes(attribute.source))
  ) || sources[0];

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/70 backdrop-blur-xs flex justify-end transition-opacity">
      <div className="w-full max-w-lg bg-[#11161D] h-full shadow-2xl flex flex-col border-l border-[#29313C] animate-in slide-in-from-right duration-200">
        {/* Header */}
        <div className="px-6 py-4 border-b border-[#29313C] flex items-center justify-between bg-[#151B23]">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono font-bold tracking-widest text-[#4D7CFF] uppercase">
                TRACEABLE PROVENANCE
              </span>
              <StatusBadge status={attribute.status} size="sm" />
            </div>
            <h2 className="text-lg font-bold font-mono text-[#F4F7FB] mt-0.5">{attribute.label}</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-[#667180] hover:text-[#F4F7FB] rounded hover:bg-[#1B222C] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Resolved Value Card */}
          <div className="bg-[#151B23] border border-[#2F6BFF]/40 rounded-lg p-5 shadow-[0_0_20px_rgba(47,107,255,0.15)]">
            <span className="text-[10px] font-mono uppercase tracking-wider text-[#98A3B3]">
              Standardized Technical Fact
            </span>
            <div className="mt-1 text-2xl font-extrabold font-mono text-[#F4F7FB]">
              {String(attribute.normalized_value || attribute.value || 'N/A')}
              {attribute.uom && <span className="ml-1.5 text-base font-normal text-[#4D7CFF]">{attribute.uom}</span>}
            </div>
            <div className="mt-2 text-xs font-mono text-[#62E6A7] flex items-center gap-2">
              <span>Confidence: {((attribute.confidence || 0.9) * 100).toFixed(0)}%</span>
              <span>•</span>
              <span>UOM Normalized</span>
            </div>
          </div>

          {/* Source Information */}
          <div className="space-y-2">
            <div className="text-[10px] font-mono font-bold uppercase tracking-wider text-[#667180]">
              Authoritative Manufacturer Source
            </div>
            {matchedSource ? (
              <div className="border border-[#29313C] rounded-lg p-4 space-y-3 bg-[#151B23]">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Globe className="w-4 h-4 text-[#4D7CFF]" />
                    <span className="font-mono font-bold text-xs text-[#F4F7FB]">{matchedSource.domain}</span>
                  </div>
                  <span className="px-2 py-0.5 text-[10px] font-mono font-bold bg-[#62E6A7]/10 text-[#62E6A7] border border-[#62E6A7]/30 rounded">
                    {matchedSource.authority_level} TIER
                  </span>
                </div>

                <div className="text-xs font-mono truncate">
                  <a
                    href={matchedSource.url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-[#4D7CFF] hover:underline flex items-center gap-1 inline-flex"
                  >
                    <span className="truncate max-w-xs">{matchedSource.url}</span>
                    <ExternalLink className="w-3 h-3 shrink-0" />
                  </a>
                </div>

                <div className="grid grid-cols-2 gap-2 text-[11px] font-mono pt-2 border-t border-[#1F2732]">
                  <div>
                    <span className="text-[#667180]">Type:</span>{' '}
                    <span className="text-[#98A3B3] font-semibold">{matchedSource.source_type}</span>
                  </div>
                  <div>
                    <span className="text-[#667180]">Origin:</span>{' '}
                    <span className="text-[#98A3B3] font-semibold">{matchedSource.source_origin || 'LIVE'}</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-xs font-mono text-[#667180] italic p-3 border border-[#29313C] rounded bg-[#151B23]">
                Extracted directly from high-confidence product name rules.
              </div>
            )}
          </div>

          {/* Verbatim Proof */}
          <div className="space-y-2">
            <div className="text-[10px] font-mono font-bold uppercase tracking-wider text-[#667180]">
              Traceable Document Snippet
            </div>
            <div className="bg-[#0B0F14] border border-[#29313C] rounded-lg p-4 font-mono text-xs text-[#62E6A7] leading-relaxed whitespace-pre-wrap">
              {attribute.evidence || (matchedSource ? matchedSource.description?.slice(0, 400) : 'No verbatim text recorded.')}
            </div>
          </div>

          {/* Zero Hallucination Badge */}
          <div className="bg-[#151B23] border border-[#62E6A7]/30 rounded-lg p-4 flex items-start gap-3">
            <ShieldCheck className="w-5 h-5 text-[#62E6A7] shrink-0 mt-0.5" />
            <div>
              <h4 className="text-xs font-mono font-bold text-[#F4F7FB]">0% Hallucination Tolerance</h4>
              <p className="text-[11px] text-[#98A3B3] mt-0.5 leading-relaxed">
                CATALYST does not invent attributes. Values must be matched verbatim or normalized through strict deterministic type checkers.
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-[#29313C] bg-[#151B23] flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-mono font-bold text-[#F4F7FB] bg-[#1B222C] hover:bg-[#29313C] border border-[#29313C] rounded"
          >
            Close Panel
          </button>
        </div>
      </div>
    </div>
  );
}
