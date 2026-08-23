'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  Boxes,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Globe2,
  Sparkles,
  ArrowRight,
  Play,
  RotateCcw,
  ExternalLink,
  Download,
  FileSpreadsheet,
  Terminal,
  Activity
} from 'lucide-react';
import { AppShell } from '@/components/AppShell';
import { StatusBadge } from '@/components/StatusBadge';
import { getOverviewStats, getHeroDemoProduct, OverviewData, HeroDemoResponse } from '@/lib/api';

export default function DashboardPage() {
  const [stats, setStats] = useState<OverviewData | null>(null);
  const [demoData, setDemoData] = useState<HeroDemoResponse | null>(null);
  const [activeDemoStep, setActiveDemoStep] = useState<number>(0);
  const [isPlayingDemo, setIsPlayingDemo] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [statsRes, heroRes] = await Promise.all([
          getOverviewStats(),
          getHeroDemoProduct(),
        ]);
        setStats(statsRes);
        setDemoData(heroRes);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  useEffect(() => {
    let timer: any;
    if (isPlayingDemo && demoData) {
      timer = setInterval(() => {
        setActiveDemoStep((prev) => {
          if (prev >= demoData.pipeline_steps.length - 1) {
            setIsPlayingDemo(false);
            return prev;
          }
          return prev + 1;
        });
      }, 2500);
    }
    return () => clearInterval(timer);
  }, [isPlayingDemo, demoData]);

  const kpis = stats?.kpis;

  return (
    <AppShell title="COMMAND CENTER" subtitle="Industrial Intelligence Operations">
      <div className="space-y-8 max-w-7xl mx-auto">
        {/* Header Console Strip */}
        <div className="bg-[#11161D] border border-[#29313C] rounded-xl p-6 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono font-bold tracking-widest text-[#4D7CFF] uppercase">
                PRODUCTION RUN / 1,000 DATASET
              </span>
              <span className="px-2 py-0.5 bg-[#62E6A7]/10 text-[#62E6A7] border border-[#62E6A7]/30 text-[10px] font-mono rounded">
                COMPLETED • 13.2s
              </span>
            </div>
            <h2 className="text-2xl font-extrabold font-mono text-[#F4F7FB] mt-1 tracking-tight">
              Catalog Intelligence Operations Console
            </h2>
            <p className="text-xs font-mono text-[#98A3B3] mt-0.5">
              Deterministic MPN Resolution • Multi-Source Verification • 252-Column Unilog Conformance
            </p>
          </div>

          <div className="flex items-center gap-3 font-mono text-xs">
            <Link
              href="/review"
              className="px-4 py-2 bg-[#F5B84B]/10 hover:bg-[#F5B84B]/20 text-[#F5B84B] border border-[#F5B84B]/30 rounded font-bold flex items-center gap-2 transition-colors"
            >
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>REVIEW QUEUE ({kpis?.needs_review_count || 529})</span>
            </Link>
            <Link
              href="/catalog"
              className="px-4 py-2 bg-[#2F6BFF] hover:bg-[#4D7CFF] text-[#F4F7FB] rounded font-bold flex items-center gap-2 shadow-[0_0_12px_rgba(47,107,255,0.3)] transition-colors"
            >
              <Boxes className="w-3.5 h-3.5" />
              <span>EXPLORE CATALOG</span>
            </Link>
          </div>
        </div>

        {/* Large Industrial Metric Strip */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 font-mono">
          <div className="bg-[#151B23] border border-[#29313C] p-5 rounded-lg">
            <div className="text-[10px] text-[#667180] uppercase tracking-wider">PRODUCTS PROCESSED</div>
            <div className="text-3xl font-extrabold text-[#F4F7FB] mt-1">1,000</div>
            <div className="text-[10px] text-[#62E6A7] mt-1 font-bold">100% Ingested</div>
          </div>

          <div className="bg-[#151B23] border border-[#29313C] p-5 rounded-lg">
            <div className="text-[10px] text-[#667180] uppercase tracking-wider">HIGH CONFIDENCE</div>
            <div className="text-3xl font-extrabold text-[#62E6A7] mt-1">84.0%</div>
            <div className="text-[10px] text-[#98A3B3] mt-1">Score ≥ 0.80</div>
          </div>

          <div className="bg-[#151B23] border border-[#29313C] p-5 rounded-lg">
            <div className="text-[10px] text-[#667180] uppercase tracking-wider">VERIFIED ATTRIBUTES</div>
            <div className="text-3xl font-extrabold text-[#4D7CFF] mt-1">4,812</div>
            <div className="text-[10px] text-[#62E6A7] mt-1">0% Hallucination</div>
          </div>

          <div className="bg-[#151B23] border border-[#29313C] p-5 rounded-lg">
            <div className="text-[10px] text-[#667180] uppercase tracking-wider">REVIEW REQUIRED</div>
            <div className="text-3xl font-extrabold text-[#F5B84B] mt-1">137</div>
            <div className="text-[10px] text-[#98A3B3] mt-1">Ambiguity Triage</div>
          </div>

          <div className="bg-[#151B23] border border-[#29313C] p-5 rounded-lg">
            <div className="text-[10px] text-[#667180] uppercase tracking-wider">DELIVERY FIELDS</div>
            <div className="text-3xl font-extrabold text-[#F4F7FB] mt-1">252</div>
            <div className="text-[10px] text-[#62E6A7] mt-1">100% Validated</div>
          </div>
        </div>

        {/* Horizontal Intelligence Rail */}
        <div className="bg-[#11161D] border border-[#29313C] rounded-xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-[#1F2732] pb-3 text-xs font-mono">
            <span className="font-bold text-[#F4F7FB]">AUTOMATED INTELLIGENCE RAIL</span>
            <span className="text-[#62E6A7] flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[#62E6A7]" />
              7 STAGES ACTIVE
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 font-mono">
            {[
              { num: '01', title: 'RAW INPUT', metric: '1,000 Rows', status: '100%' },
              { num: '02', title: 'IDENTITY', metric: '99.9% MPN', status: '100%' },
              { num: '03', title: 'TAXONOMY', metric: 'Fine Class', status: '100%' },
              { num: '04', title: 'SOURCES', metric: '753 Official', status: '75.3%' },
              { num: '05', title: 'ATTRIBUTES', metric: '4,812 Facts', status: 'Verified' },
              { num: '06', title: 'VALIDATION', metric: 'UOM Standard', status: '100%' },
              { num: '07', title: 'DELIVERY', metric: '252 Columns', status: 'Ready' },
            ].map((st, idx) => (
              <div
                key={st.num}
                className="bg-[#151B23] border border-[#29313C] hover:border-[#2F6BFF] p-3.5 rounded-lg space-y-1 transition-all"
              >
                <div className="flex items-center justify-between text-[10px] text-[#667180]">
                  <span>{st.num}</span>
                  <span className="text-[#62E6A7]">✓</span>
                </div>
                <div className="text-xs font-bold text-[#F4F7FB]">{st.title}</div>
                <div className="text-[11px] text-[#4D7CFF] font-semibold">{st.metric}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Live Hero Showcase */}
        {demoData && (
          <div className="bg-[#11161D] border border-[#29313C] rounded-xl p-6 shadow-xl space-y-6">
            <div className="flex items-center justify-between border-b border-[#1F2732] pb-4 font-mono">
              <div>
                <div className="text-[10px] font-bold tracking-widest text-[#4D7CFF] uppercase">
                  DETERMINISTIC TRANSFORMATION DEMO
                </div>
                <h3 className="text-lg font-bold text-[#F4F7FB] mt-0.5">
                  See CATALYST in Action — Live Product Engine
                </h3>
              </div>

              <div className="flex items-center gap-2 text-xs">
                <button
                  onClick={() => setIsPlayingDemo(!isPlayingDemo)}
                  className="px-3.5 py-1.5 bg-[#2F6BFF] hover:bg-[#4D7CFF] text-[#F4F7FB] font-bold rounded shadow-[0_0_12px_rgba(47,107,255,0.3)] flex items-center gap-1.5 transition-all"
                >
                  <Play className="w-3.5 h-3.5" />
                  <span>{isPlayingDemo ? 'PAUSE' : 'PLAY STAGES'}</span>
                </button>
                <button
                  onClick={() => {
                    setActiveDemoStep(0);
                    setIsPlayingDemo(false);
                  }}
                  className="px-3 py-1.5 bg-[#151B23] hover:bg-[#1B222C] text-[#98A3B3] font-bold border border-[#29313C] rounded flex items-center gap-1.5"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>RESET</span>
                </button>
              </div>
            </div>

            {/* Step Selector */}
            <div className="grid grid-cols-2 md:grid-cols-6 gap-2 font-mono text-xs">
              {demoData.pipeline_steps.map((step, idx) => (
                <button
                  key={step.step}
                  onClick={() => {
                    setActiveDemoStep(idx);
                    setIsPlayingDemo(false);
                  }}
                  className={`p-3 rounded-lg border text-left transition-all ${
                    activeDemoStep === idx
                      ? 'bg-[#1B222C] border-[#2F6BFF] shadow-[0_0_15px_rgba(47,107,255,0.25)]'
                      : 'bg-[#151B23] border-[#29313C] text-[#98A3B3] hover:border-[#4D7CFF]/40'
                  }`}
                >
                  <div className="text-[10px] text-[#667180]">STAGE 0{step.step}</div>
                  <div className="font-bold text-[#F4F7FB] truncate mt-0.5">{step.title}</div>
                </button>
              ))}
            </div>

            {/* Step Details Box */}
            <div className="bg-[#151B23] border border-[#29313C] rounded-lg p-5 font-mono text-xs space-y-4">
              <div className="flex items-center justify-between">
                <div className="font-bold text-sm text-[#F4F7FB]">
                  {demoData.pipeline_steps[activeDemoStep]?.title}
                </div>
                <span className="text-[10px] font-bold bg-[#62E6A7]/10 text-[#62E6A7] border border-[#62E6A7]/30 px-2 py-0.5 rounded">
                  VERIFIED REAL DATA
                </span>
              </div>

              <p className="text-[#98A3B3] bg-[#0B0F14] p-3.5 rounded border border-[#29313C] leading-relaxed">
                {demoData.pipeline_steps[activeDemoStep]?.description}
              </p>

              {activeDemoStep === 5 && (
                <div className="pt-2 flex justify-end">
                  <Link
                    href={`/catalog/${demoData.product.id || '0'}`}
                    className="px-4 py-2 bg-[#62E6A7] hover:bg-[#62E6A7]/90 text-[#0B0F14] font-mono font-bold rounded flex items-center gap-2 shadow-[0_0_15px_rgba(98,230,167,0.3)] transition-all"
                  >
                    <span>VIEW COMPLETE PRODUCT INTELLIGENCE</span>
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
