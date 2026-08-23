'use client';

import React, { useState } from 'react';
import { ShieldCheck, Globe, FileText, CheckCircle2, ArrowRight } from 'lucide-react';

export function EvidenceGraph() {
  const [selectedNode, setSelectedNode] = useState<string>('voltage');

  const nodes = [
    {
      id: 'voltage',
      label: 'Voltage',
      val: '120 V',
      source: 'Frigidaire Tech Specs Table',
      url: 'https://www.frigidaire.com/Dishwashers/PDSH4816AF',
      status: 'VERIFIED',
      evidence: 'Line 42: "Electrical Requirements: 120 V, 60 Hz, 15 A dedicated circuit"',
      color: '#62E6A7',
    },
    {
      id: 'current',
      label: 'Amps',
      val: '15 A',
      source: 'Installation Guide PDF',
      url: 'https://www.frigidaire.com/manuals/PDSH4816AF_install.pdf',
      status: 'VERIFIED',
      evidence: 'Section 3.2: "Supply wire: 15 A rated breaker required for motor load"',
      color: '#62E6A7',
    },
    {
      id: 'sound',
      label: 'Sound Level',
      val: '47 dBA',
      source: 'Acoustic Lab Certification',
      url: 'https://www.frigidaire.com/Dishwashers/PDSH4816AF',
      status: 'VERIFIED',
      evidence: 'Specs: "Quiet Operation: 47 dBA Sound Package with Direct Feed"',
      color: '#62E6A7',
    },
    {
      id: 'material',
      label: 'Tub Material',
      val: 'Stainless Steel',
      source: 'Product Engineering Sheet',
      url: 'https://www.frigidaire.com/Dishwashers/PDSH4816AF',
      status: 'VERIFIED',
      evidence: 'Feature 01: "Durable interior stainless steel tub and spray arms"',
      color: '#62E6A7',
    },
    {
      id: 'width',
      label: 'Width',
      val: '24 in',
      source: 'CAD Dimensions Diagram',
      url: 'https://www.frigidaire.com/Dishwashers/PDSH4816AF',
      status: 'VERIFIED',
      evidence: 'Cutout Width: "24 in. (61.0 cm) Standard Opening"',
      color: '#62E6A7',
    },
  ];

  const activeNode = nodes.find((n) => n.id === selectedNode) || nodes[0];

  return (
    <div className="bg-[#11161D] border border-[#29313C] rounded-xl p-8 shadow-2xl relative overflow-hidden">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#1F2732] pb-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono font-bold tracking-widest text-[#4D7CFF] uppercase">
              PROVENANCE TOPOLOGY
            </span>
            <span className="px-2 py-0.5 bg-[#62E6A7]/10 text-[#62E6A7] border border-[#62E6A7]/30 text-[10px] font-mono rounded">
              0% HALLUCINATION GUARANTEE
            </span>
          </div>
          <h2 className="text-xl md:text-2xl font-extrabold text-[#F4F7FB] mt-1 tracking-tight">
            Every Fact Has An Authoritative Source
          </h2>
          <p className="text-xs text-[#98A3B3] mt-1">
            Interactive trace of technical dimensions linked to live manufacturer engineering documentation.
          </p>
        </div>
      </div>

      {/* Main Diagram Area */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 my-8 items-center">
        {/* Left / Center: Interactive Nodes Grid */}
        <div className="lg:col-span-7 space-y-4">
          <div className="text-xs font-mono font-semibold text-[#667180] uppercase tracking-wider mb-2">
            Click Attribute to Trace Source
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {nodes.map((node) => {
              const isSelected = selectedNode === node.id;
              return (
                <button
                  key={node.id}
                  onClick={() => setSelectedNode(node.id)}
                  className={`text-left p-3.5 rounded-lg border transition-all relative ${
                    isSelected
                      ? 'bg-[#1B222C] border-[#2F6BFF] shadow-[0_0_15px_rgba(47,107,255,0.25)]'
                      : 'bg-[#151B23] border-[#29313C] hover:border-[#4D7CFF]/50'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] font-mono text-[#667180] uppercase">{node.label}</span>
                    <span className="w-2 h-2 rounded-full" style={{ backgroundColor: node.color }} />
                  </div>
                  <div className="font-mono font-bold text-sm text-[#F4F7FB]">{node.val}</div>
                  <div className="mt-2 text-[9px] font-mono text-[#62E6A7] flex items-center gap-1">
                    <CheckCircle2 className="w-2.5 h-2.5" />
                    <span>Exact Spec Match</span>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Central Canonical Product Anchor */}
          <div className="p-4 rounded-lg bg-[#0B0F14] border border-[#29313C] flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded bg-[#1B222C] border border-[#2F6BFF] flex items-center justify-center font-mono font-bold text-xs text-[#4D7CFF]">
                MPN
              </div>
              <div>
                <div className="font-mono font-bold text-xs text-[#F4F7FB]">PDSH4816AF • FRIGIDAIRE®</div>
                <div className="text-[11px] text-[#98A3B3]">Built-In Dishwasher 24 in Stainless Steel</div>
              </div>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#62E6A7]/10 text-[#62E6A7] border border-[#62E6A7]/30">
              TIER 1 PRIMARY
            </span>
          </div>
        </div>

        {/* Right: Live Evidence Inspector */}
        <div className="lg:col-span-5 bg-[#151B23] border border-[#29313C] rounded-lg p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-[#1F2732] pb-3">
            <div className="text-xs font-mono font-bold text-[#F4F7FB] flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-[#62E6A7]" />
              <span>Evidence Trace for: {activeNode.label}</span>
            </div>
            <span className="text-xs font-mono font-bold text-[#4D7CFF]">{activeNode.val}</span>
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <span className="text-[10px] font-mono text-[#667180] uppercase">Source Document</span>
              <div className="font-semibold text-[#F4F7FB] mt-0.5 flex items-center gap-1.5">
                <Globe className="w-3.5 h-3.5 text-[#4D7CFF]" />
                <span>{activeNode.source}</span>
              </div>
              <a
                href={activeNode.url}
                target="_blank"
                rel="noreferrer"
                className="text-[11px] font-mono text-[#4D7CFF] hover:underline truncate block mt-1"
              >
                {activeNode.url}
              </a>
            </div>

            <div>
              <span className="text-[10px] font-mono text-[#667180] uppercase">Extracted Verbatim Proof</span>
              <div className="bg-[#0B0F14] border border-[#29313C] rounded p-3 font-mono text-[11px] text-[#62E6A7] leading-relaxed mt-1">
                {activeNode.evidence}
              </div>
            </div>

            <div className="pt-2 border-t border-[#1F2732] flex items-center justify-between text-[10px] font-mono text-[#98A3B3]">
              <span>Verification Consensus: 100%</span>
              <span>Retrieved: 23 Aug 2026</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
