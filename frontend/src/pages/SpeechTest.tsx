import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import ProgressBar from "../components/common/ProgressBar";
import LoadingSpinner from "../components/common/LoadingSpinner";
import TextPrompt from "../components/speech/TextPrompt";
import AudioRecorder from "../components/speech/AudioRecorder";
import SpeechResult from "../components/speech/SpeechResult";
import { analyzeSpeech } from "../services/api";
import type { SpeechResult as SpeechResultType } from "../types";

const STEP_LABELS = ["Handwriting", "Speech", "Results"];

const READING_PROMPTS = [
  "The big brown dog jumped over the lazy fox.",
  "Sally sells seashells by the seashore.",
  "Peter Piper picked a peck of pickled peppers.",
];

export default function SpeechTest() {
  const navigate = useNavigate();
  const sessionId = Number(sessionStorage.getItem("session_id"));
  const userAge = Number(sessionStorage.getItem("user_age") || "8");

  const [promptIndex, setPromptIndex] = useState(0);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SpeechResultType | null>(null);
  const [error, setError] = useState<string | null>(null);

  const currentPrompt = READING_PROMPTS[promptIndex];

  // Determine age group for TextPrompt sizing
  const ageGroup = userAge <= 7 ? "5-7" : userAge <= 10 ? "8-10" : "11-13";

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

  const handleRecordingComplete = useCallback((blob: Blob) => {
    setAudioBlob(blob);
  }, []);

  const handleAnalyze = async () => {
    if (!audioBlob) return;

    setLoading(true);
    setError(null);

    try {
      const data = await analyzeSpeech(sessionId, audioBlob, currentPrompt);
      setResult(data);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Speech analysis failed. Please try again.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleNextPrompt = () => {
    if (promptIndex < READING_PROMPTS.length - 1) {
      setPromptIndex((prev) => prev + 1);
      setAudioBlob(null);
      setResult(null);
      setError(null);
    }
  };

  const handleViewResults = () => {
    if (result) {
      sessionStorage.setItem("speech_score", String(result.risk_score));
    }
    navigate("/results");
  };

  return (
    <div className="min-h-screen bg-[#F0F4FF] font-[Comic_Neue]">
      <div className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
        {/* Progress */}
        <ProgressBar currentStep={2} totalSteps={3} labels={STEP_LABELS} />

        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-10 text-center"
        >
          <h1 className="text-3xl font-extrabold text-gray-900">Speech Test</h1>
          <p className="mt-2 text-base text-gray-500">
            Read the sentence below out loud while recording your voice.
          </p>
        </motion.div>

        {/* Instructions */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="mt-8 rounded-2xl border border-[#FF6584]/15 bg-white p-6 shadow-sm"
        >
          <h2 className="mb-3 text-lg font-bold text-[#FF6584]">Instructions</h2>
          <ul className="space-y-2 text-sm text-gray-600">
            <li className="flex items-start gap-2">
              <span className="mt-0.5 inline-block h-2 w-2 flex-shrink-0 rounded-full bg-[#43E97B]" />
              Find a quiet place with minimal background noise.
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-0.5 inline-block h-2 w-2 flex-shrink-0 rounded-full bg-[#43E97B]" />
              Read the sentence displayed below out loud.
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-0.5 inline-block h-2 w-2 flex-shrink-0 rounded-full bg-[#43E97B]" />
              Press the microphone button to start and stop recording.
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-0.5 inline-block h-2 w-2 flex-shrink-0 rounded-full bg-[#FFB347]" />
              Speak at a natural pace -- don't rush!
            </li>
          </ul>
        </motion.div>

        {/* Prompt selector */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25 }}
          className="mt-8"
        >
          <div className="mb-3 flex items-center justify-between">
            <span className="text-sm font-semibold text-gray-500">
              Sentence {promptIndex + 1} of {READING_PROMPTS.length}
            </span>
            {!result && promptIndex < READING_PROMPTS.length - 1 && (
              <button
                onClick={handleNextPrompt}
                className="text-sm font-semibold text-[#6C63FF] transition-colors hover:text-[#5a52e0]"
              >
                Try a different sentence
              </button>
            )}
          </div>
          <TextPrompt text={currentPrompt} ageGroup={ageGroup} />
        </motion.div>

        {/* Recorder */}
        {!result && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35 }}
            className="mt-8"
          >
            <AudioRecorder onRecordingComplete={handleRecordingComplete} disabled={loading} />
          </motion.div>
        )}

        {/* Analyze Button */}
        {audioBlob && !result && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6 text-center"
          >
            <button
              onClick={handleAnalyze}
              className="inline-flex items-center gap-2 rounded-full bg-[#FF6584] px-8 py-3.5 text-lg font-bold text-white shadow-lg shadow-[#FF6584]/30 transition-all hover:scale-105 hover:bg-[#e8576f] active:scale-95"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              Analyze Speech
            </button>
          </motion.div>
        )}

        {/* Loading */}
        {loading && (
          <div className="mt-8">
            <LoadingSpinner message="Analyzing speech... hang tight!" />
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
            <SpeechResult result={result} />

            <div className="text-center">
              <button
                onClick={handleViewResults}
                className="inline-flex items-center gap-2 rounded-full bg-[#43E97B] px-8 py-3.5 text-lg font-bold text-white shadow-lg shadow-[#43E97B]/30 transition-all hover:scale-105 hover:bg-[#36d46a] active:scale-95"
              >
                View Results
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
