import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import LoadingSpinner from "../components/common/LoadingSpinner";
import TestHistory from "../components/dashboard/TestHistory";
import CombinedReport from "../components/dashboard/CombinedReport";
import { listUsers, getHistory } from "../services/api";
import type { User, TestSession } from "../types";

export default function Dashboard() {
  const navigate = useNavigate();

  const [users, setUsers] = useState<User[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [sessions, setSessions] = useState<TestSession[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(true);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch users on mount
  useEffect(() => {
    let cancelled = false;

    const fetchUsers = async () => {
      setLoadingUsers(true);
      try {
        const data = await listUsers();
        if (!cancelled) {
          setUsers(data);

          // Auto-select current user from session if available
          const storedUserId = sessionStorage.getItem("user_id");
          if (storedUserId && data.some((u) => u.id === Number(storedUserId))) {
            setSelectedUserId(Number(storedUserId));
          }
        }
      } catch {
        if (!cancelled) setError("Failed to load users.");
      } finally {
        if (!cancelled) setLoadingUsers(false);
      }
    };

    fetchUsers();
    return () => {
      cancelled = true;
    };
  }, []);

  // Fetch history when user is selected
  useEffect(() => {
    if (!selectedUserId) {
      setSessions([]);
      return;
    }

    let cancelled = false;

    const fetchHistory = async () => {
      setLoadingHistory(true);
      setError(null);
      try {
        const data = await getHistory(selectedUserId);
        if (!cancelled) setSessions(data);
      } catch {
        if (!cancelled) setError("Failed to load test history.");
      } finally {
        if (!cancelled) setLoadingHistory(false);
      }
    };

    fetchHistory();
    return () => {
      cancelled = true;
    };
  }, [selectedUserId]);

  // Get the latest completed session for detail display
  const latestSession = sessions.find((s) => s.combined_score !== null) ?? null;

  // Extract scores from latest session for CombinedReport
  const latestHandwritingScore =
    latestSession && latestSession.handwriting_tests.length > 0
      ? latestSession.handwriting_tests[0].confidence * 100
      : undefined;
  const latestSpeechScore =
    latestSession && latestSession.speech_tests.length > 0
      ? latestSession.speech_tests[0].confidence * 100
      : undefined;

  return (
    <div className="min-h-screen bg-[#F0F4FF] ">
      <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col items-start gap-4 sm:flex-row sm:items-center sm:justify-between"
        >
          <div>
            <h1 className="text-3xl font-extrabold text-gray-900">Dashboard</h1>
            <p className="mt-1 text-base text-gray-500">
              View test history and results for each child.
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

        {/* User Selector */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mt-8"
        >
          <label htmlFor="userSelect" className="mb-2 block text-sm font-semibold text-gray-700">
            Select a Child
          </label>

          {loadingUsers ? (
            <div className="rounded-xl bg-white p-4">
              <LoadingSpinner message="Loading users..." />
            </div>
          ) : (
            <select
              id="userSelect"
              value={selectedUserId ?? ""}
              onChange={(e) => setSelectedUserId(e.target.value ? Number(e.target.value) : null)}
              className="w-full rounded-xl border-2 border-[#6C63FF]/20 bg-white px-4 py-3 text-gray-800 outline-none transition-colors focus:border-[#6C63FF] sm:max-w-md"
            >
              <option value="">-- Choose a child --</option>
              {users.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.name} (age {user.age})
                </option>
              ))}
            </select>
          )}
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
          {!selectedUserId && !loadingUsers && (
            <motion.div
              key="empty"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mt-12 flex flex-col items-center justify-center rounded-2xl bg-white p-12 shadow-sm"
            >
              <svg
                className="mb-4 h-20 w-20 text-[#6C63FF] opacity-30"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={1}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              <p className="text-lg font-semibold text-gray-500">Select a child to view their results</p>
              <p className="mt-1 text-sm text-gray-400">
                Choose from the dropdown above or start a new test.
              </p>
            </motion.div>
          )}

          {selectedUserId && loadingHistory && (
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

          {selectedUserId && !loadingHistory && (
            <motion.div
              key="content"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mt-8 space-y-10"
            >
              {/* Test History */}
              <section>
                <TestHistory sessions={sessions} />
              </section>

              {/* Latest Result Details */}
              {latestSession && latestSession.combined_score !== null && (
                <section>
                  <h2 className="mb-4 text-xl font-bold text-gray-900">Latest Result Details</h2>
                  <CombinedReport
                    result={{
                      combined_score: latestSession.combined_score,
                      risk_level: latestSession.risk_level ?? "Unknown",
                      recommendation:
                        "Review the detailed scores above. If the risk level is moderate or high, consider consulting a specialist.",
                      disclaimer:
                        "This tool is for screening purposes only and does not constitute a medical diagnosis. Please consult a qualified professional for a comprehensive evaluation.",
                    }}
                    handwritingScore={latestHandwritingScore}
                    speechScore={latestSpeechScore}
                  />
                </section>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
