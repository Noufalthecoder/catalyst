'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  ArrowRight,
  ShieldCheck,
  Globe,
  Database,
  CheckCircle2,
  Sparkles,
  Boxes,
  Layers,
  Terminal,
  Activity
} from 'lucide-react';
import { CatalystLogo } from '@/components/CatalystLogo';
import { EvidenceGraph } from '@/components/EvidenceGraph';

export default function LandingPage() {
  const [pipelineState, setPipelineState] = useState<number>(0);
  const stages = ['RAW INPUT', 'IDENTIFIED', 'CLASSIFIED', 'ENRICHED', 'VERIFIED', 'COMMERCE READY'];

  useEffect(() => {
    const timer = setInterval(() => {
      setPipelineState((prev) => (prev + 1) % stages.length);
    }, 2000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-[#0B0F14] bg-blueprint-grid text-[#F4F7FB] flex flex-col justify-between">
      {/* Header Navigation */}
      <header className="px-8 py-5 border-b border-[#29313C] bg-[#11161D]/80 backdrop-blur-md flex items-center justify-between sticky top-0 z-40">
        <div className="flex items-center gap-3">
          <CatalystLogo size={30} />
          <div>
            <span className="font-mono font-extrabold text-base tracking-wider text-[#F4F7FB] leading-none block">
              CATALYST
            </span>
            <span className="text-[9px] font-mono tracking-widest text-[#667180] uppercase block mt-0.5">
              INDUSTRIAL INTELLIGENCE
            </span>
          </div>
        </div>

        <div className="flex items-center gap-5 font-mono text-xs">
          <Link
            href="/dashboard"
            className="text-[#98A3B3] hover:text-[#F4F7FB] transition-colors"
          >
            COMMAND CENTER
          </Link>
          <Link
            href="/catalog"
            className="text-[#98A3B3] hover:text-[#F4F7FB] transition-colors"
          >
            CATALOG DATABASE
          </Link>
          <Link
            href="/dashboard"
            className="px-4 py-2 bg-[#2F6BFF] hover:bg-[#4D7CFF] text-[#F4F7FB] font-bold rounded shadow-[0_0_15px_rgba(47,107,255,0.35)] transition-all"
          >
            LAUNCH PLATFORM
          </Link>
        </div>
      </header>

      {/* Hero Section: Split Composition */}
      <main className="max-w-7xl mx-auto px-6 py-16 space-y-24 flex-1">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Left Column: Huge Industrial Typography */}
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#151B23] border border-[#29313C] rounded text-[11px] font-mono text-[#98A3B3]">
              <span className="w-2 h-2 rounded-full bg-[#62E6A7] animate-pulse" />
              <span>CATALOG INTELLIGENCE / 01</span>
            </div>

            <h1 className="text-4xl sm:text-6xl font-extrabold font-mono tracking-tighter text-[#F4F7FB] leading-[1.05]">
              TURN<br />
              MESSY DATA<br />
              INTO <span className="text-[#2F6BFF] drop-shadow-[0_0_25px_rgba(47,107,255,0.5)]">TRUSTED</span><br />
              INTELLIGENCE.
            </h1>

            <p className="text-sm sm:text-base text-[#98A3B3] font-mono max-w-xl leading-relaxed">
              CATALYST transforms fragmented industrial product data into verified, standardized, and commerce-ready catalog intelligence.
            </p>

            <div className="pt-2 flex flex-wrap items-center gap-4 font-mono text-xs">
              <Link
                href="/enrichment"
                className="px-6 py-3 bg-[#2F6BFF] hover:bg-[#4D7CFF] text-white font-bold rounded shadow-[0_0_20px_rgba(47,107,255,0.4)] flex items-center gap-2 transition-all"
              >
                <span>[ START ENRICHMENT ]</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/catalog"
                className="px-6 py-3 bg-[#151B23] hover:bg-[#1B222C] text-[#F4F7FB] font-bold rounded border border-[#29313C] flex items-center gap-2 transition-all"
              >
                <span>[ EXPLORE CATALOG ]</span>
              </Link>
            </div>
          </div>

          {/* Right Column: Live Product Intelligence Terminal Card */}
          <div className="lg:col-span-5">
            <div className="bg-[#11161D] border border-[#29313C] rounded-xl p-6 shadow-2xl space-y-5 relative overflow-hidden">
              {/* Card Header */}
              <div className="flex items-center justify-between border-b border-[#1F2732] pb-3 text-xs font-mono">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-[#2F6BFF]" />
                  <span className="font-bold text-[#F4F7FB]">PRODUCT INTELLIGENCE</span>
                </div>
                <span className="font-bold text-[#62E6A7] bg-[#62E6A7]/10 px-2 py-0.5 rounded border border-[#62E6A7]/30">
                  98.4% ✓
                </span>
              </div>

              {/* Product Identity */}
              <div className="space-y-1 font-mono">
                <div className="text-xl font-extrabold text-[#F4F7FB] tracking-tight">PDSH4816AF</div>
                <div className="text-xs font-bold text-[#4D7CFF]">FRIGIDAIRE®</div>
                <div className="text-[11px] text-[#98A3B3] uppercase tracking-wider mt-1">
                  BUILT-IN DISHWASHER 24 IN
                </div>
              </div>

              {/* Technical Facts Strip */}
              <div className="grid grid-cols-3 gap-2 py-3 border-y border-[#1F2732] font-mono text-center">
                <div className="bg-[#151B23] p-2 rounded border border-[#29313C]">
                  <div className="text-[9px] text-[#667180] uppercase">VOLTAGE</div>
                  <div className="text-xs font-bold text-[#F4F7FB]">120 V</div>
                </div>
                <div className="bg-[#151B23] p-2 rounded border border-[#29313C]">
                  <div className="text-[9px] text-[#667180] uppercase">AMPS</div>
                  <div className="text-xs font-bold text-[#F4F7FB]">15 A</div>
                </div>
                <div className="bg-[#151B23] p-2 rounded border border-[#29313C]">
                  <div className="text-[9px] text-[#667180] uppercase">SOUND</div>
                  <div className="text-xs font-bold text-[#F4F7FB]">47 dBA</div>
                </div>
              </div>

              {/* Verified Sources & Status */}
              <div className="space-y-2 text-xs font-mono">
                <div className="flex items-center justify-between text-[#98A3B3]">
                  <span>SOURCE</span>
                  <span className="text-[#62E6A7] flex items-center gap-1 font-bold">
                    <Globe className="w-3.5 h-3.5" />
                    frigidaire.com ✓ OFFICIAL
                  </span>
                </div>
                <div className="p-2.5 rounded bg-[#0B0F14] border border-[#29313C] text-[11px] text-[#62E6A7] space-y-1">
                  <div className="flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>✓ MPN VERIFIED DETERMINISTICALLY</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>✓ ATTRIBUTES CROSS-CHECKED AGAINST PDF</span>
                  </div>
                </div>
              </div>

              {/* Live State Transition Indicator */}
              <div className="pt-2 border-t border-[#1F2732] flex items-center justify-between text-[10px] font-mono text-[#98A3B3]">
                <span className="text-[#667180]">STAGE:</span>
                <span className="font-bold text-[#4D7CFF] bg-[#2F6BFF]/10 px-2 py-0.5 rounded border border-[#2F6BFF]/30">
                  {stages[pipelineState]}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Signature Evidence Graph */}
        <EvidenceGraph />

        {/* Editorial "Why CATALYST" 3-Block Section */}
        <div className="space-y-6">
          <div className="text-xs font-mono font-bold tracking-widest text-[#4D7CFF] uppercase">
            OPERATING PRINCIPLES
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 font-mono">
            {/* Block 01 */}
            <div className="bg-[#11161D] border border-[#29313C] rounded-xl p-8 space-y-4 hover:border-[#2F6BFF] transition-all">
              <div className="text-5xl font-extrabold text-[#29313C] tracking-tighter">01</div>
              <h3 className="text-lg font-bold text-[#F4F7FB]">IDENTIFY</h3>
              <p className="text-xs text-[#98A3B3] leading-relaxed">
                Deterministic resolution of manufacturer, brand aliases, and exact MPN collisions before any enrichment occurs.
              </p>
            </div>

            {/* Block 02 */}
            <div className="bg-[#11161D] border border-[#29313C] rounded-xl p-8 space-y-4 hover:border-[#62E6A7] transition-all">
              <div className="text-5xl font-extrabold text-[#29313C] tracking-tighter">02</div>
              <h3 className="text-lg font-bold text-[#F4F7FB]">VERIFY</h3>
              <p className="text-xs text-[#98A3B3] leading-relaxed">
                Automated multi-source consensus. Every technical fact is cross-checked against primary manufacturer documentation.
              </p>
            </div>

            {/* Block 03 */}
            <div className="bg-[#11161D] border border-[#29313C] rounded-xl p-8 space-y-4 hover:border-[#4D7CFF] transition-all">
              <div className="text-5xl font-extrabold text-[#29313C] tracking-tighter">03</div>
              <h3 className="text-lg font-bold text-[#F4F7FB]">DELIVER</h3>
              <p className="text-xs text-[#98A3B3] leading-relaxed">
                Guaranteed 252-column schema conformance with normalized units (V, A, dBA, UOM) and synthesized commerce copy.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Technical Footer */}
      <footer className="px-8 py-5 border-t border-[#29313C] bg-[#11161D] text-xs font-mono text-[#667180] flex flex-col sm:flex-row items-center justify-between gap-2">
        <div>CATALYST INDUSTRIAL PRODUCT INTELLIGENCE OPERATING SYSTEM</div>
        <div>FASTAPI :8000 • 252-COLUMN UNILOG STANDARD</div>
      </footer>
    </div>
  );
}
