# DyslexAI - Demo Setup Guide

## Quick Setup (5 minutes)

### Step 1: Clone the repo
```bash
git clone https://github.com/Praveen8104/dyslexia-detection.git
cd dyslexia-detection
```

### Step 2: Download ML models from Google Drive
Download both files from the shared Google Drive link and place them in `backend/saved_models/`:
- `handwriting_model.keras` (23 MB)
- `speech_model.keras` (1 MB)

### Step 3: Run setup
```bash
chmod +x setup.sh
./setup.sh
```
This installs all Python and Node.js dependencies automatically.

### Step 4: Start the app
```bash
chmod +x start.sh
./start.sh
```
Open **http://localhost:3000** in your browser.

---

## Prerequisites
- **Python 3.9+** — [Download](https://www.python.org/downloads/)
- **Node.js 18+** — [Download](https://nodejs.org/)
- **ffmpeg** — Required for audio processing
  - macOS: `brew install ffmpeg`
  - Ubuntu: `sudo apt install ffmpeg`
  - Windows: Download from https://ffmpeg.org/download.html

---

## Live Demo Script

### 1. Create a Child Profile
- Click **"Begin Screening"** on the home page
- Enter: Name = "Demo Child", Age = 8, Gender = any
- Click **"Begin Test"**

### 2. Handwriting Test
- Upload a handwriting sample image (use the sample images from Google Drive)
- Click **"Analyze Handwriting"**
- Show the results: prediction, confidence, risk score, detected markers
- Click **"Continue to Speech Test"**

### 3. Speech Test
- A reading prompt will appear on screen
- Click the **record button** and read the sentence aloud (or have someone read it)
- Click **stop** after reading
- Click **"Analyze Speech"**
- Show the results: prediction, WPM, hesitations, silence ratio
- Click **"View Results"**

### 4. Combined Results
- Show the **combined risk gauge** (0-100)
- Explain the weighting: 55% handwriting + 45% speech
- Show the recommendation text
- Click **"Go to Dashboard"**

### 5. Dashboard
- Show the test history table with all past sessions
- Click on a session to show detailed results

---

## Talking Points for Review

### Architecture
- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: Flask + SQLAlchemy + SQLite
- **ML Models**: TensorFlow/Keras

### Handwriting Model
- EfficientNetB0 (transfer learning from ImageNet)
- 3 classes: Normal, Reversal, Corrected
- Hybrid: 30% CNN + 70% OpenCV heuristics
- Trained on 56,000+ real handwriting images

### Speech Model
- CNN + Bidirectional LSTM
- 2 classes: Normal, At-Risk
- Hybrid: 35% ML + 65% rule-based heuristics
- Age-adjusted reading speed thresholds

### Combined Scoring
- Handwriting 55% + Speech 45%
- Risk levels: Low (0-30), Moderate (31-60), High (61-100)

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `python3: command not found` | Install Python 3.9+ |
| `node: command not found` | Install Node.js 18+ |
| Port 5001 already in use | `lsof -ti:5001 \| xargs kill -9` |
| Port 3000 already in use | `lsof -ti:3000 \| xargs kill -9` |
| Models not found warning | Download `.keras` files from Google Drive |
| Audio analysis fails | Install ffmpeg |
| `pip install` fails | Try `pip3 install -r requirements.txt` |

## Manual Start (if start.sh doesn't work)

**Terminal 1:**
```bash
cd backend
source venv/bin/activate    # On Windows: venv\Scripts\activate
python3 run.py
```

**Terminal 2:**
```bash
cd frontend
npm run dev
```
