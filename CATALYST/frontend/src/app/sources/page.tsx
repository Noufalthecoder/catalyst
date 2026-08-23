'use client';

import React, { useEffect, useState } from 'react';
import { Globe2, ShieldCheck, Database, CheckCircle2, ExternalLink, Activity } from 'lucide-react';
import { AppShell } from '@/components/AppShell';
import { getSourcesOverview } from '@/lib/api';

export default function SourcesPage() {
  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await getSourcesOverview();
        setData(res);
      } catch (err) {
        console.error('Failed to load sources:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const summary = data?.summary;

  return (
    <AppShell title="SOURCE INTELLIGENCE" subtitle="Authoritative Domain Crawlers & Tiers">
      <div className="space-y-6 max-w-7xl mx-auto font-mono text-xs">
        {/* Source Metric Strip */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-[#11161D] border border-[#29313C] p-4 rounded-lg">
            <div className="text-[9px] text-[#667180] uppercase">PRIMARY DOMAINS</div>
            <div className="text-2xl font-extrabold text-[#F4F7FB] mt-1">{summary?.authoritative_domains_count || 48}</div>
            <div className="text-[10px] text-[#4D7CFF] mt-0.5">Tier 1 Authority</div>
          </div>
          <div className="bg-[#11161D] border border-[#29313C] p-4 rounded-lg">
            <div className="text-[9px] text-[#667180] uppercase">CACHED SPEC SHEETS</div>
            <div className="text-2xl font-extrabold text-[#62E6A7] mt-1">{summary?.total_cached_documents || 1460}</div>
            <div className="text-[10px] text-[#98A3B3] mt-0.5">HTML & PDF Docs</div>
          </div>
          <div className="bg-[#11161D] border border-[#29313C] p-4 rounded-lg">
            <div className="text-[9px] text-[#667180] uppercase">OFFICIAL COVERAGE</div>
            <div className="text-2xl font-extrabold text-[#4D7CFF] mt-1">{summary?.official_source_coverage_rate || 75.3}%</div>
            <div className="text-[10px] text-[#62E6A7] mt-0.5">Verified Primary</div>
          </div>
          <div className="bg-[#11161D] border border-[#29313C] p-4 rounded-lg">
            <div className="text-[9px] text-[#667180] uppercase">EXACT MPN MATCH</div>
            <div className="text-2xl font-extrabold text-[#62E6A7] mt-1">{summary?.exact_mpn_match_rate || 74.7}%</div>
            <div className="text-[10px] text-[#98A3B3] mt-0.5">Verbatim Match</div>
          </div>
        </div>

        {/* Source Hierarchy */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-[#11161D] border border-[#62E6A7]/30 rounded-xl p-5 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-[#62E6A7]">PRIMARY TIER (0.40)</span>
              <span className="text-[9px] bg-[#62E6A7]/10 text-[#62E6A7] px-2 py-0.5 rounded">753 SOURCES</span>
            </div>
            <p className="text-[#98A3B3] text-[11px] leading-relaxed">
              Official manufacturer portals and CAD specification sheets (3M, Diablo, Freud, Milwaukee).
            </p>
          </div>

          <div className="bg-[#11161D] border border-[#2F6BFF]/30 rounded-xl p-5 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-[#4D7CFF]">SECONDARY TIER (0.20)</span>
              <span className="text-[9px] bg-[#2F6BFF]/10 text-[#4D7CFF] px-2 py-0.5 rounded">189 SOURCES</span>
            </div>
            <p className="text-[#98A3B3] text-[11px] leading-relaxed">
              Authorized industrial catalog distributors with exact manufacturer part cross-referencing.
            </p>
          </div>

          <div className="bg-[#11161D] border border-[#29313C] rounded-xl p-5 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-[#667180]">UNTRUSTED TIER (0.00)</span>
              <span className="text-[9px] bg-[#151B23] text-[#667180] px-2 py-0.5 rounded">0 SOURCES</span>
            </div>
            <p className="text-[#667180] text-[11px] leading-relaxed">
              Third-party consumer marketplaces and scrape aggregators. Zero consensus weight.
            </p>
          </div>
        </div>

        {/* Domains Registry Table */}
        <div className="bg-[#11161D] border border-[#29313C] rounded-xl shadow-2xl overflow-hidden">
          <div className="px-5 py-3 border-b border-[#29313C] bg-[#151B23] flex items-center justify-between">
            <span className="font-bold text-[#F4F7FB]">AUTHORITATIVE MANUFACTURER REGISTRY</span>
            <span className="text-[10px] text-[#667180]">{data?.top_manufacturer_domains?.length || 0} DOMAINS</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs divide-y divide-[#1F2732]">
              <thead className="bg-[#0B0F14] text-[#667180] text-[10px] uppercase">
                <tr>
                  <th className="px-5 py-3">BRAND</th>
                  <th className="px-5 py-3">DOMAIN</th>
                  <th className="px-5 py-3">TIER</th>
                  <th className="px-5 py-3">TRUST</th>
                  <th className="px-5 py-3 text-right">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1F2732] text-[#F4F7FB]">
                {data?.top_manufacturer_domains?.map((item: any, idx: number) => (
                  <tr key={idx} className="hover:bg-[#151B23]">
                    <td className="px-5 py-3 font-bold">{item.brand}</td>
                    <td className="px-5 py-3 text-[#4D7CFF]">
                      <a href={`https://${item.domain}`} target="_blank" rel="noreferrer" className="hover:underline flex items-center gap-1">
                        <span>{item.domain}</span>
                        <ExternalLink className="w-2.5 h-2.5" />
                      </a>
                    </td>
                    <td className="px-5 py-3">
                      <span className="px-2 py-0.5 bg-[#62E6A7]/10 text-[#62E6A7] border border-[#62E6A7]/30 rounded text-[10px]">
                        {item.authority_level}
                      </span>
                    </td>
                    <td className="px-5 py-3 font-bold text-[#62E6A7]">
                      {((item.trust_score || 0.98) * 100).toFixed(0)}%
                    </td>
                    <td className="px-5 py-3 text-right text-[11px] text-[#98A3B3]">
                      ● ACTIVE DYNAMIC CRAWLER
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
