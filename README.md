# DyslexAI

A web-based dyslexia screening tool for children aged 6-12 that identifies early indicators of dyslexia through **handwriting image analysis** and **speech pattern analysis** using a hybrid approach combining deep learning with domain-specific heuristics.

Built as a B.Tech final-year project.

## Overview

DyslexAI analyses two key modalities associated with dyslexia:

1. **Handwriting** -- Detects letter reversals, irregular spacing, poor baseline alignment, inconsistent letter sizes, and low stroke quality using a CNN (EfficientNetB0) blended with OpenCV-based image heuristics.
2. **Speech** -- Measures reading speed (WPM), hesitation count, and silence ratio from an audio recording using a CNN-BiLSTM model blended with age-appropriate rule-based scoring.

Both scores are combined into a single risk level (**Low / Moderate / High**) with actionable recommendations for parents and educators.

> **Disclaimer:** This is a screening tool, not a clinical diagnosis. It identifies potential indicators of dyslexia based on handwriting and speech patterns. A positive result does not confirm dyslexia, and a negative result does not rule it out. Results should always be interpreted by a qualified professional.

## Features

- **Handwriting Analysis** -- Upload a photo of handwriting; the system extracts 8 visual features (spacing, alignment, stroke quality, size consistency, symmetry, ink density, contour regularity, reversal signs) and blends them with CNN predictions.
- **Speech Analysis** -- Record a child reading a sentence aloud; the system computes reading fluency metrics and blends them with CNN-BiLSTM predictions. WPM thresholds adjust automatically by the child's age.
- **Combined Risk Scoring** -- Weighted combination (55% handwriting, 45% speech) producing a 0-100 risk score with three tiers: Low (0-30), Moderate (31-60), High (61-100).
- **Dashboard** -- View all test sessions with detailed results, animated risk gauges, and per-module breakdowns.
- **Child Profiles** -- Create profiles with name, age (3-18), and gender for age-appropriate analysis thresholds.
- **Responsive UI** -- Works on desktop and mobile with smooth animations and a child-friendly design.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript 5.9, Vite 7, Tailwind CSS 4, Framer Motion 12 |
| Backend | Python 3.11, Flask 3.0, Flask-SQLAlchemy, Gunicorn |
| ML/AI | TensorFlow/Keras 2.15, OpenCV, librosa, pydub |
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
│   │   ├── services/api.ts     Axios API client with error interceptor
│   │   └── types/index.ts      TypeScript interfaces
│   ├── vite.config.ts
│   └── Dockerfile
├── backend/
│   ├── app/
│   │   ├── __init__.py         Flask app factory, CORS, DB init
│   │   ├── routes/             users, handwriting, speech, results
│   │   ├── models/             SQLAlchemy models (User, TestSession, HandwritingTest, SpeechTest)
│   │   └── ml/
│   │       ├── handwriting/    preprocessor (CLAHE, deskew, Otsu), predictor (8-feature heuristics + CNN)
│   │       ├── speech/         audio_processor, feature_extractor (MFCC+delta), predictor (rule-based + CNN-BiLSTM)
│   │       └── scoring/        combined_scorer (weighted blend, risk classification, recommendations)
│   ├── training/               Training scripts and Jupyter notebooks
│   ├── saved_models/           Trained .keras model files
│   ├── tests/                  51 pytest test cases
│   ├── data/                   Datasets (gitignored)
│   └── Dockerfile
├── docker-compose.yml
└── docs/                       Demo guide, sample images, project documentation
```

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- ffmpeg (required for audio format conversion)

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

The API server starts at http://localhost:5001.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 in your browser. The Vite dev server proxies `/api` requests to the backend automatically.

### Docker (Production)

```bash
docker-compose up --build
```

This starts the backend on port 5000 and the frontend (via nginx) on port 80.

### Running Tests

```bash
cd backend
source venv/bin/activate
python -m pytest tests/ -v
```

51 test cases covering:
- User API (creation, validation, age range enforcement)
- Results API (combining, boundaries, invalid inputs)
- Combined Scorer (all risk tiers, boundary values, clamping)
- Handwriting validation (file type, size, session checks)
- Speech validation (audio format, session checks)
- Preprocessor (image shape, invalid paths)
- Audio processor (silence ratio, hesitations, reading speed)
- Feature extractor (MFCC output shape, short audio padding)

## ML Models

### Handwriting -- EfficientNetB0 (Transfer Learning)

| Property | Value |
|----------|-------|
| Dataset | [Kaggle Dyslexia Handwriting Dataset](https://www.kaggle.com/datasets/drizasazanitaisa/dyslexia-handwriting-dataset) -- 56,700+ images |
| Architecture | Input (224x224x1) -> EfficientNetB0 (ImageNet) -> GlobalAvgPool -> Dense(128) -> Dense(3, softmax) |
| Classes | Normal, Reversal, Corrected |
| Training | 2-phase: freeze base, then fine-tune last 40 layers |
| Test Accuracy | 87.9% |
| Preprocessing | Grayscale -> CLAHE -> Deskew (min-area rectangle) -> Otsu binarization -> Median blur -> Resize -> Normalize |

**Hybrid scoring:** The CNN provides 30% of the handwriting score. The remaining 70% comes from OpenCV-based heuristic analysis of 8 features:

1. Ink density (sparse/dense writing detection)
2. Connected component analysis (letter count and distribution)
3. Size consistency (coefficient of variation of letter heights)
4. Baseline alignment (residual deviation from linear fit)
5. Spacing regularity (gap coefficient of variation)
6. Stroke quality (circularity measure of contours)
7. Left-right symmetry (reversal/mirror writing indicator)
8. Risk distribution (reversal vs. corrected probability weighting)

**Why hybrid?** The CNN was trained on individual 32x32 letter images, but real-world input is a full handwriting photo. The heuristic analysis compensates for this domain gap by extracting features that the CNN cannot capture from resized whole-page images.

```bash
# Download dataset and train
kaggle datasets download -d drizasazanitaisa/dyslexia-handwriting-dataset
cd backend && python training/train_handwriting.py
```

### Speech -- CNN-BiLSTM Hybrid

| Property | Value |
|----------|-------|
| Dataset | [TORGO Dysarthria Dataset](https://www.kaggle.com/datasets/poojag718/dysarthria-and-nondysarthria-speech-dataset) -- 8,214 audio files |
| Architecture | Input (200x39 MFCC) -> Conv1D(64) -> Conv1D(128) -> BiLSTM(64) -> Dense(32) -> Dense(2, softmax) |
| Classes | Normal, At-Risk |
| Features | 13 MFCCs + 13 delta + 13 delta-delta = 39 features per frame |
| Test Accuracy | 98.4% |

**Hybrid scoring:** The CNN-BiLSTM provides 35% of the speech score. The remaining 65% comes from rule-based heuristics:

| Metric | How it works |
|--------|-------------|
| Reading speed (WPM) | Compared against age-appropriate thresholds (6yo: 60 WPM, 12yo: 140 WPM) |
| Hesitation count | Pauses > 0.8s during reading |
| Silence ratio | Proportion of non-speech time in the recording |

**Why hybrid?** The ML model was trained on dysarthria (motor speech disorder) data, which differs from dyslexia (a phonological processing disorder). The rule-based heuristics — reading speed, hesitations, and silence ratio — are more directly relevant to dyslexia screening, so they are weighted higher.

```bash
# Download dataset and train
kaggle datasets download -d poojag718/dysarthria-and-nondysarthria-speech-dataset
cd backend && python training/train_speech.py
```

## API Reference

### Users

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|-------------|
| POST | `/api/users` | Create child profile + test session | `{ name, age, gender?, parent_email? }` |
| GET | `/api/users` | List all users | -- |
| GET | `/api/users/:id` | Get single user | -- |

### Analysis

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|-------------|
| POST | `/api/handwriting/analyze` | Analyze handwriting image | `multipart: image (PNG/JPG), session_id` |
| POST | `/api/speech/analyze` | Analyze speech recording | `multipart: audio (WAV/WebM/MP3/OGG/M4A/FLAC/AAC), session_id, expected_text` |

### Results

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|-------------|
| POST | `/api/results/combine` | Combine module scores into final risk | `{ session_id, handwriting_score?, speech_score? }` |
| GET | `/api/results/:session_id` | Get single test session with details | -- |
| GET | `/api/results/all` | Get all sessions (dashboard) | -- |
| GET | `/api/results/history/:user_id` | Get test history for a user | -- |

### Validation Rules

- Image uploads: PNG/JPG only, max 10 MB, file size validated before saving
- Audio uploads: WAV/WebM/MP3/OGG/M4A/FLAC/AAC, max 10 MB, auto-converted to WAV via ffmpeg
- Child age: must be integer between 3 and 18
- Scores: must be numeric, between 0 and 100

## Database Schema

```
User (id, name, age, gender, parent_email, created_at)
  └── TestSession (id, user_id, combined_score, risk_level, created_at)
        ├── HandwritingTest (id, session_id, image_path, prediction, confidence, markers, created_at)
        └── SpeechTest (id, session_id, audio_path, expected_text, prediction, confidence,
                        reading_speed_wpm, hesitation_count, silence_ratio, created_at)
```

## Application Flow

```
Home Page          Handwriting Test       Speech Test          Results
┌──────────┐      ┌──────────────┐      ┌──────────────┐     ┌──────────────┐
│ Create   │ ---> │ Upload image │ ---> │ Record audio │ --> │ Combined     │
│ profile  │      │ Analyze      │      │ Analyze      │     │ risk score   │
│ (name,   │      │ View markers │      │ View metrics │     │ Risk gauge   │
│  age)    │      │              │      │ (WPM, pauses)│     │ Recommen-    │
└──────────┘      └──────────────┘      └──────────────┘     │ dations      │
                   Step 1/3              Step 2/3             └──────┬───────┘
                                                              Step 3/3
                                                                     │
                                                              Dashboard
                                                             ┌──────────────┐
                                                             │ All sessions │
                                                             │ Test details │
                                                             │ Risk history │
                                                             └──────────────┘
```

## Risk Classification

| Level | Score Range | Meaning | Recommendation |
|-------|------------|---------|----------------|
| Low Risk | 0 -- 30 | No significant indicators detected | Continue monitoring; re-screen in 6-12 months if concerned |
| Moderate Risk | 31 -- 60 | Some indicators present | Consult a learning specialist; re-screen in 2-4 weeks to confirm |
| High Risk | 61 -- 100 | Multiple indicators present | Professional evaluation by educational psychologist strongly recommended |

## Limitations

- **Handwriting model domain gap** -- The CNN was trained on individual letter images (32x32), not full handwriting photos. The system compensates with OpenCV heuristics that analyse the full image, but accuracy may vary with handwriting quality and photo conditions.
- **Speech model domain mismatch** -- The ML model was trained on dysarthria (motor speech disorder) data, not dyslexia-specific data. Rule-based heuristics (WPM, hesitations, silence ratio) are weighted at 65% to compensate.
- **Age range** -- Thresholds are calibrated for children aged 6-12. Results outside this range should be interpreted with caution.
- **Language** -- Currently supports English-language handwriting and reading prompts only.
- **Not a clinical tool** -- This is a screening aid. It does not replace professional evaluation by qualified specialists.

## Future Scope

- Eye-tracking module for reading pattern analysis
- Speech-to-text transcription for word-level error analysis
- Multi-language support (Hindi, Telugu)
- Longitudinal tracking with progress graphs over time
- PDF report export for sharing with educators and clinicians
- Phonological awareness tasks (rhyming, syllable segmentation)

## License

This project was built for academic purposes as a B.Tech final-year project.
