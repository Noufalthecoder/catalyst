'use client';

import React, { Suspense, useRef, useState, useEffect, useCallback, useMemo } from 'react';
import dynamic from 'next/dynamic';
import Link from 'next/link';
import { CatalystLogo } from '@/components/CatalystLogo';

// Dynamically import the 3D canvas to avoid SSR issues
const PipelineCanvas = dynamic(() => import('./PipelineCanvas'), {
  ssr: false,
  loading: () => (
    <div className="flex-1 flex items-center justify-center bg-[#050810]">
      <div className="text-center space-y-4 font-mono">
        <div className="w-12 h-12 border-2 border-[#2F6BFF] border-t-transparent rounded-full animate-spin mx-auto" />
        <div className="text-xs text-[#667180]">INITIALIZING 3D INTELLIGENCE ENGINE...</div>
      </div>
    </div>
  ),
});

const STAGES = [
  {
    id: 'raw',
    num: '01',
    title: 'RAW INPUT',
    subtitle: 'Supplier Catalog Ingestion',
    metric: '1,000 ROWS',
    status: 'INGESTED',
    color: '#4D7CFF',
    accent: '#2F6BFF',
    desc: 'Fragmented supplier CSVs and XLSXs with inconsistent MPNs, ambiguous descriptions, and missing manufacturer data enter CATALYST.',
    details: [
      { label: 'Format', value: 'CSV / XLSX' },
      { label: 'Total Rows', value: '1,000' },
      { label: 'Columns', value: '12 Raw Fields' },
      { label: 'Issues', value: 'Missing MPNs, Brand Conflicts, Duplicates' },
    ],
  },
  {
    id: 'identity',
    num: '02',
    title: 'IDENTITY ENGINE',
    subtitle: 'Resolve What The Product Is',
    metric: '99.9% MPN RESOLUTION',
    status: 'VERIFIED',
    color: '#4D7CFF',
    accent: '#2F6BFF',
    desc: 'Deterministic MPN normalization, manufacturer alias resolution, and brand disambiguation. No LLM hallucination — rule-based identity engine.',
    details: [
      { label: 'MPN Resolution', value: '99.9%' },
      { label: 'Brand Aliases', value: '47 Resolved' },
      { label: 'Method', value: 'Deterministic Rules' },
      { label: 'Conflicts', value: '0.1% Manual Review' },
    ],
  },
  {
    id: 'taxonomy',
    num: '03',
    title: 'TAXONOMY ENGINE',
    subtitle: 'Industrial Classification',
    metric: 'FINE CLASS',
    status: 'CLASSIFIED',
    color: '#8B5CF6',
    accent: '#7C3AED',
    desc: 'Products are classified into Unilog-compliant industrial taxonomy hierarchies: Department → Section → Class → Product Type.',
    details: [
      { label: 'Departments', value: '24 Industrial' },
      { label: 'Product Types', value: '156 Categories' },
      { label: 'Accuracy', value: '97.3%' },
      { label: 'Schema', value: 'Unilog Fine Class' },
    ],
  },
  {
    id: 'sources',
    num: '04',
    title: 'SOURCE INTELLIGENCE',
    subtitle: 'Find Authoritative Evidence',
    metric: '753 OFFICIAL SOURCES',
    status: 'CRAWLED',
    color: '#06B6D4',
    accent: '#0891B2',
    desc: 'Live web crawling against authoritative manufacturer domains. Primary tier sources receive 0.40 consensus weight. Unverified sources: 0.00.',
    details: [
      { label: 'Official Sources', value: '753' },
      { label: 'Coverage', value: '75.3%' },
      { label: 'MPN Match Rate', value: '74.7%' },
      { label: 'Cached Specs', value: '1,460 Documents' },
    ],
  },
  {
    id: 'attributes',
    num: '05',
    title: 'ATTRIBUTE INTELLIGENCE',
    subtitle: 'Extract Structured Product Facts',
    metric: '4,812 VERIFIED',
    status: 'EXTRACTED',
    color: '#62E6A7',
    accent: '#10B981',
    desc: 'Verbatim fact extraction from manufacturer spec sheets. Attributes are matched with UOM-aware type checkers. Zero inference without source evidence.',
    details: [
      { label: 'Verified Attributes', value: '4,812' },
      { label: 'Tracked Dimensions', value: '5,000' },
      { label: 'Fill Rate', value: '96.2%' },
      { label: 'Hallucination Rate', value: '0%' },
    ],
  },
  {
    id: 'normalization',
    num: '06',
    title: 'NORMALIZATION',
    subtitle: 'Standardize Every Value',
    metric: 'UOM STANDARD',
    status: 'NORMALIZED',
    color: '#F59E0B',
    accent: '#D97706',
    desc: 'Unit-of-measure normalization, value canonicalization, and format standardization across all extracted attributes.',
    details: [
      { label: '24 inches →', value: '24 in' },
      { label: '120VAC →', value: '120 VAC' },
      { label: '20V MAX →', value: '20 V MAX' },
      { label: 'Coverage', value: '100% Fields' },
    ],
  },
  {
    id: 'validation',
    num: '07',
    title: 'VALIDATION ENGINE',
    subtitle: 'Verify Every Critical Fact',
    metric: '84% HIGH CONFIDENCE',
    status: 'VALIDATED',
    color: '#62E6A7',
    accent: '#10B981',
    desc: 'Multi-rule validation pipeline: source consensus, UOM type checkers, attribute range validators, and schema conformance checks.',
    details: [
      { label: 'High Confidence', value: '84.0%' },
      { label: 'Source Match', value: '75.3%' },
      { label: 'UOM Valid', value: '100%' },
      { label: 'Schema Valid', value: '100%' },
    ],
  },
  {
    id: 'review',
    num: '08',
    title: 'HUMAN REVIEW',
    subtitle: 'Automation Handles Volume. Humans Handle Ambiguity.',
    metric: '137 ITEMS',
    status: 'IN REVIEW',
    color: '#F5B84B',
    accent: '#D97706',
    desc: 'Ambiguous products are routed to a structured human review workflow. Operators resolve attribute conflicts with full source evidence context.',
    details: [
      { label: 'Review Queue', value: '137 Items' },
      { label: 'Categories', value: 'Attribute, Identity, Source' },
      { label: 'Avg Resolution', value: '< 2 min/item' },
      { label: 'Decision Types', value: 'Accept, Keep, Override, Unknown' },
    ],
  },
  {
    id: 'canonical',
    num: '09',
    title: 'CANONICAL PRODUCT',
    subtitle: 'Trusted Product Intelligence Card',
    metric: '98.4% CONFIDENCE',
    status: 'TRUSTED',
    color: '#62E6A7',
    accent: '#10B981',
    desc: 'A single canonical product intelligence record synthesizing verified identity, taxonomy, sourced attributes, and generated commerce descriptions.',
    details: [
      { label: 'Example MPN', value: 'PDSH4816AF' },
      { label: 'Brand', value: 'FRIGIDAIRE®' },
      { label: 'Trust Score', value: '98.4%' },
      { label: 'Source', value: 'frigidaire.com ✓ OFFICIAL' },
    ],
  },
  {
    id: 'delivery',
    num: '10',
    title: 'DELIVERY',
    subtitle: '252-Column Enterprise Schema',
    metric: '252 FIELDS',
    status: 'DELIVERED',
    color: '#2F6BFF',
    accent: '#1D4ED8',
    desc: '1,000 products exported as a fully Unilog-compliant 252-column CSV/JSONL. Zero schema corruptions. Commerce-ready for ERP, PIM, and e-commerce ingestion.',
    details: [
      { label: 'Schema Columns', value: '252' },
      { label: 'Total Records', value: '1,000' },
      { label: 'Compliance', value: '100%' },
      { label: 'Formats', value: 'CSV, JSONL, PIM, ERP' },
    ],
  },
];

export default function ArchitecturePage() {
  const [selectedStage, setSelectedStage] = useState<number | null>(null);
  const [isAutoRun, setIsAutoRun] = useState(false);
  const [activeStage, setActiveStage] = useState<number>(-1);
  const [showWow, setShowWow] = useState(false);
  const autoRunRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const runPipeline = useCallback(() => {
    setIsAutoRun(true);
    setActiveStage(0);
    setShowWow(false);
    STAGES.forEach((_, i) => {
      autoRunRef.current = setTimeout(() => {
        setActiveStage(i);
        if (i === STAGES.length - 1) {
          setTimeout(() => {
            setShowWow(true);
            setIsAutoRun(false);
            setActiveStage(-1);
          }, 2000);
        }
      }, i * 1800);
    });
  }, []);

  const resetAll = useCallback(() => {
    if (autoRunRef.current) clearTimeout(autoRunRef.current);
    setIsAutoRun(false);
    setActiveStage(-1);
    setSelectedStage(null);
    setShowWow(false);
  }, []);

  useEffect(() => {
    return () => {
      if (autoRunRef.current) clearTimeout(autoRunRef.current);
    };
  }, []);

  const selectedStageData = selectedStage !== null ? STAGES[selectedStage] : null;

  return (
    <div className="min-h-screen bg-[#050810] text-[#F4F7FB] flex flex-col overflow-hidden font-mono select-none">
      {/* TOP HUD */}
      <header className="z-30 shrink-0 border-b border-[#29313C]/60 bg-[#050810]/90 backdrop-blur px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <CatalystLogo size={22} />
          <div>
            <div className="text-xs font-extrabold tracking-widest text-[#F4F7FB]">CATALYST</div>
            <div className="text-[9px] tracking-widest text-[#667180]">INDUSTRIAL INTELLIGENCE</div>
          </div>
          <div className="hidden md:flex items-center gap-1 ml-4 pl-4 border-l border-[#29313C]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#62E6A7] animate-pulse" />
            <span className="text-[10px] text-[#62E6A7] font-bold">INTELLIGENCE ENGINE ONLINE</span>
          </div>
        </div>

        {/* Center Title */}
        <div className="hidden md:block text-center">
          <div className="text-xs font-bold text-[#F4F7FB] tracking-widest">INTELLIGENCE PIPELINE ARCHITECTURE</div>
          <div className="text-[9px] text-[#667180]">RAW DATA → VERIFIED PRODUCT INTELLIGENCE</div>
        </div>

        {/* Telemetry Strip */}
        <div className="hidden lg:flex items-center gap-5 text-[10px]">
          {[
            { label: 'PRODUCTS', value: '1,000' },
            { label: 'HIGH CONF', value: '84%' },
            { label: 'VERIFIED ATTR', value: '4,812' },
            { label: 'REVIEW', value: '137' },
            { label: 'FIELDS', value: '252' },
          ].map((t) => (
            <div key={t.label} className="text-center">
              <div className="text-[#4D7CFF] font-bold">{t.value}</div>
              <div className="text-[#667180]">{t.label}</div>
            </div>
          ))}
          <div className="pl-4 border-l border-[#29313C] text-[#62E6A7] font-bold">● OPERATIONAL</div>
        </div>
      </header>

      {/* MAIN SPLIT: 3D Canvas Left, Stage List Right */}
      <div className="flex-1 flex overflow-hidden">
        {/* 3D Canvas */}
        <div className="flex-1 relative overflow-hidden">
          <PipelineCanvas
            stages={STAGES}
            activeStage={activeStage}
            selectedStage={selectedStage}
            onSelectStage={setSelectedStage}
            showWow={showWow}
          />

          {/* Control Bar Overlay */}
          <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-3 z-20 bg-[#11161D]/80 border border-[#29313C] rounded-lg px-4 py-2.5 backdrop-blur-md shadow-xl">
            <button
              onClick={runPipeline}
              disabled={isAutoRun}
              className="px-4 py-1.5 bg-[#2F6BFF] hover:bg-[#4D7CFF] text-white text-xs font-bold rounded shadow-[0_0_12px_rgba(47,107,255,0.4)] disabled:opacity-40 transition-all"
            >
              ▶ PLAY PIPELINE
            </button>
            <button
              onClick={resetAll}
              className="px-3 py-1.5 bg-[#151B23] hover:bg-[#1B222C] text-[#98A3B3] text-xs font-bold rounded border border-[#29313C] transition-all"
            >
              ↺ RESET
            </button>
            <div className="w-px h-4 bg-[#29313C]" />
            <span className="text-[10px] text-[#667180]">Click stage to inspect · Drag to orbit</span>
          </div>
        </div>

        {/* Right Stage List Panel */}
        <aside className="w-72 bg-[#0B0F14] border-l border-[#29313C]/60 flex flex-col overflow-hidden shrink-0">
          <div className="px-4 py-3 border-b border-[#29313C]/60 bg-[#11161D]/60">
            <div className="text-[10px] font-bold text-[#4D7CFF] tracking-widest uppercase">10 INTELLIGENCE STAGES</div>
            <div className="text-[11px] text-[#667180] mt-0.5">Select to inspect architecture</div>
          </div>
          <div className="flex-1 overflow-y-auto divide-y divide-[#1F2732]/60">
            {STAGES.map((stage, i) => {
              const isActive = activeStage === i;
              const isSelected = selectedStage === i;
              return (
                <button
                  key={stage.id}
                  onClick={() => setSelectedStage(isSelected ? null : i)}
                  className={`w-full text-left px-4 py-3 transition-all group ${
                    isSelected
                      ? 'bg-[#151B23] border-l-2'
                      : isActive
                      ? 'bg-[#11161D]'
                      : 'hover:bg-[#0D1117]'
                  }`}
                  style={{ borderLeftColor: isSelected ? stage.color : 'transparent' }}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span
                      className="text-[10px] font-bold"
                      style={{ color: isActive || isSelected ? stage.color : '#667180' }}
                    >
                      {stage.num} / {stage.title}
                    </span>
                    <span
                      className="text-[9px] px-1.5 py-0.5 rounded font-bold"
                      style={{
                        backgroundColor: `${stage.color}15`,
                        color: stage.color,
                        border: `1px solid ${stage.color}30`,
                      }}
                    >
                      {stage.status}
                    </span>
                  </div>
                  <div className="text-[11px] text-[#98A3B3] group-hover:text-[#F4F7FB] transition-colors truncate">
                    {stage.subtitle}
                  </div>
                  <div className="text-[10px] font-bold mt-1" style={{ color: stage.color }}>
                    {stage.metric}
                  </div>

                  {isSelected && (
                    <div className="mt-3 space-y-2 text-[10px]">
                      <p className="text-[#98A3B3] leading-relaxed">{stage.desc}</p>
                      <div className="space-y-1 pt-2 border-t border-[#1F2732]">
                        {stage.details.map((d) => (
                          <div key={d.label} className="flex justify-between">
                            <span className="text-[#667180]">{d.label}</span>
                            <span className="text-[#F4F7FB] font-bold">{d.value}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </button>
              );
            })}
          </div>

          {/* Nav Links */}
          <div className="p-4 border-t border-[#29313C]/60 space-y-2">
            <Link
              href="/dashboard"
              className="block w-full text-center px-3 py-2 bg-[#2F6BFF] hover:bg-[#4D7CFF] text-white text-xs font-bold rounded shadow-[0_0_10px_rgba(47,107,255,0.3)] transition-all"
            >
              → LAUNCH COMMAND CENTER
            </Link>
            <Link
              href="/"
              className="block w-full text-center px-3 py-2 bg-[#151B23] hover:bg-[#1B222C] text-[#98A3B3] text-xs font-bold rounded border border-[#29313C] transition-all"
            >
              ← BACK TO HOME
            </Link>
          </div>
        </aside>
      </div>

      {/* WOW MOMENT OVERLAY */}
      {showWow && (
        <div className="absolute inset-0 z-40 flex items-center justify-center pointer-events-none">
          <div className="text-center space-y-4 animate-in fade-in duration-1000">
            <div className="text-[#667180] text-xs tracking-widest uppercase font-bold">FROM FRAGMENTED DATA</div>
            <div className="text-5xl font-extrabold text-[#F4F7FB] tracking-tight">
              TO <span className="text-[#62E6A7] drop-shadow-[0_0_30px_rgba(98,230,167,0.8)]">TRUSTED INTELLIGENCE</span>
            </div>
            <div className="flex items-center justify-center gap-3 mt-4">
              {['1,000 PRODUCTS', '4,812 ATTRIBUTES', '84% CONFIDENCE', '252 FIELDS'].map((m) => (
                <span key={m} className="px-3 py-1 bg-[#151B23] border border-[#29313C] rounded text-xs font-bold text-[#4D7CFF]">
                  {m}
                </span>
              ))}
            </div>
            <div className="mt-6">
              <CatalystLogo size={48} className="mx-auto" />
              <div className="text-2xl font-extrabold mt-3 tracking-widest text-[#F4F7FB]">CATALYST</div>
              <div className="text-xs text-[#667180]">Industrial Product Intelligence Engine</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
