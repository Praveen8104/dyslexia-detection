# DyslexAI

A web-based dyslexia screening tool for children (ages 6–12) that detects dyslexia indicators through **handwriting image analysis** and **speech analysis** using machine learning.

Built as a final-year B.Tech project.

## Features

- **Handwriting Analysis** — Upload a handwriting image and get predictions using a MobileNetV2 CNN combined with OpenCV-based heuristics (letter spacing, baseline alignment, size consistency, stroke quality, reversal detection)
- **Speech Analysis** — Record a child reading a sentence aloud and get predictions using a CNN-LSTM model combined with rule-based heuristics (reading speed, hesitation count, silence ratio)
- **Combined Risk Scoring** — Weighted combination of handwriting (55%) and speech (45%) scores with risk levels: Low (0–30), Moderate (31–60), High (61–100)
- **Dashboard** — View all test sessions with detailed results, risk gauges, and per-module breakdowns
- **Child Profiles** — Create profiles with name, age, and gender for age-appropriate analysis thresholds

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, Framer Motion |
| Backend | Python 3.10, Flask 3.0, SQLAlchemy |
| ML | TensorFlow/Keras 2.15, OpenCV, librosa |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Deployment | Docker Compose, nginx |

## Project Structure

```
dyslexia-detection/
├── frontend/
│   ├── src/
│   │   ├── pages/              Home, Dashboard, HandwritingTest, SpeechTest, Results, TestDetailPage
│   │   ├── components/
│   │   │   ├── common/         Navbar, LoadingSpinner, ErrorBoundary, ScoreCard, ProgressBar
│   │   │   ├── handwriting/    ImageUploader, HandwritingPreview, HandwritingResult
│   │   │   ├── speech/         AudioRecorder, TextPrompt, SpeechResult
│   │   │   └── dashboard/      TestHistory, TestDetail, RiskGauge, CombinedReport
│   │   ├── hooks/              useImageUpload, useAudioRecorder
│   │   ├── services/api.ts     Axios API client
│   │   └── types/index.ts      TypeScript interfaces
│   ├── vite.config.ts
│   └── Dockerfile
├── backend/
│   ├── app/
│   │   ├── routes/             users, handwriting, speech, results
│   │   ├── models/             SQLAlchemy models (User, TestSession, HandwritingTest, SpeechTest)
│   │   └── ml/
│   │       ├── handwriting/    preprocessor, cnn_model, predictor
│   │       ├── speech/         audio_processor, feature_extractor, speech_model, predictor
│   │       └── scoring/        combined_scorer
│   ├── training/               Training scripts and notebooks
│   ├── saved_models/           Trained .keras model files (gitignored)
│   ├── data/                   Datasets (gitignored)
│   └── Dockerfile
└── docker-compose.yml
```

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- ffmpeg (`brew install ffmpeg` on macOS)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run --port 5001
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 in your browser. The frontend proxies API calls to the backend.

### Docker

```bash
docker-compose up --build
```

## ML Models

### Handwriting — MobileNetV2 (Transfer Learning)

- **Dataset**: [Kaggle Dyslexia Handwriting Dataset](https://www.kaggle.com/datasets/drizasazanitaisa/dyslexia-handwriting-dataset) — 56,700+ real handwriting images
- **Architecture**: Input (128x128x1) → Conv2D (1→3ch) → MobileNetV2 (ImageNet) → GlobalAvgPool → Dense(128) → Dense(3, softmax)
- **Classes**: Normal, Reversal, Corrected
- **Training**: 2-phase — freeze base then fine-tune last 30 layers
- **Test Accuracy**: 87.9%
- **Hybrid approach**: 30% CNN + 70% OpenCV heuristics (spacing, alignment, stroke quality, size consistency)

```bash
# Download dataset
kaggle datasets download -d drizasazanitaisa/dyslexia-handwriting-dataset

# Train
cd backend
python training/train_handwriting.py
```

### Speech — CNN-LSTM Hybrid

- **Dataset**: [TORGO Dysarthria Dataset](https://www.kaggle.com/datasets/poojag718/dysarthria-and-nondysarthria-speech-dataset) — 8,214 audio files
- **Architecture**: Input (200x39 MFCC) → Conv1D(64) → Conv1D(128) → LSTM(64) → Dense(32) → Dense(2, softmax)
- **Classes**: Normal, At-Risk
- **Features**: 13 MFCCs + 13 delta + 13 delta-delta = 39 features per frame
- **Test Accuracy**: 98.4%
- **Hybrid approach**: 35% CNN-LSTM + 65% rule-based heuristics (WPM thresholds by age, hesitation count, silence ratio)

```bash
# Download dataset
kaggle datasets download -d poojag718/dysarthria-and-nondysarthria-speech-dataset

# Train
cd backend
python training/train_speech.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users` | Create child profile |
| GET | `/api/users` | List all users |
| POST | `/api/handwriting/analyze` | Upload image → handwriting prediction |
| POST | `/api/speech/analyze` | Upload audio → speech prediction |
| POST | `/api/results/combine` | Combine scores → final risk level |
| GET | `/api/results/<session_id>` | Get single test session |
| GET | `/api/results/all` | Get all test sessions |
| GET | `/api/results/history/<user_id>` | Get test history for a user |

## Database Schema

```
User (id, name, age, gender, parent_email, created_at)
  └── TestSession (id, user_id, combined_score, risk_level, created_at)
        ├── HandwritingTest (id, session_id, image_path, prediction, confidence, markers)
        └── SpeechTest (id, session_id, audio_path, expected_text, prediction, confidence,
                        reading_speed_wpm, hesitation_count, silence_ratio)
```

## Screenshots

The app uses a clean, modern UI with the Inter font, animated risk gauges, and responsive design for both desktop and mobile.

## Limitations

- Handwriting model trained on individual letter images — uses OpenCV heuristics to supplement analysis of full handwriting photos
- Speech model trained on dysarthria (motor speech disorder) data — uses rule-based heuristics weighted higher for dyslexia-specific indicators
- No eye-tracking module yet (planned for future scope)
- Not a clinical diagnostic tool — results should be interpreted by a qualified professional

## Disclaimer

This is a screening tool, not a clinical diagnosis. Results should be interpreted by a qualified professional.
