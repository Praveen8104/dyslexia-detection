import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import ProgressBar from "../components/common/ProgressBar";
import LoadingSpinner from "../components/common/LoadingSpinner";
import ImageUploader from "../components/handwriting/ImageUploader";
import HandwritingResult from "../components/handwriting/HandwritingResult";
import { analyzeHandwriting } from "../services/api";
import type { HandwritingResult as HandwritingResultType } from "../types";

const STEP_LABELS = ["Handwriting", "Speech", "Results"];

export default function HandwritingTest() {
  const navigate = useNavigate();
  const sessionId = Number(sessionStorage.getItem("session_id"));

  const [imageFile, setImageFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<HandwritingResultType | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Redirect if no session
  if (!sessionId) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-[#F0F4FF] font-[Comic_Neue]">
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

  const handleAnalyze = async () => {
    if (!imageFile) return;

    setLoading(true);
    setError(null);

    try {
      const data = await analyzeHandwriting(sessionId, imageFile);
      setResult(data);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Analysis failed. Please try again.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleContinue = () => {
    if (result) {
      sessionStorage.setItem("handwriting_score", String(result.risk_score));
    }
    navigate("/speech-test");
  };

  return (
    <div className="min-h-screen bg-[#F0F4FF] font-[Comic_Neue]">
      <div className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
        {/* Progress */}
        <ProgressBar currentStep={1} totalSteps={3} labels={STEP_LABELS} />

        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-10 text-center"
        >
          <h1 className="text-3xl font-extrabold text-gray-900">Handwriting Test</h1>
          <p className="mt-2 text-base text-gray-500">
            Upload a photo of the child's handwriting so our AI can look for dyslexia markers.
          </p>
        </motion.div>

        {/* Instructions */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="mt-8 rounded-2xl border border-[#6C63FF]/15 bg-white p-6 shadow-sm"
        >
          <h2 className="mb-3 text-lg font-bold text-[#6C63FF]">Instructions</h2>
          <ul className="space-y-2 text-sm text-gray-600">
            <li className="flex items-start gap-2">
              <span className="mt-0.5 inline-block h-2 w-2 flex-shrink-0 rounded-full bg-[#43E97B]" />
              Ask the child to write a few sentences on plain paper.
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-0.5 inline-block h-2 w-2 flex-shrink-0 rounded-full bg-[#43E97B]" />
              Take a clear, well-lit photo of the handwriting.
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-0.5 inline-block h-2 w-2 flex-shrink-0 rounded-full bg-[#43E97B]" />
              Upload the image below (PNG or JPG).
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-0.5 inline-block h-2 w-2 flex-shrink-0 rounded-full bg-[#FFB347]" />
              Make sure the writing fills most of the image.
            </li>
          </ul>
        </motion.div>

        {/* Uploader */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-8"
        >
          <ImageUploader onImageSelected={setImageFile} disabled={loading} />
        </motion.div>

        {/* Analyze Button */}
        {imageFile && !result && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6 text-center"
          >
            <button
              onClick={handleAnalyze}
              className="inline-flex items-center gap-2 rounded-full bg-[#6C63FF] px-8 py-3.5 text-lg font-bold text-white shadow-lg shadow-[#6C63FF]/30 transition-all hover:scale-105 hover:bg-[#5a52e0] active:scale-95"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              Analyze Handwriting
            </button>
          </motion.div>
        )}

        {/* Loading */}
        {loading && (
          <div className="mt-8">
            <LoadingSpinner message="Analyzing handwriting... this may take a moment." />
          </div>
        )}

        {/* Error */}
        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-6 rounded-xl bg-[#FF6584]/10 p-4 text-center text-sm font-medium text-[#FF6584]"
          >
            {error}
            <button
              onClick={handleAnalyze}
              className="mt-2 block w-full text-center text-sm font-bold text-[#6C63FF] underline"
            >
              Try Again
            </button>
          </motion.div>
        )}

        {/* Result */}
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8 space-y-6"
          >
            <HandwritingResult result={result} />

            <div className="text-center">
              <button
                onClick={handleContinue}
                className="inline-flex items-center gap-2 rounded-full bg-[#43E97B] px-8 py-3.5 text-lg font-bold text-white shadow-lg shadow-[#43E97B]/30 transition-all hover:scale-105 hover:bg-[#36d46a] active:scale-95"
              >
                Continue to Speech Test
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
