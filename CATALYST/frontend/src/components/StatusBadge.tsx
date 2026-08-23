import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Clock, HelpCircle, ShieldCheck } from 'lucide-react';

interface StatusBadgeProps {
  status: string;
  className?: string;
  size?: 'sm' | 'md';
}

export function StatusBadge({ status, className = '', size = 'sm' }: StatusBadgeProps) {
  const norm = (status || 'UNKNOWN').toUpperCase();

  let bg = 'bg-[#151B23] text-[#98A3B3] border-[#29313C]';
  let icon = <HelpCircle className={size === 'sm' ? 'w-3 h-3' : 'w-4 h-4'} />;
  let label = status;

  if (norm === 'VERIFIED' || norm === 'AUTO_APPROVED' || norm === 'SUCCESS' || norm === 'PRIMARY') {
    bg = 'bg-[#62E6A7]/10 text-[#62E6A7] border-[#62E6A7]/30 shadow-[0_0_10px_rgba(98,230,167,0.1)]';
    icon = <CheckCircle2 className={size === 'sm' ? 'w-3 h-3 text-[#62E6A7]' : 'w-4 h-4 text-[#62E6A7]'} />;
    label = norm === 'PRIMARY' ? 'Official Tier 1' : norm === 'AUTO_APPROVED' ? 'Auto Approved' : 'Verified';
  } else if (norm === 'NEEDS_REVIEW' || norm === 'PROBABLE' || norm === 'SECONDARY' || norm === 'WARNING') {
    bg = 'bg-[#F5B84B]/10 text-[#F5B84B] border-[#F5B84B]/30';
    icon = <AlertTriangle className={size === 'sm' ? 'w-3 h-3 text-[#F5B84B]' : 'w-4 h-4 text-[#F5B84B]'} />;
    label = norm === 'SECONDARY' ? 'Secondary' : norm === 'PROBABLE' ? 'Probable' : 'Needs Review';
  } else if (norm === 'BLOCKED' || norm === 'FAILED' || norm === 'INVALID' || norm === 'UNTRUSTED') {
    bg = 'bg-[#FF667A]/10 text-[#FF667A] border-[#FF667A]/30';
    icon = <XCircle className={size === 'sm' ? 'w-3 h-3 text-[#FF667A]' : 'w-4 h-4 text-[#FF667A]'} />;
    label = norm === 'INVALID' ? 'Format Rejected' : norm === 'BLOCKED' ? 'Blocked' : 'Failed';
  } else if (norm === 'PROCESSING') {
    bg = 'bg-[#2F6BFF]/15 text-[#4D7CFF] border-[#2F6BFF]/40 animate-pulse';
    icon = <Clock className={size === 'sm' ? 'w-3 h-3 text-[#4D7CFF]' : 'w-4 h-4 text-[#4D7CFF]'} />;
    label = 'Processing';
  } else if (norm === 'CONFLICTED') {
    bg = 'bg-[#FF667A]/15 text-[#FF667A] border-[#FF667A]/40';
    icon = <AlertTriangle className={size === 'sm' ? 'w-3 h-3 text-[#FF667A]' : 'w-4 h-4 text-[#FF667A]'} />;
    label = 'Conflicted';
  }

  const px = size === 'sm' ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-xs';

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-mono font-medium border rounded ${bg} ${px} ${className}`}
    >
      {icon}
      <span>{label}</span>
    </span>
  );
}
