import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/common/Navbar';
import ErrorBoundary from './components/common/ErrorBoundary';
import Home from './pages/Home';
import HandwritingTest from './pages/HandwritingTest';
import SpeechTest from './pages/SpeechTest';
import Results from './pages/Results';
import Dashboard from './pages/Dashboard';
import TestDetailPage from './pages/TestDetailPage';
import NotFound from './pages/NotFound';

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <div className="min-h-screen" style={{ backgroundColor: '#F0F4FF' }}>
          <Navbar />
          <main className="pt-4 pb-12">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/handwriting-test" element={<HandwritingTest />} />
              <Route path="/speech-test" element={<SpeechTest />} />
              <Route path="/results" element={<Results />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/dashboard/test/:sessionId" element={<TestDetailPage />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </main>
        </div>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
