import { useEffect, useState } from "react";
import { motion, useSpring, useMotionValue, animate } from "framer-motion";

const getRiskConfig = (score) => {
  if (score >= 75) return {
    label: "HIGH RISK",
    color: "#EF4444",
    glow: "rgba(239,68,68,0.6)",
    bg: "rgba(239,68,68,0.1)",
    textColor: "text-high-risk",
    borderColor: "border-high-risk/30",
    badge: "bg-high-risk/20 text-high-risk border-high-risk/40",
  };
  if (score >= 40) return {
    label: "SUSPICIOUS",
    color: "#F59E0B",
    glow: "rgba(245,158,11,0.6)",
    bg: "rgba(245,158,11,0.1)",
    textColor: "text-medium-risk",
    borderColor: "border-medium-risk/30",
    badge: "bg-medium-risk/20 text-medium-risk border-medium-risk/40",
  };
  return {
    label: "SAFE",
    color: "#10B981",
    glow: "rgba(16,185,129,0.6)",
    bg: "rgba(16,185,129,0.1)",
    textColor: "text-safe",
    borderColor: "border-safe/30",
    badge: "bg-safe/20 text-safe border-safe/40",
  };
};

export default function RiskMeter({ score = 0, size = 180, showLabel = true }) {
  const [displayScore, setDisplayScore] = useState(0);
  const config = getRiskConfig(score);

  const radius = (size - 24) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (displayScore / 100) * circumference;

  useEffect(() => {
    const timer = setTimeout(() => {
      let start = 0;
      const step = () => {
        start += 1.5;
        if (start <= score) {
          setDisplayScore(Math.round(start));
          requestAnimationFrame(step);
        } else {
          setDisplayScore(score);
        }
      };
      requestAnimationFrame(step);
    }, 300);
    return () => clearTimeout(timer);
  }, [score]);

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative" style={{ width: size, height: size }}>
        {/* Outer glow ring */}
        <svg
          width={size}
          height={size}
          className="absolute inset-0"
          style={{ filter: `drop-shadow(0 0 12px ${config.glow})` }}
        >
          {/* Background track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="rgba(255,255,255,0.06)"
            strokeWidth={10}
          />
          {/* Progress arc */}
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={config.color}
            strokeWidth={10}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            style={{ transformOrigin: "center", rotate: "-90deg" }}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.5, ease: "easeOut", delay: 0.3 }}
          />
        </svg>

        {/* Inner content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          {/* Center glow */}
          <div
            className="absolute w-16 h-16 rounded-full blur-2xl opacity-40"
            style={{ background: config.color }}
          />
          <motion.span
            className={`text-4xl font-display font-black relative z-10 ${config.textColor}`}
            style={{ textShadow: `0 0 20px ${config.glow}` }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            {displayScore}
          </motion.span>
          <span className="text-xs font-mono text-text-secondary tracking-widest relative z-10">RISK</span>
        </div>

        {/* Scanning pulse */}
        <div
          className="absolute inset-0 rounded-full border-2 opacity-20 animate-ping"
          style={{ borderColor: config.color }}
        />
      </div>

      {/* Risk badge */}
      {showLabel && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.8 }}
          className={`px-4 py-1.5 rounded-full border font-mono text-xs font-semibold tracking-widest ${config.badge}`}
        >
          ● {config.label}
        </motion.div>
      )}
    </div>
  );
}

/* Bar variant */
export function RiskBar({ score = 0, label = "" }) {
  const [displayScore, setDisplayScore] = useState(0);
  const config = getRiskConfig(score);

  useEffect(() => {
    const timer = setTimeout(() => {
      let start = 0;
      const step = () => {
        start += 2;
        if (start <= score) {
          setDisplayScore(Math.round(start));
          requestAnimationFrame(step);
        } else {
          setDisplayScore(score);
        }
      };
      requestAnimationFrame(step);
    }, 200);
    return () => clearTimeout(timer);
  }, [score]);

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-xs font-mono text-text-secondary tracking-wider">{label}</span>
        <span className={`text-sm font-mono font-bold ${config.textColor}`}>{displayScore}%</span>
      </div>
      <div className="relative h-2 bg-white/5 rounded-full overflow-hidden">
        <motion.div
          className="absolute inset-y-0 left-0 rounded-full"
          style={{
            background: `linear-gradient(90deg, ${config.color}88, ${config.color})`,
            boxShadow: `0 0 12px ${config.glow}`,
          }}
          initial={{ width: "0%" }}
          animate={{ width: `${displayScore}%` }}
          transition={{ duration: 1.2, ease: "easeOut", delay: 0.2 }}
        />
        {/* Shine */}
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent" />
      </div>
    </div>
  );
}
