import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import LoadingSpinner from "../components/common/LoadingSpinner";
import TestDetail from "../components/dashboard/TestDetail";
import { getResults } from "../services/api";
import type { TestSession } from "../types";

export default function TestDetailPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();

  const [session, setSession] = useState<TestSession | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;

    let cancelled = false;

    const fetchSession = async () => {
      setLoading(true);
      try {
        const data = await getResults(Number(sessionId));
        if (!cancelled) setSession(data);
      } catch {
        if (!cancelled) setError("Failed to load test details.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchSession();
    return () => { cancelled = true; };
  }, [sessionId]);

  return (
    <div className="min-h-screen bg-[#F0F4FF]">
      <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
        {/* Back button */}
        <motion.button
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          onClick={() => navigate("/dashboard")}
          className="mb-6 inline-flex items-center gap-2 text-sm font-medium text-gray-500 transition-colors hover:text-[#6C63FF]"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          Back to Dashboard
        </motion.button>

        {loading && <LoadingSpinner message="Loading test details..." />}

        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="rounded-xl bg-[#FF6584]/10 p-4 text-center text-sm font-medium text-[#FF6584]"
          >
            {error}
          </motion.div>
        )}

        {!loading && session && (
          <TestDetail
            session={session}
            onClose={() => navigate("/dashboard")}
          />
        )}
      </div>
    </div>
  );
}
