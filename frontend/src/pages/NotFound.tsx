import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

export default function NotFound() {
  return (
    <div className="flex min-h-[80vh] flex-col items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h1 className="text-8xl font-bold" style={{ color: '#6C63FF' }}>
          404
        </h1>
        <h2 className="mt-4 text-2xl font-semibold text-gray-700">
          Page Not Found
        </h2>
        <p className="mt-2 text-gray-500">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <div className="mt-8 flex gap-4 justify-center">
          <Link
            to="/"
            className="rounded-xl px-6 py-3 text-white font-semibold shadow-lg transition hover:opacity-90"
            style={{ backgroundColor: '#6C63FF' }}
          >
            Go Home
          </Link>
          <Link
            to="/dashboard"
            className="rounded-xl px-6 py-3 font-semibold border-2 transition hover:bg-gray-50"
            style={{ borderColor: '#6C63FF', color: '#6C63FF' }}
          >
            Dashboard
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
