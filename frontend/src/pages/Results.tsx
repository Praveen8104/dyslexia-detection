import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import ProgressBar from "../components/common/ProgressBar";
import LoadingSpinner from "../components/common/LoadingSpinner";
import CombinedReport from "../components/dashboard/CombinedReport";
import { combineResults } from "../services/api";
import type { CombinedResult } from "../types";

const STEP_LABELS = ["Handwriting", "Speech", "Results"];

export default function Results() {
  const navigate = useNavigate();

  const sessionIdStr = sessionStorage.getItem("session_id");
  const sessionId = sessionIdStr ? Number(sessionIdStr) : null;
  const handwritingScore = sessionStorage.getItem("handwriting_score");
  const speechScore = sessionStorage.getItem("speech_score");

  const hwScore = handwritingScore ? Number(handwritingScore) : null;
  const spScore = speechScore ? Number(speechScore) : null;

  const [result, setResult] = useState<CombinedResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;

    let cancelled = false;

    const fetchResults = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await combineResults(sessionId!, hwScore, spScore);
        if (!cancelled) {
          setResult(data);
        }
      } catch (err: unknown) {
        if (!cancelled) {
          const message = err instanceof Error ? err.message : "Failed to load results.";
          setError(message);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchResults();

    return () => {
      cancelled = true;
    };
  }, [sessionId, hwScore, spScore]);

  // Redirect if no session
  if (!sessionId) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-[#F0F4FF] ">
        <p className="mb-4 text-lg font-semibold text-gray-600">No active session found.</p>
        <button
          onClick={() => navigate("/")}
          className="rounded-full bg-[#6C63FF] px-6 py-3 font-bold text-white shadow-md transition-all hover:bg-[#5a52e0]"
        >
          Go Home
        </button>
      </div>
    );
  }

  const handleNewTest = () => {
    sessionStorage.removeItem("session_id");
    sessionStorage.removeItem("user_id");
    sessionStorage.removeItem("user_name");
    sessionStorage.removeItem("user_age");
    sessionStorage.removeItem("handwriting_score");
    sessionStorage.removeItem("speech_score");
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-[#F0F4FF] ">
      <div className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
        {/* Progress */}
        <ProgressBar currentStep={3} totalSteps={3} labels={STEP_LABELS} />

        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-10 text-center"
        >
          <h1 className="text-3xl font-extrabold text-gray-900">Your Results</h1>
          <p className="mt-2 text-base text-gray-500">
            Here is the combined screening report based on handwriting and speech analysis.
          </p>
        </motion.div>

        {/* Loading */}
        {loading && (
          <div className="mt-12">
            <LoadingSpinner message="Crunching the numbers..." />
          </div>
        )}

        {/* Error */}
        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-8 rounded-xl bg-[#FF6584]/10 p-6 text-center"
          >
            <p className="text-sm font-medium text-[#FF6584]">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-3 text-sm font-bold text-[#6C63FF] underline"
            >
              Retry
            </button>
          </motion.div>
        )}

        {/* Combined Report */}
        {result && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mt-10 space-y-8"
          >
            <CombinedReport
              result={result}
              handwritingScore={hwScore ?? undefined}
              speechScore={spScore ?? undefined}
            />

            {/* Actions */}
            <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
              <button
                onClick={() => navigate("/dashboard")}
                className="inline-flex items-center gap-2 rounded-full bg-[#6C63FF] px-8 py-3.5 text-lg font-bold text-white shadow-lg shadow-[#6C63FF]/30 transition-all hover:scale-105 hover:bg-[#5a52e0] active:scale-95"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 17v-2m3 2v-4m3 4v-6m-9 10h12a2 2 0 002-2V7a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Go to Dashboard
              </button>

              <button
                onClick={handleNewTest}
                className="inline-flex items-center gap-2 rounded-full border-2 border-[#6C63FF] bg-white px-8 py-3.5 text-lg font-bold text-[#6C63FF] transition-all hover:scale-105 hover:bg-[#6C63FF]/5 active:scale-95"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Start New Test
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
