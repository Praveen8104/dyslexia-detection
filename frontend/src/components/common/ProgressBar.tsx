import { motion } from "framer-motion";

interface ProgressBarProps {
  currentStep: number;
  totalSteps: number;
  labels?: string[];
}

export default function ProgressBar({ currentStep, totalSteps, labels }: ProgressBarProps) {
  const percentage = Math.min((currentStep / totalSteps) * 100, 100);

  return (
    <div className="w-full font-[Comic_Neue]">
      {/* Step indicators */}
      {labels && labels.length > 0 && (
        <div className="mb-3 flex justify-between">
          {labels.map((label, index) => {
            const stepNum = index + 1;
            const isCompleted = stepNum < currentStep;
            const isCurrent = stepNum === currentStep;

            return (
              <div key={index} className="flex flex-col items-center gap-1" style={{ width: `${100 / labels.length}%` }}>
                <motion.div
                  initial={{ scale: 0.8 }}
                  animate={{
                    scale: isCurrent ? 1.15 : 1,
                    backgroundColor: isCompleted
                      ? "#43E97B"
                      : isCurrent
                        ? "#6C63FF"
                        : "#D1D5DB",
                  }}
                  transition={{ type: "spring", stiffness: 300, damping: 20 }}
                  className="flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold text-white"
                >
                  {isCompleted ? (
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    stepNum
                  )}
                </motion.div>
                <span
                  className="text-xs font-semibold text-center leading-tight"
                  style={{ color: isCurrent ? "#6C63FF" : "#9CA3AF" }}
                >
                  {label}
                </span>
              </div>
            );
          })}
        </div>
      )}

      {/* Progress track */}
      <div className="relative h-4 w-full overflow-hidden rounded-full bg-gray-200">
        <motion.div
          className="absolute inset-y-0 left-0 rounded-full"
          style={{
            background: "linear-gradient(90deg, #6C63FF 0%, #43E97B 100%)",
          }}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.6, ease: "easeOut" }}
        />
      </div>

      {/* Text summary */}
      <div className="mt-2 flex items-center justify-between text-sm font-semibold" style={{ color: "#6C63FF" }}>
        <span>
          Step {currentStep} of {totalSteps}
        </span>
        <span>{Math.round(percentage)}%</span>
      </div>
    </div>
  );
}
