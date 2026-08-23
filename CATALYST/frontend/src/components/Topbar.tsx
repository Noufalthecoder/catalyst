'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Search, Sparkles, Terminal, Activity, Database } from 'lucide-react';

interface TopbarProps {
  title?: string;
  subtitle?: string;
}

export function Topbar({ title, subtitle }: TopbarProps) {
  const pathname = usePathname();
  const pathParts = pathname?.split('/').filter(Boolean) || [];

  return (
    <header className="h-14 bg-[#11161D] border-b border-[#29313C] px-6 flex items-center justify-between sticky top-0 z-20">
      {/* Title & Breadcrumbs */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1.5 text-xs font-mono text-[#667180]">
          <Link href="/dashboard" className="hover:text-[#F4F7FB] transition-colors">
            CATALYST
          </Link>
          {pathParts.map((part, idx) => (
            <React.Fragment key={part}>
              <span>/</span>
              <span className={idx === pathParts.length - 1 ? 'text-[#F4F7FB] font-bold uppercase' : 'uppercase'}>
                {part}
              </span>
            </React.Fragment>
          ))}
        </div>
        {title && (
          <div className="hidden sm:flex items-center gap-2 pl-4 border-l border-[#29313C]">
            <span className="text-xs font-mono font-bold text-[#F4F7FB]">{title}</span>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center gap-3">
        {/* Quick Search */}
        <div className="relative w-64">
          <Search className="w-3.5 h-3.5 text-[#667180] absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search MPN, brand, specs..."
            className="w-full bg-[#0B0F14] border border-[#29313C] rounded pl-8 pr-3 py-1.5 text-xs font-mono text-[#F4F7FB] placeholder:text-[#667180] focus:outline-none focus:border-[#4D7CFF] transition-colors"
          />
        </div>

        {/* Start Enrichment CTA */}
        <Link
          href="/enrichment"
          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-[#2F6BFF] hover:bg-[#4D7CFF] text-[#F4F7FB] text-xs font-mono font-bold rounded shadow-[0_0_12px_rgba(47,107,255,0.3)] transition-colors"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>RUN ENRICHMENT</span>
        </Link>
      </div>
    </header>
  );
}
