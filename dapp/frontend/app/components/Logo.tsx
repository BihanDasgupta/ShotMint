'use client';

export default function Logo({ size = 48 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="inline-block"
    >
      {/* Gold SM text without circle */}
      <text
        x="50"
        y="70"
        fontSize="60"
        fill="url(#goldGradient)"
        textAnchor="middle"
        fontWeight="bold"
        fontFamily="Arial, sans-serif"
        letterSpacing="-2"
      >
        SM
      </text>
      
      <defs>
        <linearGradient id="goldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#fbbf24" />
          <stop offset="50%" stopColor="#f59e0b" />
          <stop offset="100%" stopColor="#d97706" />
        </linearGradient>
      </defs>
    </svg>
  );
}

