# DyslexAI - Dyslexia Detection Web Application

A web-based dyslexia screening tool for children (ages 6-12) that detects dyslexia indicators through **handwriting image analysis** (CNN) and **speech analysis** (audio processing + ML).

## Tech Stack

- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS + Framer Motion
- **Backend**: Python 3.10 + Flask 3.0
- **ML**: TensorFlow/Keras 2.15, OpenCV, librosa
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Deployment**: Docker Compose

## Quick Start

### Development Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:3000` and proxies API calls to `http://localhost:5000`.

### Docker Deployment
```bash
docker-compose up --build
```

## Training Models

1. Download datasets and place in `backend/data/`:
   - `handwriting/`: Kaggle Dyslexia Handwriting Dataset (subdirs: `Normal/`, `Reversal/`, `Corrected/`)
   - `speech/`: Audio files (subdirs: `Normal/`, `AtRisk/`)

2. Run training notebooks in `backend/training/`:
   - `handwriting_training.ipynb` - MobileNetV2 transfer learning
   - `speech_training.ipynb` - CNN-LSTM hybrid model

3. Trained models are saved to `backend/saved_models/`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users` | Create child profile |
| POST | `/api/handwriting/analyze` | Upload image for CNN prediction |
| POST | `/api/speech/analyze` | Upload audio for speech analysis |
| POST | `/api/results/combine` | Combine scores for final risk |
| GET | `/api/results/<session_id>` | Get test results |
| GET | `/api/results/history/<user_id>` | Get test history |

## Disclaimer

This is a screening tool, not a clinical diagnosis. Results should be interpreted by a qualified professional.
