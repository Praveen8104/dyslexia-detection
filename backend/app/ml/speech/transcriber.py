"""Speech-to-text transcription and Word Error Rate computation.

Uses OpenAI Whisper (local model, no API key needed) to transcribe
audio and compare against expected text to detect reading errors
(substitutions, omissions, insertions) - key indicators of dyslexia.
"""

import logging
import re

logger = logging.getLogger(__name__)

# Try to import whisper; graceful fallback if not installed
_whisper = None
_whisper_model = None

def _load_whisper():
    global _whisper, _whisper_model
    if _whisper_model is not None:
        return _whisper_model
    try:
        import whisper
        _whisper = whisper
        _whisper_model = whisper.load_model("base")
        logger.info("Whisper 'base' model loaded successfully")
        return _whisper_model
    except ImportError:
        logger.warning(
            "openai-whisper not installed. "
            "Speech transcription disabled. Install with: pip install openai-whisper"
        )
        return None
    except Exception as e:
        logger.error(f"Failed to load Whisper model: {e}")
        return None


def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio file to text using Whisper.

    Args:
        audio_path: Path to audio file (WAV, MP3, WebM, etc.)

    Returns:
        Transcribed text (lowercase, stripped), or empty string if
        transcription is unavailable.
    """
    model = _load_whisper()
    if model is None:
        return ""

    try:
        result = model.transcribe(
            audio_path,
            language="en",
            fp16=False,
        )
        text = result.get("text", "").strip().lower()
        return text
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return ""


def _normalize_text(text: str) -> list:
    """Normalize text for comparison: lowercase, remove punctuation, split."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)  # remove punctuation
    text = re.sub(r"\s+", " ", text)     # collapse whitespace
    return text.split()


def compute_word_error_rate(reference: str, hypothesis: str) -> dict:
    """Compute Word Error Rate between expected and transcribed text.

    Uses minimum edit distance (Levenshtein) at the word level.

    Returns:
        dict with:
            - wer: float (0.0 = perfect, 1.0 = 100% errors)
            - substitutions: int (wrong words - e.g., "dog" read as "bog")
            - deletions: int (skipped words)
            - insertions: int (added words)
            - ref_words: list of reference words
            - hyp_words: list of hypothesis words
            - total_ref_words: int
    """
    ref_words = _normalize_text(reference)
    hyp_words = _normalize_text(hypothesis)

    if not ref_words:
        return {
            "wer": 0.0,
            "substitutions": 0,
            "deletions": 0,
            "insertions": 0,
            "ref_words": ref_words,
            "hyp_words": hyp_words,
            "total_ref_words": 0,
        }

    # Dynamic programming - minimum edit distance at word level
    n = len(ref_words)
    m = len(hyp_words)

    # dp[i][j] = (cost, substitutions, deletions, insertions)
    dp = [[(0, 0, 0, 0) for _ in range(m + 1)] for _ in range(n + 1)]

    for i in range(1, n + 1):
        dp[i][0] = (i, 0, i, 0)  # all deletions
    for j in range(1, m + 1):
        dp[0][j] = (j, 0, 0, j)  # all insertions

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if ref_words[i - 1] == hyp_words[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                # Substitution
                sub = dp[i - 1][j - 1]
                sub_cost = (sub[0] + 1, sub[1] + 1, sub[2], sub[3])

                # Deletion (word in ref but not in hyp - child skipped it)
                dele = dp[i - 1][j]
                del_cost = (dele[0] + 1, dele[1], dele[2] + 1, dele[3])

                # Insertion (word in hyp but not in ref - child added it)
                ins = dp[i][j - 1]
                ins_cost = (ins[0] + 1, ins[1], ins[2], ins[3] + 1)

                dp[i][j] = min(sub_cost, del_cost, ins_cost, key=lambda x: x[0])

    total_cost, subs, dels, ins = dp[n][m]
    wer = total_cost / n if n > 0 else 0.0

    return {
        "wer": round(min(wer, 1.0), 4),
        "substitutions": subs,
        "deletions": dels,
        "insertions": ins,
        "ref_words": ref_words,
        "hyp_words": hyp_words,
        "total_ref_words": n,
    }


def analyze_reading_errors(reference: str, hypothesis: str) -> dict:
    """High-level reading error analysis for dyslexia indicators.

    Returns a dict with WER metrics plus dyslexia-relevant interpretation.
    """
    if not hypothesis:
        return {
            "transcription": "",
            "wer": None,
            "substitutions": 0,
            "deletions": 0,
            "insertions": 0,
            "total_ref_words": len(_normalize_text(reference)),
            "reading_accuracy": None,
            "error_details": "Transcription unavailable (Whisper not installed)",
        }

    wer_result = compute_word_error_rate(reference, hypothesis)

    accuracy = round((1.0 - wer_result["wer"]) * 100, 1)

    # Interpret errors for dyslexia context
    details = []
    if wer_result["substitutions"] > 0:
        details.append(
            f"{wer_result['substitutions']} word(s) substituted "
            "(read differently from text)"
        )
    if wer_result["deletions"] > 0:
        details.append(
            f"{wer_result['deletions']} word(s) omitted (skipped while reading)"
        )
    if wer_result["insertions"] > 0:
        details.append(
            f"{wer_result['insertions']} word(s) inserted (added words not in text)"
        )
    if not details:
        details.append("All words read correctly")

    return {
        "transcription": hypothesis,
        "wer": wer_result["wer"],
        "substitutions": wer_result["substitutions"],
        "deletions": wer_result["deletions"],
        "insertions": wer_result["insertions"],
        "total_ref_words": wer_result["total_ref_words"],
        "reading_accuracy": accuracy,
        "error_details": "; ".join(details),
    }
