'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  AlertTriangle,
  CheckCircle2,
  XCircle,
  HelpCircle,
  ShieldAlert,
  ArrowRight,
  ExternalLink,
  Edit3,
  Check,
  RotateCcw,
  Sparkles
} from 'lucide-react';
import { AppShell } from '@/components/AppShell';
import { StatusBadge } from '@/components/StatusBadge';
import { getReviewQueue, submitReviewDecision, ReviewQueueResponse, ReviewItem } from '@/lib/api';

export default function ReviewPage() {
  const [data, setData] = useState<ReviewQueueResponse | null>(null);
  const [selectedItem, setSelectedItem] = useState<ReviewItem | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [loading, setLoading] = useState<boolean>(true);
  const [customValue, setCustomValue] = useState<string>('');
  const [actionSuccessMsg, setActionSuccessMsg] = useState<string | null>(null);

  const fetchQueue = async (category: string) => {
    setLoading(true);
    try {
      const res = await getReviewQueue(category);
      setData(res);
      if (res.items.length > 0 && !selectedItem) {
        setSelectedItem(res.items[0]);
      }
    } catch (err) {
      console.error('Failed to load review queue:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue(selectedCategory);
  }, [selectedCategory]);

  const handleDecision = async (action: string) => {
    if (!selectedItem) return;
    try {
      const res = await submitReviewDecision(selectedItem.id, {
        action,
        override_value: action === 'OVERRIDE_VALUE' ? customValue : undefined,
      });
      setActionSuccessMsg(res.message);
      setTimeout(() => setActionSuccessMsg(null), 3000);

      selectedItem.resolved = true;
      selectedItem.decision = res.decision;

      const nextUnresolved = data?.items.find((i) => !i.resolved && i.id !== selectedItem.id);
      if (nextUnresolved) {
        setSelectedItem(nextUnresolved);
      }
    } catch (err) {
      console.error('Failed to submit decision:', err);
    }
  };

  const counts = data?.counts;

  return (
    <AppShell title="REVIEW CENTER" subtitle="Human-In-The-Loop Discrepancy Triage">
      <div className="space-y-6 max-w-7xl mx-auto font-mono text-xs">
        {/* Category Count Selector */}
        <div className="flex flex-wrap items-center gap-2 bg-[#11161D] border border-[#29313C] rounded-xl p-2.5 shadow-xl">
          {[
            { id: 'all', label: 'ALL ITEMS', count: counts?.all || 0 },
            { id: 'attribute', label: 'ATTRIBUTE CONFLICTS', count: counts?.attribute || 0 },
            { id: 'identity', label: 'IDENTITY ISSUES', count: counts?.identity || 0 },
            { id: 'taxonomy', label: 'TAXONOMY CONFIRMATION', count: counts?.taxonomy || 0 },
            { id: 'quality', label: 'LOW QUALITY BAND', count: counts?.quality || 0 },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => {
                setSelectedCategory(tab.id);
                setSelectedItem(null);
              }}
              className={`px-3 py-2 rounded font-bold flex items-center gap-2 transition-all ${
                selectedCategory === tab.id
                  ? 'bg-[#2F6BFF] text-[#F4F7FB] shadow-[0_0_12px_rgba(47,107,255,0.3)]'
                  : 'text-[#98A3B3] hover:bg-[#151B23] hover:text-[#F4F7FB]'
              }`}
            >
              <span>{tab.label}</span>
              <span
                className={`px-1.5 py-0.2 rounded text-[10px] ${
                  selectedCategory === tab.id ? 'bg-[#0B0F14] text-[#F4F7FB]' : 'bg-[#151B23] text-[#667180]'
                }`}
              >
                {tab.count}
              </span>
            </button>
          ))}
          {counts && counts.resolved > 0 && (
            <span className="ml-auto px-3 py-1 bg-[#62E6A7]/10 text-[#62E6A7] border border-[#62E6A7]/30 rounded font-bold flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>{counts.resolved} RESOLVED IN SESSION</span>
            </span>
          )}
        </div>

        {/* Feedback Alert */}
        {actionSuccessMsg && (
          <div className="bg-[#151B23] border border-[#62E6A7]/40 rounded-lg p-4 flex items-center justify-between text-xs text-[#62E6A7] shadow-[0_0_15px_rgba(98,230,167,0.15)]">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" />
              <span className="font-bold">{actionSuccessMsg}</span>
            </div>
            <span className="text-[10px] text-[#98A3B3]">PERSISTED IN FASTAPI BACKEND</span>
          </div>
        )}

        {/* 2-Column Investigation Workspace */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column (5 Cols): Priority Queue List */}
          <div className="lg:col-span-5 bg-[#11161D] border border-[#29313C] rounded-xl shadow-xl overflow-hidden flex flex-col h-[680px]">
            <div className="px-4 py-3 border-b border-[#29313C] bg-[#151B23] flex items-center justify-between">
              <span className="font-bold text-[#F4F7FB]">PRIORITY QUEUE</span>
              <span className="text-[10px] text-[#667180]">{data?.items.length || 0} RECORDS</span>
            </div>

            <div className="flex-1 overflow-y-auto divide-y divide-[#1F2732]">
              {loading ? (
                <div className="p-8 text-center text-[#667180]">Loading queue records...</div>
              ) : !data?.items.length ? (
                <div className="p-8 text-center text-[#98A3B3]">
                  <CheckCircle2 className="w-8 h-8 text-[#62E6A7] mx-auto mb-2" />
                  No review items in this category.
                </div>
              ) : (
                data.items.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => setSelectedItem(item)}
                    className={`w-full text-left p-4 hover:bg-[#151B23] transition-colors block ${
                      selectedItem?.id === item.id ? 'bg-[#151B23] border-l-4 border-l-[#2F6BFF]' : ''
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-xs text-[#4D7CFF] truncate">
                        {item.mpn || `PRODUCT #${item.product_index}`}
                      </span>
                      {item.resolved ? (
                        <span className="px-2 py-0.5 bg-[#62E6A7]/10 text-[#62E6A7] border border-[#62E6A7]/30 rounded text-[9px] font-bold">
                          RESOLVED
                        </span>
                      ) : (
                        <span
                          className={`px-2 py-0.5 rounded text-[9px] font-bold ${
                            item.priority === 'CRITICAL'
                              ? 'bg-[#FF667A]/15 text-[#FF667A] border border-[#FF667A]/30'
                              : 'bg-[#F5B84B]/15 text-[#F5B84B] border border-[#F5B84B]/30'
                          }`}
                        >
                          {item.priority}
                        </span>
                      )}
                    </div>

                    <div className="font-bold text-[#F4F7FB] mb-1">{item.brand || 'INDUSTRIAL'}</div>
                    <div className="text-[#98A3B3] line-clamp-2 leading-relaxed">{item.summary}</div>
                  </button>
                ))
              )}
            </div>
          </div>

          {/* Right Column (7 Cols): Side-By-Side Resolution */}
          <div className="lg:col-span-7 bg-[#11161D] border border-[#29313C] rounded-xl p-6 shadow-2xl space-y-6">
            {selectedItem ? (
              <>
                <div className="border-b border-[#1F2732] pb-4 flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-bold px-2 py-0.5 bg-[#F5B84B]/10 text-[#F5B84B] border border-[#F5B84B]/30 rounded uppercase">
                        {selectedItem.category} TRIAGE
                      </span>
                      <span className="text-[10px] text-[#667180]">ID: {selectedItem.id}</span>
                    </div>
                    <h2 className="text-lg font-bold text-[#F4F7FB] mt-1">
                      {selectedItem.brand} — {selectedItem.mpn}
                    </h2>
                  </div>

                  <Link
                    href={`/catalog/${selectedItem.id}`}
                    className="text-xs font-bold text-[#4D7CFF] hover:underline flex items-center gap-1"
                  >
                    <span>INSPECT RECORD</span>
                    <ExternalLink className="w-3 h-3" />
                  </Link>
                </div>

                {/* Explanation */}
                <div className="bg-[#151B23] border border-[#F5B84B]/30 rounded-lg p-4 space-y-1">
                  <div className="font-bold text-[#F5B84B] flex items-center gap-1.5">
                    <AlertTriangle className="w-4 h-4" />
                    <span>DISCREPANCY EXPLANATION</span>
                  </div>
                  <p className="text-[#98A3B3] leading-relaxed mt-1">{selectedItem.summary}</p>
                </div>

                {/* Side-by-side comparison */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-[#151B23] border border-[#29313C] rounded-lg p-4 space-y-1.5">
                    <div className="text-[10px] font-bold text-[#667180] uppercase">INPUT CATALOG DESCRIPTOR</div>
                    <div className="text-base font-bold text-[#F4F7FB]">
                      {selectedItem.conflicts?.[0]?.input_value || '18 V (From Raw Descriptor)'}
                    </div>
                    <div className="text-[11px] text-[#98A3B3]">Raw supplier spreadsheet value</div>
                  </div>

                  <div className="bg-[#151B23] border border-[#2F6BFF]/40 rounded-lg p-4 space-y-1.5 shadow-[0_0_15px_rgba(47,107,255,0.15)]">
                    <div className="text-[10px] font-bold text-[#4D7CFF] uppercase">OFFICIAL MANUFACTURER SOURCE</div>
                    <div className="text-base font-bold text-[#62E6A7]">
                      {selectedItem.conflicts?.[0]?.source_value || '20 V MAX (From Official Specs)'}
                    </div>
                    <div className="text-[11px] text-[#98A3B3]">Authoritative engineering specs</div>
                  </div>
                </div>

                {/* Actions */}
                <div className="space-y-3 pt-4 border-t border-[#1F2732]">
                  <div className="text-[10px] font-bold text-[#667180] uppercase tracking-wider">
                    RESOLUTION DECISION
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                    <button
                      onClick={() => handleDecision('ACCEPT_SOURCE')}
                      className="px-4 py-2.5 bg-[#62E6A7] hover:bg-[#62E6A7]/90 text-[#0B0F14] font-bold rounded flex items-center justify-center gap-1.5 shadow-[0_0_12px_rgba(98,230,167,0.25)] transition-all"
                    >
                      <Check className="w-3.5 h-3.5" />
                      <span>[ ACCEPT SOURCE ]</span>
                    </button>

                    <button
                      onClick={() => handleDecision('KEEP_INPUT')}
                      className="px-4 py-2.5 bg-[#151B23] hover:bg-[#1B222C] text-[#F4F7FB] border border-[#29313C] font-bold rounded flex items-center justify-center gap-1.5 transition-all"
                    >
                      <RotateCcw className="w-3.5 h-3.5 text-[#98A3B3]" />
                      <span>[ KEEP INPUT ]</span>
                    </button>

                    <button
                      onClick={() => handleDecision('MARK_UNKNOWN')}
                      className="px-4 py-2.5 bg-[#151B23] hover:bg-[#1B222C] text-[#98A3B3] hover:text-[#F4F7FB] border border-[#29313C] font-bold rounded flex items-center justify-center gap-1.5 transition-all"
                    >
                      <HelpCircle className="w-3.5 h-3.5" />
                      <span>[ MARK UNKNOWN ]</span>
                    </button>
                  </div>

                  {/* Custom Override input */}
                  <div className="pt-2 flex items-center gap-2">
                    <input
                      type="text"
                      value={customValue}
                      onChange={(e) => setCustomValue(e.target.value)}
                      placeholder="Enter custom override value (e.g. '20 V MAX Standard')..."
                      className="flex-1 bg-[#0B0F14] border border-[#29313C] rounded px-3 py-2 text-[#F4F7FB] placeholder:text-[#667180] focus:outline-none focus:border-[#4D7CFF]"
                    />
                    <button
                      onClick={() => handleDecision('OVERRIDE_VALUE')}
                      disabled={!customValue.trim()}
                      className="px-4 py-2 bg-[#2F6BFF] hover:bg-[#4D7CFF] text-[#F4F7FB] font-bold rounded disabled:opacity-30 transition-all"
                    >
                      OVERRIDE
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div className="p-16 text-center text-[#667180]">
                Select an item from the left queue to begin human triage.
              </div>
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
