import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import LoadingSpinner from "../components/common/LoadingSpinner";
import TestHistory from "../components/dashboard/TestHistory";
import { getAllSessions } from "../services/api";
import type { TestSession } from "../types";

export default function Dashboard() {
  const navigate = useNavigate();

  const [sessions, setSessions] = useState<TestSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const fetchSessions = async () => {
      setLoading(true);
      try {
        const data = await getAllSessions();
        if (!cancelled) setSessions(data);
      } catch {
        if (!cancelled) setError("Failed to load test history.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchSessions();
    return () => { cancelled = true; };
  }, []);

  return (
    <div className="min-h-screen bg-[#F0F4FF]">
      <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col items-start gap-4 sm:flex-row sm:items-center sm:justify-between"
        >
          <div>
            <h1 className="text-3xl font-extrabold text-gray-900">Dashboard</h1>
            <p className="mt-1 text-base text-gray-500">
              View all tests and detailed results.
            </p>
          </div>

          <button
            onClick={() => navigate("/")}
            className="inline-flex items-center gap-2 rounded-full bg-[#6C63FF] px-6 py-3 text-sm font-bold text-white shadow-md shadow-[#6C63FF]/25 transition-all hover:scale-105 hover:bg-[#5a52e0] active:scale-95"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            New Test
          </button>
        </motion.div>

        {/* Error */}
        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-6 rounded-xl bg-[#FF6584]/10 p-4 text-center text-sm font-medium text-[#FF6584]"
          >
            {error}
          </motion.div>
        )}

        {/* Content */}
        <AnimatePresence mode="wait">
          {loading && (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="mt-12"
            >
              <LoadingSpinner message="Loading test history..." />
            </motion.div>
          )}

          {!loading && (
            <motion.div
              key="content"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mt-8"
            >
              <TestHistory sessions={sessions} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
