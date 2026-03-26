import { motion } from "framer-motion";
import { useAudioRecorder } from "../../hooks/useAudioRecorder";
import { useEffect } from "react";

interface AudioRecorderProps {
  onRecordingComplete: (blob: Blob) => void;
  disabled?: boolean;
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60)
    .toString()
    .padStart(2, "0");
  const s = (seconds % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

export default function AudioRecorder({
  onRecordingComplete,
  disabled = false,
}: AudioRecorderProps) {
  const {
    isRecording,
    duration,
    audioBlob,
    audioUrl,
    error: micError,
    startRecording,
    stopRecording,
    resetRecording,
  } = useAudioRecorder();

  useEffect(() => {
    if (audioBlob) {
      onRecordingComplete(audioBlob);
    }
  }, [audioBlob, onRecordingComplete]);

  const handleToggle = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <div className="flex w-full flex-col items-center gap-6 rounded-2xl bg-white p-8 shadow-lg">
      {/* Record / Stop button */}
      <button
        onClick={handleToggle}
        disabled={disabled}
        className="group relative flex h-20 w-20 items-center justify-center rounded-full transition-shadow focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
        style={{
          backgroundColor: isRecording ? "#FF6584" : "#6C63FF",
          boxShadow: isRecording
            ? "0 0 0 0 rgba(255,101,132,0.5)"
            : "0 4px 14px rgba(108,99,255,0.4)",
        }}
        aria-label={isRecording ? "Stop recording" : "Start recording"}
      >
        {/* Pulsing ring when recording */}
        {isRecording && (
          <motion.span
            className="absolute inset-0 rounded-full bg-[#FF6584]"
            animate={{ scale: [1, 1.4], opacity: [0.5, 0] }}
            transition={{ duration: 1, repeat: Infinity, ease: "easeOut" }}
          />
        )}

        {isRecording ? (
          /* Stop icon */
          <span className="relative z-10 h-6 w-6 rounded-sm bg-white" />
        ) : (
          /* Mic icon */
          <svg
            className="relative z-10 h-8 w-8 text-white"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 1a4 4 0 00-4 4v6a4 4 0 008 0V5a4 4 0 00-4-4z"
            />
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M19 11a7 7 0 01-14 0M12 19v3m-3 0h6"
            />
          </svg>
        )}
      </button>

      {/* Status label and timer */}
      <div className="flex flex-col items-center gap-1">
        <p className="text-sm font-medium text-gray-500">
          {isRecording
            ? "Recording..."
            : audioUrl
              ? "Recording complete"
              : "Tap to record"}
        </p>
        {(isRecording || duration > 0) && (
          <p className="font-mono text-lg font-semibold text-gray-700">
            {formatTime(duration)}
          </p>
        )}
      </div>

      {/* Microphone error */}
      {micError && (
        <motion.div
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md rounded-lg bg-[#FF6584]/10 px-4 py-3 text-center text-sm font-medium text-[#FF6584]"
        >
          {micError}
        </motion.div>
      )}

      {/* Playback and reset */}
      {audioUrl && !isRecording && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex w-full flex-col items-center gap-3"
        >
          <audio controls src={audioUrl} className="w-full max-w-md" />
          <button
            onClick={resetRecording}
            className="rounded-lg px-4 py-2 text-sm font-medium text-[#6C63FF] transition-colors hover:bg-[#6C63FF]/10"
          >
            Record again
          </button>
        </motion.div>
      )}
    </div>
  );
}
