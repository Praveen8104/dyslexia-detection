import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { createUser } from "../services/api";

const AGE_OPTIONS = Array.from({ length: 7 }, (_, i) => i + 6); // 6-12

const FEATURES = [
  {
    title: "Handwriting Analysis",
    description:
      "Upload a handwriting sample and our AI will detect letter reversals, irregular spacing, and other dyslexia markers.",
    icon: (
      <svg className="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M16.862 3.487a2.1 2.1 0 113.003 2.94L7.5 18.795l-4 1 1-4L16.862 3.487z" />
      </svg>
    ),
    color: "#6C63FF",
  },
  {
    title: "Speech Analysis",
    description:
      "Record your child reading aloud. We measure reading speed, hesitations, and fluency to assess risk.",
    icon: (
      <svg className="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 1a4 4 0 00-4 4v6a4 4 0 008 0V5a4 4 0 00-4-4z" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M19 11a7 7 0 01-14 0M12 19v3m-3 0h6" />
      </svg>
    ),
    color: "#FF6584",
  },
  {
    title: "Combined Report",
    description:
      "Both modules are combined into a single risk score with personalised recommendations for next steps.",
    icon: (
      <svg className="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 17v-2m3 2v-4m3 4v-6m-9 10h12a2 2 0 002-2V7a2 2 0 00-2-2H6a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
    color: "#43E97B",
  },
];

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.15, duration: 0.5, ease: "easeOut" },
  }),
};

export default function Home() {
  const navigate = useNavigate();

  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [age, setAge] = useState<number>(6);
  const [gender, setGender] = useState("");
  const [parentEmail, setParentEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError("Please enter the child's name.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const payload: { name: string; age: number; gender?: string; parent_email?: string } = {
        name: name.trim(),
        age,
      };
      if (gender) payload.gender = gender;
      if (parentEmail) payload.parent_email = parentEmail;

      const { user, session_id } = await createUser(payload);

      sessionStorage.setItem("session_id", String(session_id));
      sessionStorage.setItem("user_id", String(user.id));
      sessionStorage.setItem("user_name", user.name);
      sessionStorage.setItem("user_age", String(user.age));

      navigate("/handwriting-test");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Something went wrong. Please try again.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F0F4FF] ">
      {/* Hero Section */}
      <section className="relative overflow-hidden px-4 pb-16 pt-20 text-center sm:px-6 lg:px-8">
        {/* Decorative blobs */}
        <div className="pointer-events-none absolute -left-32 -top-32 h-96 w-96 rounded-full bg-[#6C63FF]/10 blur-3xl" />
        <div className="pointer-events-none absolute -right-32 bottom-0 h-80 w-80 rounded-full bg-[#FF6584]/10 blur-3xl" />

        <motion.div
          className="relative mx-auto max-w-3xl"
          initial="hidden"
          animate="visible"
        >
          <motion.h1
            variants={fadeUp}
            custom={0}
            className="text-4xl font-extrabold leading-tight text-gray-900 sm:text-5xl lg:text-6xl"
          >
            Dyslex
            <span className="text-[#6C63FF]">AI</span>{" "}
            <span className="text-[#FF6584]">Screening</span>
          </motion.h1>

          <motion.p
            variants={fadeUp}
            custom={1}
            className="mx-auto mt-6 max-w-xl text-lg leading-relaxed text-gray-600 sm:text-xl"
          >
            A friendly, AI-powered tool that checks handwriting and reading to help identify early signs of dyslexia in children aged 6 to 12.
          </motion.p>

          <motion.div variants={fadeUp} custom={2} className="mt-10">
            <button
              onClick={() => setShowForm(true)}
              className="inline-flex items-center gap-2 rounded-full bg-[#6C63FF] px-8 py-4 text-lg font-bold text-white shadow-lg shadow-[#6C63FF]/30 transition-all hover:scale-105 hover:bg-[#5a52e0] active:scale-95"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
              Start Screening
            </button>
          </motion.div>
        </motion.div>
      </section>

      {/* Child Profile Form Modal */}
      <AnimatePresence>
        {showForm && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowForm(false)}
          >
            <motion.div
              className="relative w-full max-w-md rounded-3xl bg-white p-8 shadow-2xl"
              initial={{ opacity: 0, scale: 0.9, y: 40 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 40 }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Close button */}
              <button
                onClick={() => setShowForm(false)}
                className="absolute right-4 top-4 rounded-full p-1 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
                aria-label="Close"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>

              <h2 className="mb-1 text-2xl font-bold text-gray-900">Child Profile</h2>
              <p className="mb-6 text-sm text-gray-500">
                Tell us a little about the child before we begin.
              </p>

              <form onSubmit={handleSubmit} className="space-y-5">
                {/* Name */}
                <div>
                  <label htmlFor="childName" className="mb-1 block text-sm font-semibold text-gray-700">
                    Name <span className="text-[#FF6584]">*</span>
                  </label>
                  <input
                    id="childName"
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Enter child's name"
                    className="w-full rounded-xl border-2 border-[#6C63FF]/20 bg-[#F0F4FF] px-4 py-3 text-gray-800 outline-none transition-colors focus:border-[#6C63FF] focus:bg-white"
                    required
                  />
                </div>

                {/* Age */}
                <div>
                  <label htmlFor="childAge" className="mb-1 block text-sm font-semibold text-gray-700">
                    Age <span className="text-[#FF6584]">*</span>
                  </label>
                  <select
                    id="childAge"
                    value={age}
                    onChange={(e) => setAge(Number(e.target.value))}
                    className="w-full rounded-xl border-2 border-[#6C63FF]/20 bg-[#F0F4FF] px-4 py-3 text-gray-800 outline-none transition-colors focus:border-[#6C63FF] focus:bg-white"
                  >
                    {AGE_OPTIONS.map((a) => (
                      <option key={a} value={a}>
                        {a} years old
                      </option>
                    ))}
                  </select>
                </div>

                {/* Gender (optional) */}
                <div>
                  <label htmlFor="childGender" className="mb-1 block text-sm font-semibold text-gray-700">
                    Gender <span className="text-xs text-gray-400">(optional)</span>
                  </label>
                  <select
                    id="childGender"
                    value={gender}
                    onChange={(e) => setGender(e.target.value)}
                    className="w-full rounded-xl border-2 border-[#6C63FF]/20 bg-[#F0F4FF] px-4 py-3 text-gray-800 outline-none transition-colors focus:border-[#6C63FF] focus:bg-white"
                  >
                    <option value="">Prefer not to say</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                {/* Parent Email (optional) */}
                <div>
                  <label htmlFor="parentEmail" className="mb-1 block text-sm font-semibold text-gray-700">
                    Parent Email <span className="text-xs text-gray-400">(optional)</span>
                  </label>
                  <input
                    id="parentEmail"
                    type="email"
                    value={parentEmail}
                    onChange={(e) => setParentEmail(e.target.value)}
                    placeholder="parent@example.com"
                    className="w-full rounded-xl border-2 border-[#6C63FF]/20 bg-[#F0F4FF] px-4 py-3 text-gray-800 outline-none transition-colors focus:border-[#6C63FF] focus:bg-white"
                  />
                </div>

                {/* Error */}
                {error && (
                  <motion.p
                    initial={{ opacity: 0, y: -4 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="rounded-lg bg-[#FF6584]/10 px-4 py-2 text-sm font-medium text-[#FF6584]"
                  >
                    {error}
                  </motion.p>
                )}

                {/* Submit */}
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full rounded-xl bg-[#6C63FF] py-3.5 text-lg font-bold text-white shadow-md shadow-[#6C63FF]/25 transition-all hover:bg-[#5a52e0] disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {loading ? "Setting up..." : "Begin Test"}
                </button>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Features Section */}
      <section className="mx-auto max-w-5xl px-4 pb-24 sm:px-6 lg:px-8">
        <motion.h2
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-12 text-center text-3xl font-bold text-gray-900"
        >
          How It Works
        </motion.h2>

        <div className="grid grid-cols-1 gap-8 sm:grid-cols-3">
          {FEATURES.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.15, duration: 0.5 }}
              whileHover={{ y: -6 }}
              className="flex flex-col items-center rounded-2xl bg-white p-8 text-center shadow-md transition-shadow hover:shadow-lg"
            >
              <div
                className="mb-5 flex h-16 w-16 items-center justify-center rounded-2xl"
                style={{ backgroundColor: `${feature.color}15`, color: feature.color }}
              >
                {feature.icon}
              </div>
              <h3 className="mb-2 text-xl font-bold text-gray-900">{feature.title}</h3>
              <p className="text-sm leading-relaxed text-gray-500">{feature.description}</p>
              <div className="mt-4 flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 text-sm font-bold text-gray-400">
                {index + 1}
              </div>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
}
