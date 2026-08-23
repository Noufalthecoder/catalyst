import React from 'react';

interface CatalystLogoProps {
  size?: number;
  className?: string;
}

export function CatalystLogo({ size = 28, className = '' }: CatalystLogoProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Top Transformation Segment (Electric Blue) */}
      <path
        d="M26 8H12C8.68629 8 6 10.6863 6 14V15C6 15.5523 6.44772 16 7 16H18C19.1046 16 20 15.1046 20 14V12H26C26.5523 12 27 11.5523 27 11V9C27 8.44772 26.5523 8 26 8Z"
        fill="#2F6BFF"
      />
      {/* Bottom Offset Evidence Segment (Evidence Green) */}
      <path
        d="M26 24H12C8.68629 24 6 21.3137 6 18V17C6 16.4477 6.44772 16 7 16H18C19.1046 16 20 16.8954 20 18V20H26C26.5523 20 27 20.4477 27 21V23C27 23.5523 26.5523 24 26 24Z"
        fill="#62E6A7"
      />
      {/* Center Precision Target Node */}
      <circle cx="13" cy="16" r="2" fill="#F4F7FB" />
    </svg>
  );
}
