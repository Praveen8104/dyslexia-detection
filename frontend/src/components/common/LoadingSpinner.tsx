import { motion } from "framer-motion";

interface LoadingSpinnerProps {
  message?: string;
}

export default function LoadingSpinner({ message }: LoadingSpinnerProps) {
  const dotColors = ["#6C63FF", "#FF6584", "#43E97B", "#FFB347"];

  return (
    <div className="flex flex-col items-center justify-center gap-6 py-12 ">
      {/* Bouncing dots */}
      <div className="flex items-center gap-3">
        {dotColors.map((color, i) => (
          <motion.span
            key={i}
            className="block h-4 w-4 rounded-full"
            style={{ backgroundColor: color }}
            animate={{ y: [0, -16, 0] }}
            transition={{
              duration: 0.6,
              repeat: Infinity,
              delay: i * 0.15,
              ease: "easeInOut",
            }}
          />
        ))}
      </div>

      {/* Optional message */}
      {message && (
        <motion.p
          className="text-lg font-semibold text-gray-500"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          {message}
        </motion.p>
      )}
    </div>
  );
}
