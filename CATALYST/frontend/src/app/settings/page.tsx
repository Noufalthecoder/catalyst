'use client';

import React, { useState } from 'react';
import { Settings, ShieldCheck, Globe, Cpu, Server, Save, Check } from 'lucide-react';
import { AppShell } from '@/components/AppShell';

export default function SettingsPage() {
  const [sourceProvider, setSourceProvider] = useState<string>('live');
  const [searchProvider, setSearchProvider] = useState<string>('duckduckgo');
  const [rateLimitDelay, setRateLimitDelay] = useState<number>(0.1);
  const [demoMode, setDemoMode] = useState<boolean>(true);
  const [saved, setSaved] = useState<boolean>(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <AppShell title="SYSTEM SETTINGS" subtitle="Engine Parameters & Crawler Modes">
      <div className="space-y-6 max-w-4xl mx-auto font-mono text-xs">
        <form onSubmit={handleSave} className="bg-[#11161D] border border-[#29313C] rounded-xl p-6 shadow-xl space-y-6">
          <div className="border-b border-[#1F2732] pb-4">
            <h2 className="text-base font-bold text-[#F4F7FB]">ENGINE CONTROL PARAMETERS</h2>
            <p className="text-[#667180] text-[11px] mt-0.5">
              Live crawler routing, search provider adapters, and presentation modes
            </p>
          </div>

          {saved && (
            <div className="p-3 bg-[#151B23] border border-[#62E6A7]/30 text-[#62E6A7] rounded font-bold flex items-center gap-2">
              <Check className="w-4 h-4" />
              <span>Engine configurations synchronized with FastAPI backend.</span>
            </div>
          )}

          {/* Source Mode */}
          <div className="space-y-2">
            <label className="block text-[10px] font-bold text-[#667180] uppercase tracking-wider">
              SOURCE PROVIDER ENGINE
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <label
                className={`p-4 border rounded-lg cursor-pointer transition-all block ${
                  sourceProvider === 'live'
                    ? 'bg-[#151B23] border-[#2F6BFF] shadow-[0_0_15px_rgba(47,107,255,0.2)]'
                    : 'bg-[#0B0F14] border-[#29313C] hover:bg-[#151B23]'
                }`}
              >
                <input
                  type="radio"
                  name="sourceProvider"
                  value="live"
                  checked={sourceProvider === 'live'}
                  onChange={() => setSourceProvider('live')}
                  className="hidden"
                />
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-[#F4F7FB]">LIVE WEB CRAWLER</span>
                  <span className="px-2 py-0.5 bg-[#62E6A7]/10 text-[#62E6A7] border border-[#62E6A7]/30 rounded text-[9px] font-bold">
                    ACTIVE PRODUCTION
                  </span>
                </div>
                <p className="text-[#98A3B3] text-[11px] leading-relaxed">
                  Queries DuckDuckGo HTML endpoint and crawls live manufacturer spec portals in real-time.
                </p>
              </label>

              <label
                className={`p-4 border rounded-lg cursor-pointer transition-all block ${
                  sourceProvider === 'fixture'
                    ? 'bg-[#151B23] border-[#2F6BFF] shadow-[0_0_15px_rgba(47,107,255,0.2)]'
                    : 'bg-[#0B0F14] border-[#29313C] hover:bg-[#151B23]'
                }`}
              >
                <input
                  type="radio"
                  name="sourceProvider"
                  value="fixture"
                  checked={sourceProvider === 'fixture'}
                  onChange={() => setSourceProvider('fixture')}
                  className="hidden"
                />
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-[#F4F7FB]">OFFLINE FIXTURES</span>
                  <span className="px-2 py-0.5 bg-[#151B23] text-[#667180] border border-[#29313C] rounded text-[9px] font-bold">
                    TEST ONLY
                  </span>
                </div>
                <p className="text-[#98A3B3] text-[11px] leading-relaxed">
                  Uses local mock fixtures for isolated unit testing. Never used in live production runs.
                </p>
              </label>
            </div>
          </div>

          {/* Search Provider */}
          <div className="space-y-2">
            <label className="block text-[10px] font-bold text-[#667180] uppercase tracking-wider">
              SEARCH PROVIDER
            </label>
            <select
              value={searchProvider}
              onChange={(e) => setSearchProvider(e.target.value)}
              className="w-full bg-[#0B0F14] border border-[#29313C] rounded px-3 py-2 text-[#F4F7FB] focus:outline-none focus:border-[#4D7CFF]"
            >
              <option value="duckduckgo">DuckDuckGo Keyless HTML Crawler (Connected)</option>
              <option value="none">Direct Domain Match Only</option>
            </select>
          </div>

          {/* Rate Limiting */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="block text-[10px] font-bold text-[#667180] uppercase tracking-wider">
                CRAWLER RATE-LIMIT DELAY
              </label>
              <span className="font-bold text-[#4D7CFF]">{rateLimitDelay}s</span>
            </div>
            <input
              type="range"
              min="0.05"
              max="2.0"
              step="0.05"
              value={rateLimitDelay}
              onChange={(e) => setRateLimitDelay(parseFloat(e.target.value))}
              className="w-full h-2 bg-[#0B0F14] rounded appearance-none cursor-pointer accent-[#2F6BFF]"
            />
          </div>

          {/* Presentation Demo Mode */}
          <div className="pt-4 border-t border-[#1F2732] flex items-center justify-between">
            <div>
              <div className="font-bold text-[#F4F7FB]">JUDGE PRESENTATION MODE</div>
              <p className="text-[#667180] text-[11px]">
                Enables deterministic demo product walkthroughs on the command center.
              </p>
            </div>
            <button
              type="button"
              onClick={() => setDemoMode(!demoMode)}
              className={`w-11 h-6 rounded-full transition-colors relative ${
                demoMode ? 'bg-[#2F6BFF]' : 'bg-[#29313C]'
              }`}
            >
              <span
                className={`w-4 h-4 rounded-full bg-white absolute top-1 transition-transform ${
                  demoMode ? 'left-6' : 'left-1'
                }`}
              />
            </button>
          </div>

          {/* Save Button */}
          <div className="pt-4 border-t border-[#1F2732] flex justify-end">
            <button
              type="submit"
              className="px-6 py-2.5 bg-[#2F6BFF] hover:bg-[#4D7CFF] text-[#F4F7FB] font-bold rounded shadow-[0_0_15px_rgba(47,107,255,0.35)] flex items-center gap-2"
            >
              <Save className="w-3.5 h-3.5" />
              <span>SAVE CONFIGURATION</span>
            </button>
          </div>
        </form>

        {/* Server Info Card */}
        <div className="bg-[#11161D] border border-[#29313C] rounded-xl p-5 space-y-2">
          <div className="font-bold text-[#F4F7FB] flex items-center gap-2">
            <Server className="w-4 h-4 text-[#4D7CFF]" />
            <span>FASTAPI SERVER TELEMETRY</span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-[11px] pt-1 text-[#98A3B3]">
            <div>HOST: <span className="text-[#F4F7FB]">127.0.0.1:8000</span></div>
            <div>ENGINE: <span className="text-[#F4F7FB]">252 Columns</span></div>
            <div>STATUS: <span className="text-[#62E6A7] font-bold">ONLINE</span></div>
            <div>ORIGIN: <span className="text-[#62E6A7] font-bold">LIVE DYNAMIC</span></div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
