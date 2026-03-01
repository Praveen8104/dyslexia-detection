import React from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import type { TestSession } from "../../types";

interface TestHistoryProps {
  sessions: TestSession[];
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
  const navigate = useNavigate();

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
      <div className="border-b border-gray-100 px-6 py-4">
        <h3 className="text-lg font-semibold text-gray-800">
          All Tests ({sessions.length})
        </h3>
        <p className="text-xs text-gray-400 mt-1">Click on a test to view full details</p>
      </div>

      {/* Desktop table */}
      <div className="hidden md:block">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-gray-100 bg-[#F0F4FF]/60 text-xs uppercase tracking-wider text-gray-500">
              <th className="px-6 py-3 font-medium">#</th>
              <th className="px-6 py-3 font-medium">Child</th>
              <th className="px-6 py-3 font-medium">Date</th>
              <th className="px-6 py-3 font-medium">Score</th>
              <th className="px-6 py-3 font-medium">Risk Level</th>
              <th className="px-6 py-3 font-medium">Tests</th>
              <th className="px-6 py-3 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            <AnimatePresence>
              {sessions.map((s, i) => (
                <motion.tr
                  key={s.id}
                  onClick={() => navigate(`/dashboard/test/${s.id}`)}
                  className="border-b border-gray-50 cursor-pointer transition-colors hover:bg-[#F0F4FF]/40"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ delay: i * 0.05 }}
                >
                  <td className="px-6 py-4 font-medium text-gray-400">{s.id}</td>
                  <td className="px-6 py-4 text-gray-700">
                    <span className="font-medium">{s.user_name ?? "Unknown"}</span>
                    {s.user_age != null && (
                      <span className="ml-1 text-xs text-gray-400">(age {s.user_age})</span>
                    )}
                  </td>
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
                  <td className="px-6 py-4 text-gray-500 text-xs">
                    {s.handwriting_tests.length > 0 && (
                      <span className="mr-2 inline-flex items-center gap-1 rounded bg-[#6C63FF]/10 px-2 py-0.5 text-[#6C63FF]">
                        <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M16.862 3.487a2.1 2.1 0 113.003 2.94L7.5 18.795l-4 1 1-4L16.862 3.487z" />
                        </svg>
                        Handwriting
                      </span>
                    )}
                    {s.speech_tests.length > 0 && (
                      <span className="inline-flex items-center gap-1 rounded bg-[#FF6584]/10 px-2 py-0.5 text-[#FF6584]">
                        <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M12 1a4 4 0 00-4 4v6a4 4 0 008 0V5a4 4 0 00-4-4z" />
                        </svg>
                        Speech
                      </span>
                    )}
                    {s.handwriting_tests.length === 0 && s.speech_tests.length === 0 && (
                      <span className="text-gray-400">No tests</span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <svg
                      className="h-4 w-4 text-gray-300"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={2}
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                    </svg>
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
              onClick={() => navigate(`/dashboard/test/${s.id}`)}
              className="cursor-pointer rounded-xl border border-gray-100 bg-[#F0F4FF]/30 p-4 transition-colors hover:border-[#6C63FF]/30 hover:bg-[#6C63FF]/5"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ delay: i * 0.06 }}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-400">
                  #{s.id} · {formatDate(s.created_at)}
                </span>
                <span
                  className="inline-block rounded-full px-3 py-0.5 text-xs font-semibold text-white"
                  style={{ backgroundColor: riskBadgeColor(s.risk_level) }}
                >
                  {s.risk_level ?? "Pending"}
                </span>
              </div>
              <p className="mt-2 text-sm font-semibold text-gray-700">
                {s.user_name ?? "Unknown"}
                {s.user_age != null && (
                  <span className="ml-1 text-xs font-normal text-gray-400">(age {s.user_age})</span>
                )}
              </p>
              <p className="mt-1 text-xl font-bold text-gray-800">
                {s.combined_score !== null ? s.combined_score.toFixed(1) : "--"}
                <span className="ml-1 text-sm font-normal text-gray-400">/100</span>
              </p>
              <div className="mt-2 flex gap-2">
                {s.handwriting_tests.length > 0 && (
                  <span className="text-xs text-[#6C63FF]">Handwriting</span>
                )}
                {s.speech_tests.length > 0 && (
                  <span className="text-xs text-[#FF6584]">Speech</span>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default TestHistory;
