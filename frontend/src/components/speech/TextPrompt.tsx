import { motion } from "framer-motion";

interface TextPromptProps {
  text: string;
  ageGroup?: string;
}

const ageFontSize: Record<string, string> = {
  "5-7": "text-3xl",
  "8-10": "text-2xl",
  "11-13": "text-xl",
  default: "text-2xl",
};

export default function TextPrompt({ text, ageGroup }: TextPromptProps) {
  const fontSize = ageGroup
    ? ageFontSize[ageGroup] || ageFontSize.default
    : ageFontSize.default;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full rounded-2xl border border-[#6C63FF]/20 bg-white p-8 shadow-lg"
    >
      <span className="mb-3 inline-block rounded-full bg-[#6C63FF]/10 px-3 py-1 text-sm font-semibold text-[#6C63FF]">
        Read this aloud:
      </span>

      <p
        className={`${fontSize} mt-4 leading-relaxed font-medium tracking-wide text-gray-800`}
      >
        {text}
      </p>

      {ageGroup && (
        <p className="mt-4 text-xs text-gray-400">Age group: {ageGroup}</p>
      )}
    </motion.div>
  );
}
