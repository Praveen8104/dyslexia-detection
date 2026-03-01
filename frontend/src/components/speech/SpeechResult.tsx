import { motion } from "framer-motion";

interface SpeechResultData {
  prediction: string;
  confidence: number;
  reading_speed_wpm: number;
  hesitation_count: number;
  silence_ratio: number;
  risk_score: number;
}

interface SpeechResultProps {
  result: SpeechResultData;
}

function getRiskColor(score: number): string {
  if (score <= 0.3) return "#43E97B"; // accent / low risk
  if (score <= 0.6) return "#FFB347"; // warning / medium risk
  return "#FF6584"; // secondary / high risk
}

function getRiskLabel(score: number): string {
  if (score <= 0.3) return "Low Risk";
  if (score <= 0.6) return "Moderate Risk";
  return "High Risk";
}

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

const item = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0 },
};

export default function SpeechResult({ result }: SpeechResultProps) {
  const riskColor = getRiskColor(result.risk_score);
  const riskLabel = getRiskLabel(result.risk_score);

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="w-full space-y-6 rounded-2xl bg-white p-8 shadow-lg"
    >
      {/* Prediction badge */}
      <motion.div variants={item} className="flex items-center gap-3">
        <span
          className="rounded-full px-4 py-1.5 text-sm font-bold text-white"
          style={{ backgroundColor: riskColor }}
        >
          {result.prediction}
        </span>
        <span className="text-sm text-gray-500">
          Confidence:{" "}
          <span className="font-semibold text-gray-800">
            {(result.confidence * 100).toFixed(1)}%
          </span>
        </span>
      </motion.div>

      {/* Metrics grid */}
      <motion.div
        variants={item}
        className="grid grid-cols-1 gap-4 sm:grid-cols-3"
      >
        <MetricCard
          label="Reading Speed"
          value={`${result.reading_speed_wpm}`}
          unit="WPM"
          color="#6C63FF"
        />
        <MetricCard
          label="Hesitations"
          value={`${result.hesitation_count}`}
          unit="pauses"
          color="#FFB347"
        />
        <MetricCard
          label="Silence Ratio"
          value={`${(result.silence_ratio * 100).toFixed(1)}`}
          unit="%"
          color="#FF6584"
        />
      </motion.div>

      {/* Risk score bar */}
      <motion.div variants={item} className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="font-medium text-gray-600">Risk Score</span>
          <span className="font-bold" style={{ color: riskColor }}>
            {riskLabel} ({(result.risk_score * 100).toFixed(0)}%)
          </span>
        </div>
        <div className="h-3 w-full overflow-hidden rounded-full bg-gray-200">
          <motion.div
            className="h-full rounded-full"
            style={{ backgroundColor: riskColor }}
            initial={{ width: 0 }}
            animate={{ width: `${result.risk_score * 100}%` }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          />
        </div>
      </motion.div>
    </motion.div>
  );
}

function MetricCard({
  label,
  value,
  unit,
  color,
}: {
  label: string;
  value: string;
  unit: string;
  color: string;
}) {
  return (
    <div
      className="rounded-xl border p-4"
      style={{ borderColor: `${color}30` }}
    >
      <p className="text-xs font-medium text-gray-400">{label}</p>
      <p className="mt-1 text-2xl font-bold" style={{ color }}>
        {value}
        <span className="ml-1 text-sm font-normal text-gray-400">{unit}</span>
      </p>
    </div>
  );
}
