import { useState, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface ImageUploaderProps {
  onImageSelected: (file: File) => void;
  disabled?: boolean;
}

const ACCEPTED_TYPES = ["image/png", "image/jpeg", "image/jpg"];

const ImageUploader: React.FC<ImageUploaderProps> = ({
  onImageSelected,
  disabled = false,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback(
    (file: File) => {
      if (!ACCEPTED_TYPES.includes(file.type)) {
        return;
      }
      setFileName(file.name);
      const url = URL.createObjectURL(file);
      setPreview((prev) => {
        if (prev) URL.revokeObjectURL(prev);
        return url;
      });
      onImageSelected(file);
    },
    [onImageSelected]
  );

  const handleDragOver = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      if (!disabled) setIsDragging(true);
    },
    [disabled]
  );

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      if (disabled) return;
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [disabled, handleFile]
  );

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const handleClick = () => {
    if (!disabled) inputRef.current?.click();
  };

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (preview) URL.revokeObjectURL(preview);
    setPreview(null);
    setFileName(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <div className="w-full">
      <input
        ref={inputRef}
        type="file"
        accept=".png,.jpg,.jpeg"
        className="hidden"
        onChange={handleInputChange}
        disabled={disabled}
      />

      <motion.div
        onClick={handleClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        whileHover={disabled ? {} : { scale: 1.01 }}
        whileTap={disabled ? {} : { scale: 0.99 }}
        className={`
          relative cursor-pointer rounded-2xl border-3 border-dashed p-8
          transition-colors duration-200 text-center
          ${
            disabled
              ? "border-gray-300 bg-gray-100 cursor-not-allowed opacity-60"
              : isDragging
              ? "border-[#6C63FF] bg-[#6C63FF]/10"
              : "border-[#6C63FF]/40 bg-[#F0F4FF] hover:border-[#6C63FF] hover:bg-[#6C63FF]/5"
          }
        `}
      >
        <AnimatePresence mode="wait">
          {preview ? (
            <motion.div
              key="preview"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="flex flex-col items-center gap-4"
            >
              <div className="relative rounded-xl overflow-hidden border-2 border-[#6C63FF]/20 shadow-md">
                <img
                  src={preview}
                  alt="Uploaded handwriting"
                  className="max-h-56 max-w-full object-contain"
                />
              </div>
              <p className="text-sm text-[#6C63FF] font-medium truncate max-w-[250px]">
                {fileName}
              </p>
              <button
                onClick={handleClear}
                disabled={disabled}
                className="
                  px-4 py-1.5 rounded-full text-sm font-semibold
                  bg-[#FF6584]/10 text-[#FF6584] hover:bg-[#FF6584]/20
                  transition-colors
                "
              >
                Remove & Choose Again
              </button>
            </motion.div>
          ) : (
            <motion.div
              key="placeholder"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="flex flex-col items-center gap-3"
            >
              {/* Upload icon */}
              <div className="w-16 h-16 rounded-full bg-[#6C63FF]/10 flex items-center justify-center">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="w-8 h-8 text-[#6C63FF]"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
              </div>

              <div>
                <p className="text-lg font-bold text-[#6C63FF]">
                  Drop your handwriting image here!
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  or <span className="underline text-[#FF6584] font-semibold">click to browse</span>
                </p>
              </div>

              <div className="flex gap-2 mt-1">
                {["PNG", "JPG", "JPEG"].map((fmt) => (
                  <span
                    key={fmt}
                    className="px-2 py-0.5 rounded-full bg-[#43E97B]/15 text-[#2db863] text-xs font-semibold"
                  >
                    {fmt}
                  </span>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
};

export default ImageUploader;
