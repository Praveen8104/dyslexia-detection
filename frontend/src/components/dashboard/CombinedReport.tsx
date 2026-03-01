import React from "react";
import { motion } from "framer-motion";
import RiskGauge from "./RiskGauge";

interface CombinedResult {
  combined_score: number;
  risk_level: string;
  recommendation: string;
  disclaimer: string;
}

interface CombinedReportProps {
  result: CombinedResult;
  handwritingScore?: number;
  speechScore?: number;
}

const scoreColor = (score: number): string => {
  if (score <= 30) return "#43E97B";
  if (score <= 60) return "#FFB347";
  return "#FF6584";
};

const fadeUp = {
  hidden: { opacity: 0, y: 16 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.15, duration: 0.5, ease: "easeOut" },
  }),
};

const CombinedReport: React.FC<CombinedReportProps> = ({
  result,
  handwritingScore,
  speechScore,
}) => {
  return (
    <motion.div
      className="mx-auto flex w-full max-w-2xl flex-col gap-6"
      initial="hidden"
      animate="visible"
    >
      {/* Combined Score Gauge */}
      <motion.div
        className="rounded-2xl bg-white p-6 shadow-sm"
        variants={fadeUp}
        custom={0}
      >
        <h3 className="mb-4 text-center text-lg font-semibold text-gray-800">
          Combined Risk Score
        </h3>
        <RiskGauge score={result.combined_score} riskLevel={result.risk_level} />
      </motion.div>

      {/* Individual Module Scores */}
      <motion.div
        className="grid grid-cols-1 gap-4 sm:grid-cols-2"
        variants={fadeUp}
        custom={1}
      >
        {/* Handwriting */}
        <div className="rounded-2xl bg-white p-5 shadow-sm">
          <div className="mb-1 flex items-center justify-between">
            <span className="text-sm font-medium text-gray-500">Handwriting Analysis</span>
            <span className="rounded-md bg-[#F0F4FF] px-2 py-0.5 text-xs font-semibold text-[#6C63FF]">
              55% weight
            </span>
          </div>

          {handwritingScore !== undefined ? (
            <>
              <p
                className="mt-2 text-3xl font-bold"
                style={{ color: scoreColor(handwritingScore) }}
              >
                {handwritingScore.toFixed(1)}
              </p>

              {/* Mini progress bar */}
              <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-gray-100">
                <motion.div
                  className="h-full rounded-full"
                  style={{ backgroundColor: scoreColor(handwritingScore) }}
                  initial={{ width: 0 }}
                  animate={{ width: `${handwritingScore}%` }}
                  transition={{ duration: 1, ease: "easeOut", delay: 0.4 }}
                />
              </div>
            </>
          ) : (
            <p className="mt-2 text-2xl font-semibold text-gray-300">--</p>
          )}
        </div>

        {/* Speech */}
        <div className="rounded-2xl bg-white p-5 shadow-sm">
          <div className="mb-1 flex items-center justify-between">
            <span className="text-sm font-medium text-gray-500">Speech Analysis</span>
            <span className="rounded-md bg-[#F0F4FF] px-2 py-0.5 text-xs font-semibold text-[#6C63FF]">
              45% weight
            </span>
          </div>

          {speechScore !== undefined ? (
            <>
              <p
                className="mt-2 text-3xl font-bold"
                style={{ color: scoreColor(speechScore) }}
              >
                {speechScore.toFixed(1)}
              </p>

              <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-gray-100">
                <motion.div
                  className="h-full rounded-full"
                  style={{ backgroundColor: scoreColor(speechScore) }}
                  initial={{ width: 0 }}
                  animate={{ width: `${speechScore}%` }}
                  transition={{ duration: 1, ease: "easeOut", delay: 0.55 }}
                />
              </div>
            </>
          ) : (
            <p className="mt-2 text-2xl font-semibold text-gray-300">--</p>
          )}
        </div>
      </motion.div>

      {/* Score Breakdown Explanation */}
      <motion.div
        className="rounded-2xl bg-white p-5 shadow-sm"
        variants={fadeUp}
        custom={2}
      >
        <h4 className="mb-3 text-sm font-semibold uppercase tracking-wider text-gray-500">
          Score Breakdown
        </h4>
        <div className="flex items-center gap-3">
          {/* Handwriting portion */}
          <div className="flex-1">
            <div className="mb-1 flex items-center justify-between text-xs text-gray-500">
              <span>Handwriting (55%)</span>
              <span>{handwritingScore !== undefined ? handwritingScore.toFixed(1) : "--"}</span>
            </div>
            <div className="h-3 w-full overflow-hidden rounded-full bg-gray-100">
              <motion.div
                className="h-full rounded-full bg-[#6C63FF]"
                initial={{ width: 0 }}
                animate={{ width: "55%" }}
                transition={{ duration: 0.8, delay: 0.6 }}
              />
            </div>
          </div>

          <span className="text-lg font-light text-gray-300">+</span>

          {/* Speech portion */}
          <div className="flex-1">
            <div className="mb-1 flex items-center justify-between text-xs text-gray-500">
              <span>Speech (45%)</span>
              <span>{speechScore !== undefined ? speechScore.toFixed(1) : "--"}</span>
            </div>
            <div className="h-3 w-full overflow-hidden rounded-full bg-gray-100">
              <motion.div
                className="h-full rounded-full bg-[#FF6584]"
                initial={{ width: 0 }}
                animate={{ width: "45%" }}
                transition={{ duration: 0.8, delay: 0.75 }}
              />
            </div>
          </div>
        </div>
        <p className="mt-3 text-center text-xs text-gray-400">
          Combined = (Handwriting x 0.55) + (Speech x 0.45)
        </p>
      </motion.div>

      {/* Recommendation */}
      <motion.div
        className="rounded-2xl border-l-4 border-[#6C63FF] bg-[#F0F4FF] p-5"
        variants={fadeUp}
        custom={3}
      >
        <h4 className="mb-2 text-sm font-semibold uppercase tracking-wider text-[#6C63FF]">
          Recommendation
        </h4>
        <p className="text-sm leading-relaxed text-gray-700">{result.recommendation}</p>
      </motion.div>

      {/* Disclaimer */}
      <motion.div
        className="rounded-2xl bg-gray-100 p-4"
        variants={fadeUp}
        custom={4}
      >
        <p className="text-xs leading-relaxed text-gray-500">
          <span className="mr-1 font-semibold text-gray-600">Disclaimer:</span>
          {result.disclaimer}
        </p>
      </motion.div>
    </motion.div>
  );
};

export default CombinedReport;
