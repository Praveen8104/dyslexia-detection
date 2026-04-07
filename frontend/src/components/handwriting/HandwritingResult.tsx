import { motion } from "framer-motion";

interface HandwritingResultData {
  prediction: string;
  confidence: number;
  markers: string[];
  risk_score: number;
}

interface HandwritingResultProps {
  result: HandwritingResultData;
}

const predictionStyles: Record<string, { color: string; bg: string; label: string }> = {
  Normal: { color: "text-green-600", bg: "bg-green-100", label: "Normal" },
  Reversal: { color: "text-red-600", bg: "bg-red-100", label: "Reversal Detected" },
  Corrected: { color: "text-orange-600", bg: "bg-orange-100", label: "Corrected" },
};

const getRiskBarColor = (score: number): string => {
  if (score <= 30) return "bg-[#43E97B]";
  if (score <= 60) return "bg-orange-400";
  return "bg-[#FF6584]";
};

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.12 },
  },
};

const fadeUp = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: "easeOut" as const } },
};

const HandwritingResult: React.FC<HandwritingResultProps> = ({ result }) => {
  const { prediction, confidence, markers, risk_score } = result;
  const style = predictionStyles[prediction] ?? predictionStyles.Normal;
  const confidencePercent = Math.round(confidence * 100);

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="w-full rounded-2xl border-2 border-[#6C63FF]/20 bg-white shadow-lg overflow-hidden"
    >
      {/* Header */}
      <div className="px-5 py-3 bg-[#F0F4FF] border-b border-[#6C63FF]/10 flex items-center gap-2">
        <div className="w-3 h-3 rounded-full bg-[#6C63FF]" />
        <h3 className="text-sm font-bold text-[#6C63FF]">Analysis Results</h3>
      </div>

      <div className="p-5 space-y-5">
        {/* Prediction badge */}
        <motion.div variants={fadeUp} className="flex items-center gap-3">
          <span className="text-sm font-semibold text-gray-500">Prediction:</span>
          <span
            className={`px-4 py-1.5 rounded-full text-sm font-bold ${style.bg} ${style.color}`}
          >
            {style.label}
          </span>
        </motion.div>

        {/* Confidence */}
        <motion.div variants={fadeUp}>
          <div className="flex justify-between items-center mb-1.5">
            <span className="text-sm font-semibold text-gray-500">Confidence</span>
            <span className="text-sm font-bold text-[#6C63FF]">{confidencePercent}%</span>
          </div>
          <div className="w-full h-3 rounded-full bg-gray-200 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${confidencePercent}%` }}
              transition={{ duration: 0.8, ease: "easeOut" }}
              className="h-full rounded-full bg-[#6C63FF]"
            />
          </div>
        </motion.div>

        {/* Risk score */}
        <motion.div variants={fadeUp}>
          <div className="flex justify-between items-center mb-1.5">
            <span className="text-sm font-semibold text-gray-500">Risk Score</span>
            <span className="text-sm font-bold text-gray-700">{risk_score}/100</span>
          </div>
          <div className="w-full h-3 rounded-full bg-gray-200 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${risk_score}%` }}
              transition={{ duration: 0.8, ease: "easeOut", delay: 0.2 }}
              className={`h-full rounded-full ${getRiskBarColor(risk_score)}`}
            />
          </div>
        </motion.div>

        {/* Markers */}
        {markers.length > 0 && (
          <motion.div variants={fadeUp}>
            <span className="text-sm font-semibold text-gray-500 block mb-2">
              Detected Markers
            </span>
            <div className="flex flex-wrap gap-2">
              {markers.map((marker, idx) => (
                <motion.span
                  key={marker}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.4 + idx * 0.08 }}
                  className="
                    px-3 py-1 rounded-full text-xs font-semibold
                    bg-[#FF6584]/10 text-[#FF6584] border border-[#FF6584]/20
                  "
                >
                  {marker}
                </motion.span>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};

export default HandwritingResult;
