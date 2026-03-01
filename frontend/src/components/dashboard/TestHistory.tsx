import React from "react";
import { motion, AnimatePresence } from "framer-motion";

interface Session {
  id: number;
  created_at: string;
  combined_score: number | null;
  risk_level: string | null;
}

interface TestHistoryProps {
  sessions: Session[];
}

const riskBadgeColor = (level: string | null): string => {
  if (!level) return "#94A3B8";
  const l = level.toLowerCase();
  if (l.includes("low") || l.includes("no")) return "#43E97B";
  if (l.includes("moderate") || l.includes("medium")) return "#FFB347";
  if (l.includes("high") || l.includes("severe")) return "#FF6584";
  return "#6C63FF";
};

const formatDate = (iso: string): string => {
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const TestHistory: React.FC<TestHistoryProps> = ({ sessions }) => {
  if (!sessions || sessions.length === 0) {
    return (
      <motion.div
        className="flex flex-col items-center justify-center rounded-2xl bg-white p-10 shadow-sm"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <svg
          className="mb-4 h-16 w-16 text-[#6C63FF] opacity-40"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={1.5}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M9 12h6m-3-3v6m-7 4h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
          />
        </svg>
        <p className="text-lg font-medium text-gray-500">No test sessions yet</p>
        <p className="mt-1 text-sm text-gray-400">
          Complete a test to see your history here.
        </p>
      </motion.div>
    );
  }

  return (
    <div className="overflow-hidden rounded-2xl bg-white shadow-sm">
      {/* Header */}
      <div className="border-b border-gray-100 px-6 py-4">
        <h3 className="text-lg font-semibold text-gray-800">Test History</h3>
      </div>

      {/* Desktop table */}
      <div className="hidden md:block">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-gray-100 bg-[#F0F4FF]/60 text-xs uppercase tracking-wider text-gray-500">
              <th className="px-6 py-3 font-medium">#</th>
              <th className="px-6 py-3 font-medium">Date</th>
              <th className="px-6 py-3 font-medium">Score</th>
              <th className="px-6 py-3 font-medium">Risk Level</th>
            </tr>
          </thead>
          <tbody>
            <AnimatePresence>
              {sessions.map((s, i) => (
                <motion.tr
                  key={s.id}
                  className="border-b border-gray-50 transition-colors hover:bg-[#F0F4FF]/40"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ delay: i * 0.05 }}
                >
                  <td className="px-6 py-4 font-medium text-gray-400">{s.id}</td>
                  <td className="px-6 py-4 text-gray-700">{formatDate(s.created_at)}</td>
                  <td className="px-6 py-4">
                    {s.combined_score !== null ? (
                      <span className="font-semibold text-gray-800">
                        {s.combined_score.toFixed(1)}
                      </span>
                    ) : (
                      <span className="text-gray-400">--</span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className="inline-block rounded-full px-3 py-1 text-xs font-semibold text-white"
                      style={{ backgroundColor: riskBadgeColor(s.risk_level) }}
                    >
                      {s.risk_level ?? "Pending"}
                    </span>
                  </td>
                </motion.tr>
              ))}
            </AnimatePresence>
          </tbody>
        </table>
      </div>

      {/* Mobile card list */}
      <div className="flex flex-col gap-3 p-4 md:hidden">
        <AnimatePresence>
          {sessions.map((s, i) => (
            <motion.div
              key={s.id}
              className="rounded-xl border border-gray-100 bg-[#F0F4FF]/30 p-4"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ delay: i * 0.06 }}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-400">#{s.id}</span>
                <span
                  className="inline-block rounded-full px-3 py-0.5 text-xs font-semibold text-white"
                  style={{ backgroundColor: riskBadgeColor(s.risk_level) }}
                >
                  {s.risk_level ?? "Pending"}
                </span>
              </div>
              <p className="mt-2 text-sm text-gray-600">{formatDate(s.created_at)}</p>
              <p className="mt-1 text-xl font-bold text-gray-800">
                {s.combined_score !== null ? s.combined_score.toFixed(1) : "--"}
              </p>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default TestHistory;
