import React from "react";
import { motion } from "framer-motion";

interface RiskGaugeProps {
  score: number; // 0-100
  riskLevel: string;
}

const clamp = (v: number, min: number, max: number) =>
  Math.max(min, Math.min(max, v));

const scoreColor = (score: number): string => {
  if (score <= 30) return "#43E97B"; // green / accent
  if (score <= 60) return "#FFB347"; // yellow / warning
  return "#FF6584"; // red / secondary
};

const RiskGauge: React.FC<RiskGaugeProps> = ({ score, riskLevel }) => {
  const clamped = clamp(score, 0, 100);
  const color = scoreColor(clamped);

  // SVG semi-circle parameters
  const cx = 150;
  const cy = 140;
  const r = 110;
  const strokeWidth = 20;

  // Arc runs from 180deg (left) to 0deg (right) — a half circle
  const startAngle = 180;
  const endAngle = 0;
  const totalSweep = 180; // degrees

  const degToRad = (deg: number) => (deg * Math.PI) / 180;

  const polarToXY = (angleDeg: number) => ({
    x: cx + r * Math.cos(degToRad(angleDeg)),
    y: cy - r * Math.sin(degToRad(angleDeg)),
  });

  // Background arc (full semi-circle)
  const bgStart = polarToXY(startAngle);
  const bgEnd = polarToXY(endAngle);
  const bgPath = `M ${bgStart.x} ${bgStart.y} A ${r} ${r} 0 0 1 ${bgEnd.x} ${bgEnd.y}`;

  // Filled arc based on score
  const fillAngle = startAngle - (clamped / 100) * totalSweep;
  const fillEnd = polarToXY(fillAngle);
  const largeArc = clamped > 50 ? 1 : 0;
  const fillPath = `M ${bgStart.x} ${bgStart.y} A ${r} ${r} 0 ${largeArc} 1 ${fillEnd.x} ${fillEnd.y}`;

  // Needle tip position
  const needleAngle = startAngle - (clamped / 100) * totalSweep;
  const needleTip = polarToXY(needleAngle);

  // Gradient stop positions for the background track
  const gradientStops = [
    { offset: "0%", color: "#43E97B" },
    { offset: "33%", color: "#43E97B" },
    { offset: "50%", color: "#FFB347" },
    { offset: "67%", color: "#FFB347" },
    { offset: "100%", color: "#FF6584" },
  ];

  return (
    <div className="flex flex-col items-center">
      <svg viewBox="0 0 300 170" className="w-full max-w-[320px]">
        <defs>
          <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            {gradientStops.map((s) => (
              <stop key={s.offset} offset={s.offset} stopColor={s.color} />
            ))}
          </linearGradient>
        </defs>

        {/* Background track */}
        <path
          d={bgPath}
          fill="none"
          stroke="#E2E8F0"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />

        {/* Filled arc */}
        <motion.path
          d={fillPath}
          fill="none"
          stroke="url(#gaugeGrad)"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1.2, ease: "easeOut" }}
        />

        {/* Needle */}
        <motion.line
          x1={cx}
          y1={cy}
          x2={needleTip.x}
          y2={needleTip.y}
          stroke={color}
          strokeWidth={3}
          strokeLinecap="round"
          initial={{ x2: bgStart.x, y2: bgStart.y }}
          animate={{ x2: needleTip.x, y2: needleTip.y }}
          transition={{ duration: 1.2, ease: "easeOut" }}
        />

        {/* Center dot */}
        <circle cx={cx} cy={cy} r={6} fill={color} />

        {/* Score text */}
        <motion.text
          x={cx}
          y={cy - 25}
          textAnchor="middle"
          className="text-3xl font-bold"
          fill="#1E293B"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          {clamped}
        </motion.text>

        {/* Labels at ends */}
        <text x={bgStart.x - 5} y={cy + 20} textAnchor="middle" fontSize={12} fill="#94A3B8">
          0
        </text>
        <text x={bgEnd.x + 5} y={cy + 20} textAnchor="middle" fontSize={12} fill="#94A3B8">
          100
        </text>
      </svg>

      {/* Risk level label */}
      <motion.span
        className="mt-1 inline-block rounded-full px-4 py-1 text-sm font-semibold text-white"
        style={{ backgroundColor: color }}
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.8, type: "spring", stiffness: 260, damping: 20 }}
      >
        {riskLevel}
      </motion.span>
    </div>
  );
};

export default RiskGauge;
