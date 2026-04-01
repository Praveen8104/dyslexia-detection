import { motion } from "framer-motion";
import type { TestSession } from "../../types";
import RiskGauge from "./RiskGauge";

interface TestDetailProps {
  session: TestSession;
  onClose: () => void;
}

const formatDate = (iso: string): string => {
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

function getRiskColor(level: string | null): string {
  if (!level) return "#94A3B8";
  const l = level.toLowerCase();
  if (l.includes("low")) return "#43E97B";
  if (l.includes("moderate")) return "#FFB347";
  return "#FF6584";
}

export default function TestDetail({ session, onClose }: TestDetailProps) {
  const hw = session.handwriting_tests[0] ?? null;
  const sp = session.speech_tests[0] ?? null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="rounded-2xl bg-white shadow-lg overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-100 px-6 py-4">
        <div>
          <h3 className="text-lg font-bold text-gray-900">
            Test #{session.id} — {session.user_name ?? "Unknown"}
            {session.user_age != null && (
              <span className="ml-1 text-sm font-normal text-gray-400">(age {session.user_age})</span>
            )}
          </h3>
          <p className="text-xs text-gray-400 mt-0.5">{formatDate(session.created_at)}</p>
        </div>
        <button
          onClick={onClose}
          className="rounded-lg p-2 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div className="p-6 space-y-8">
        {/* Combined Score */}
        {session.combined_score !== null && (
          <div className="flex flex-col items-center">
            <RiskGauge
              score={session.combined_score}
              riskLevel={session.risk_level ?? "Unknown"}
            />
            <p className="mt-2 text-sm text-gray-500">Combined Risk Score</p>
          </div>
        )}

        {/* Module Scores Side-by-Side */}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          {/* Handwriting Details */}
          <div className="rounded-xl border-2 border-[#6C63FF]/15 p-5">
            <div className="flex items-center gap-2 mb-4">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#6C63FF]/10">
                <svg className="h-4 w-4 text-[#6C63FF]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M16.862 3.487a2.1 2.1 0 113.003 2.94L7.5 18.795l-4 1 1-4L16.862 3.487z" />
                </svg>
              </div>
              <h4 className="font-bold text-gray-800">Handwriting Analysis</h4>
            </div>

            {hw ? (
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Prediction</span>
                  <span
                    className="rounded-full px-3 py-0.5 text-xs font-semibold text-white"
                    style={{
                      backgroundColor:
                        hw.prediction === "Normal" ? "#43E97B" :
                        hw.prediction === "Reversal" ? "#FF6584" : "#FFB347",
                    }}
                  >
                    {hw.prediction}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Confidence</span>
                  <span className="font-semibold text-gray-800">
                    {(hw.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                {/* Confidence bar */}
                <div className="h-2 w-full overflow-hidden rounded-full bg-gray-100">
                  <motion.div
                    className="h-full rounded-full bg-[#6C63FF]"
                    initial={{ width: 0 }}
                    animate={{ width: `${hw.confidence * 100}%` }}
                    transition={{ duration: 0.6 }}
                  />
                </div>
                {/* Markers */}
                {hw.markers && (() => {
                  try {
                    const markers: string[] = typeof hw.markers === "string" ? JSON.parse(hw.markers) : hw.markers;
                    if (markers.length > 0) {
                      return (
                        <div className="mt-2">
                          <p className="text-xs font-medium text-gray-400 mb-1">Markers</p>
                          <div className="flex flex-wrap gap-1">
                            {markers.map((m, i) => (
                              <span key={i} className="rounded-md bg-[#FF6584]/10 px-2 py-0.5 text-xs text-[#FF6584]">
                                {m}
                              </span>
                            ))}
                          </div>
                        </div>
                      );
                    }
                  } catch { /* ignore parse errors */ }
                  return null;
                })()}
              </div>
            ) : (
              <p className="text-sm text-gray-400 italic">No handwriting test taken</p>
            )}
          </div>

          {/* Speech Details */}
          <div className="rounded-xl border-2 border-[#FF6584]/15 p-5">
            <div className="flex items-center gap-2 mb-4">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#FF6584]/10">
                <svg className="h-4 w-4 text-[#FF6584]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 1a4 4 0 00-4 4v6a4 4 0 008 0V5a4 4 0 00-4-4z" />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19 11a7 7 0 01-14 0M12 19v3m-3 0h6" />
                </svg>
              </div>
              <h4 className="font-bold text-gray-800">Speech Analysis</h4>
            </div>

            {sp ? (
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Prediction</span>
                  <span
                    className="rounded-full px-3 py-0.5 text-xs font-semibold text-white"
                    style={{
                      backgroundColor: sp.prediction === "Normal" ? "#43E97B" : "#FF6584",
                    }}
                  >
                    {sp.prediction}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Confidence</span>
                  <span className="font-semibold text-gray-800">
                    {(sp.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-gray-100">
                  <motion.div
                    className="h-full rounded-full bg-[#FF6584]"
                    initial={{ width: 0 }}
                    animate={{ width: `${sp.confidence * 100}%` }}
                    transition={{ duration: 0.6 }}
                  />
                </div>

                {/* Speech metrics */}
                <div className="mt-3 grid grid-cols-3 gap-2">
                  <div className="rounded-lg bg-[#F0F4FF] p-2 text-center">
                    <p className="text-lg font-bold text-[#6C63FF]">{sp.reading_speed_wpm}</p>
                    <p className="text-[10px] text-gray-400">WPM</p>
                  </div>
                  <div className="rounded-lg bg-[#FFB347]/10 p-2 text-center">
                    <p className="text-lg font-bold text-[#FFB347]">{sp.hesitation_count}</p>
                    <p className="text-[10px] text-gray-400">Hesitations</p>
                  </div>
                  <div className="rounded-lg bg-[#FF6584]/10 p-2 text-center">
                    <p className="text-lg font-bold text-[#FF6584]">
                      {(sp.silence_ratio * 100).toFixed(0)}%
                    </p>
                    <p className="text-[10px] text-gray-400">Silence</p>
                  </div>
                </div>

                {sp.expected_text && (
                  <div className="mt-2">
                    <p className="text-xs font-medium text-gray-400 mb-1">Reading Prompt</p>
                    <p className="rounded-lg bg-gray-50 p-2 text-sm text-gray-600 italic">
                      "{sp.expected_text}"
                    </p>
                  </div>
                )}

                {/* Transcription & Reading Accuracy */}
                {sp.transcript && (
                  <div className="mt-3 rounded-lg border border-[#6C63FF]/15 bg-[#6C63FF]/5 p-3 space-y-2">
                    <p className="text-xs font-bold text-[#6C63FF]">Reading Accuracy</p>
                    <p className="text-xs text-gray-500">
                      Child read: <span className="italic font-medium text-gray-700">&ldquo;{sp.transcript}&rdquo;</span>
                    </p>
                    {sp.reading_accuracy !== null && (
                      <p className="text-sm font-bold" style={{
                        color: sp.reading_accuracy >= 90 ? "#43E97B" : sp.reading_accuracy >= 70 ? "#FFB347" : "#FF6584"
                      }}>
                        {sp.reading_accuracy.toFixed(1)}% accurate
                      </p>
                    )}
                    {sp.error_details && (
                      <p className="text-[10px] text-gray-400">{sp.error_details}</p>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <p className="text-sm text-gray-400 italic">No speech test taken</p>
            )}
          </div>
        </div>

        {/* Disclaimer */}
        <div className="rounded-lg bg-gray-50 p-4 text-xs text-gray-400 text-center">
          This is a screening tool, not a clinical diagnosis. Results should be interpreted by a qualified professional.
        </div>
      </div>
    </motion.div>
  );
}
