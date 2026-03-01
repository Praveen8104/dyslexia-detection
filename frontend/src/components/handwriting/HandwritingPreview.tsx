import { motion } from "framer-motion";

interface HandwritingPreviewProps {
  imageUrl: string;
}

const HandwritingPreview: React.FC<HandwritingPreviewProps> = ({ imageUrl }) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="w-full rounded-2xl border-2 border-[#6C63FF]/20 bg-white shadow-lg overflow-hidden"
    >
      {/* Card header */}
      <div className="px-5 py-3 bg-[#F0F4FF] border-b border-[#6C63FF]/10 flex items-center gap-2">
        <div className="w-3 h-3 rounded-full bg-[#6C63FF]" />
        <h3 className="text-sm font-bold text-[#6C63FF]">Handwriting Sample</h3>
      </div>

      {/* Image area */}
      <div className="p-4 flex items-center justify-center bg-white min-h-[200px]">
        <img
          src={imageUrl}
          alt="Handwriting sample preview"
          className="max-w-full max-h-80 object-contain rounded-lg"
        />
      </div>
    </motion.div>
  );
};

export default HandwritingPreview;
