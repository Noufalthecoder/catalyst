'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Boxes,
  Sparkles,
  ListTodo,
  Globe2,
  BarChart3,
  Download,
  Settings,
  Activity,
  Terminal,
  Layers
} from 'lucide-react';
import { CatalystLogo } from './CatalystLogo';

const NAV_ITEMS = [
  { name: 'Command Center', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Catalog Database', href: '/catalog', icon: Boxes },
  { name: 'Enrichment Engine', href: '/enrichment', icon: Sparkles },
  { name: 'Review Workspace', href: '/review', icon: ListTodo },
  { name: 'Source Intelligence', href: '/sources', icon: Globe2 },
  { name: 'Analytics & Quality', href: '/analytics', icon: BarChart3 },
  { name: 'Deliverables & Export', href: '/exports', icon: Download },
  { name: '3D Architecture', href: '/architecture', icon: Layers },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-[#11161D] border-r border-[#29313C] flex flex-col justify-between shrink-0 h-screen sticky top-0 z-30">
      {/* Brand Header */}
      <div>
        <div className="px-5 py-4 border-b border-[#29313C] flex items-center justify-between bg-[#0B0F14]/60">
          <Link href="/dashboard" className="flex items-center gap-3">
            <CatalystLogo size={26} />
            <div>
              <span className="font-mono font-extrabold text-sm tracking-wider text-[#F4F7FB] block leading-none">
                CATALYST
              </span>
              <span className="text-[9px] font-mono tracking-widest text-[#667180] uppercase block mt-1">
                OPERATING SYSTEM
              </span>
            </div>
          </Link>
          <span className="w-2 h-2 rounded-full bg-[#62E6A7] shadow-[0_0_8px_#62E6A7]" title="Engine Active" />
        </div>

        {/* Section Label */}
        <div className="px-5 pt-4 pb-2 text-[9px] font-mono font-bold tracking-widest text-[#667180] uppercase">
          NAVIGATION PROTOCOLS
        </div>

        {/* Navigation Links */}
        <nav className="px-3 space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname?.startsWith(item.href));
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded text-xs font-mono transition-all ${
                  isActive
                    ? 'bg-[#1B222C] text-[#4D7CFF] font-bold border border-[#2F6BFF]/40 shadow-[0_0_12px_rgba(47,107,255,0.15)]'
                    : 'text-[#98A3B3] hover:text-[#F4F7FB] hover:bg-[#151B23]'
                }`}
              >
                <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-[#4D7CFF]' : 'text-[#667180]'}`} />
                <span className="truncate">{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* System Status Footer */}
      <div className="p-4 border-t border-[#29313C] bg-[#0B0F14]/40 space-y-3">
        <div className="bg-[#151B23] border border-[#29313C] rounded p-3 text-xs font-mono">
          <div className="flex items-center justify-between text-[11px]">
            <span className="text-[#62E6A7] flex items-center gap-1.5 font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-[#62E6A7] animate-ping" />
              ENGINE ONLINE
            </span>
            <span className="text-[#667180]">252-COL</span>
          </div>
          <div className="text-[10px] text-[#98A3B3] mt-1.5 flex items-center justify-between">
            <span>FastAPI Backend</span>
            <span className="text-[#4D7CFF]">:8000</span>
          </div>
        </div>

        <div className="flex items-center gap-2.5 px-1">
          <div className="w-6 h-6 rounded bg-[#1B222C] border border-[#29313C] text-[#F4F7FB] flex items-center justify-center text-[10px] font-mono font-bold">
            OP
          </div>
          <div className="truncate font-mono">
            <div className="text-[11px] font-bold text-[#F4F7FB] truncate">Production Operator</div>
            <div className="text-[9px] text-[#667180] truncate">procurement@enterprise.io</div>
          </div>
        </div>
      </div>
    </aside>
  );
}
