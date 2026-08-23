'use client';

import React from 'react';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';

interface AppShellProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
}

export function AppShell({ children, title, subtitle }: AppShellProps) {
  return (
    <div className="min-h-screen bg-[#0B0F14] bg-blueprint-grid text-[#F4F7FB] flex">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 bg-radial-glow">
        <Topbar title={title} subtitle={subtitle} />
        <main className="flex-1 p-8 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
