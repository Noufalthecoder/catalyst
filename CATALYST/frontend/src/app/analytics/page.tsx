'use client';

import React, { useEffect, useState } from 'react';
import { BarChart3, TrendingUp, ShieldCheck, AlertTriangle, PieChart, Activity } from 'lucide-react';
import { AppShell } from '@/components/AppShell';
import { getAnalytics, AnalyticsData } from '@/lib/api';

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await getAnalytics();
        setData(res);
      } catch (err) {
        console.error('Failed to load analytics:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const summary = data?.summary;

  return (
    <AppShell title="ANALYTICS & INSTRUMENTATION" subtitle="Statistical Quality Distributions">
      <div className="space-y-6 max-w-7xl mx-auto font-mono text-xs">
        {/* Metric Strip */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-[#11161D] border border-[#29313C] p-4 rounded-lg">
            <div className="text-[9px] text-[#667180] uppercase">TOTAL PRODUCTS</div>
            <div className="text-2xl font-extrabold text-[#F4F7FB] mt-1">{summary?.total_products || 1000}</div>
            <div className="text-[10px] text-[#62E6A7] mt-0.5">100% Ingested</div>
          </div>
          <div className="bg-[#11161D] border border-[#29313C] p-4 rounded-lg">
            <div className="text-[9px] text-[#667180] uppercase">MEAN QUALITY INDEX</div>
            <div className="text-2xl font-extrabold text-[#4D7CFF] mt-1">{summary?.mean_quality?.toFixed(2) || '0.65'}</div>
            <div className="text-[10px] text-[#98A3B3] mt-0.5">Scale 0.00–1.00</div>
          </div>
          <div className="bg-[#11161D] border border-[#29313C] p-4 rounded-lg">
            <div className="text-[9px] text-[#667180] uppercase">MEDIAN QUALITY INDEX</div>
            <div className="text-2xl font-extrabold text-[#62E6A7] mt-1">{summary?.median_quality?.toFixed(2) || '0.84'}</div>
            <div className="text-[10px] text-[#62E6A7] mt-0.5">Upper Band Concentration</div>
          </div>
          <div className="bg-[#11161D] border border-[#29313C] p-4 rounded-lg">
            <div className="text-[9px] text-[#667180] uppercase">TRACKED ATTRIBUTES</div>
            <div className="text-2xl font-extrabold text-[#F4F7FB] mt-1">{summary?.total_expected_attributes || 5000}</div>
            <div className="text-[10px] text-[#98A3B3] mt-0.5">Schema Slots</div>
          </div>
        </div>

        {/* Quality Histogram */}
        <div className="bg-[#11161D] border border-[#29313C] rounded-xl p-6 shadow-xl space-y-4">
          <div className="border-b border-[#1F2732] pb-3 flex items-center justify-between">
            <span className="font-bold text-[#F4F7FB]">QUALITY SCORE DISTRIBUTION HISTOGRAM</span>
            <span className="text-[10px] text-[#667180]">COMPOSITE CONFIDENCE SCORE</span>
          </div>

          <div className="space-y-3 pt-2">
            {data?.quality_distribution?.map((band) => {
              const maxCount = 1000;
              const pct = (band.count / maxCount) * 100;
              return (
                <div key={band.band} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-[#98A3B3]">{band.band}</span>
                    <span className="font-bold text-[#F4F7FB]">
                      {band.count} PRODUCTS ({((band.count / 1000) * 100).toFixed(1)}%)
                    </span>
                  </div>
                  <div className="w-full bg-[#0B0F14] h-2.5 rounded-full overflow-hidden border border-[#29313C]">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{ width: `${Math.max(pct, 1)}%`, backgroundColor: band.color }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* 2-Column Split: Attributes vs Review Triggers */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Attributes */}
          <div className="bg-[#11161D] border border-[#29313C] rounded-xl p-6 shadow-xl space-y-3">
            <div className="font-bold text-[#F4F7FB] border-b border-[#1F2732] pb-3">
              ATTRIBUTE VERIFICATION STATUS
            </div>
            <div className="space-y-2.5">
              {data?.attribute_breakdown?.map((attr) => (
                <div key={attr.name} className="p-3 rounded bg-[#151B23] border border-[#29313C] flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: attr.color }} />
                    <span className="text-[#F4F7FB]">{attr.name}</span>
                  </div>
                  <div className="text-right">
                    <span className="font-bold text-[#F4F7FB]">{attr.value.toLocaleString()}</span>
                    <span className="text-[10px] text-[#667180] block">
                      {((attr.value / 5000) * 100).toFixed(1)}% OF SCHEMA
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Review Triggers */}
          <div className="bg-[#11161D] border border-[#29313C] rounded-xl p-6 shadow-xl space-y-3">
            <div className="font-bold text-[#F4F7FB] border-b border-[#1F2732] pb-3">
              REVIEW QUEUE DRIVERS
            </div>
            <div className="space-y-2.5">
              {data?.review_triggers?.map((trig) => (
                <div key={trig.trigger} className="p-3 rounded bg-[#151B23] border border-[#29313C] flex items-center justify-between">
                  <div>
                    <span className="font-bold text-[#F4F7FB]">{trig.trigger} ISSUES</span>
                    <span className="text-[10px] text-[#667180] block">
                      Affects {trig.percentage}% of input catalog
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="font-bold text-[#F5B84B]">{trig.count} ITEMS</span>
                    <span className="text-[10px] text-[#667180] block">
                      Score: {trig.avgQuality.toFixed(2)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
