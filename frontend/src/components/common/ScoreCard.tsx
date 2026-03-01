import { motion } from "framer-motion";

interface ScoreCardProps {
  title: string;
  score: number;
  maxScore?: number;
  color?: string;
}

export default function ScoreCard({
  title,
  score,
  maxScore = 100,
  color = "#6C63FF",
}: ScoreCardProps) {
  const percentage = Math.min((score / maxScore) * 100, 100);
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="flex flex-col items-center gap-3 rounded-2xl bg-white p-6 shadow-lg "
    >
      {/* Circular progress */}
      <div className="relative h-36 w-36">
        <svg className="h-full w-full -rotate-90" viewBox="0 0 120 120">
          {/* Background circle */}
          <circle
            cx="60"
            cy="60"
            r={radius}
            fill="none"
            stroke="#E5E7EB"
            strokeWidth="10"
          />
          {/* Animated progress circle */}
          <motion.circle
            cx="60"
            cy="60"
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.2, ease: "easeOut", delay: 0.3 }}
          />
        </svg>

        {/* Score text in center */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            className="text-3xl font-bold"
            style={{ color }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
          >
            {score}
          </motion.span>
          <span className="text-xs font-semibold text-gray-400">
            / {maxScore}
          </span>
        </div>
      </div>

      {/* Title */}
      <h3 className="text-lg font-bold text-gray-700 text-center">{title}</h3>
    </motion.div>
  );
}
