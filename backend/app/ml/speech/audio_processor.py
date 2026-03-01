import os
import tempfile
import numpy as np
import librosa
from pydub import AudioSegment


def _convert_to_wav(audio_path: str) -> str:
    """Convert any audio format to WAV using pydub/ffmpeg."""
    wav_path = audio_path.rsplit(".", 1)[0] + "_converted.wav"
    audio = AudioSegment.from_file(audio_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(wav_path, format="wav")
    return wav_path


def load_audio(audio_path: str, sr: int = 16000) -> tuple:
    """Load audio file and return signal and sample rate."""
    try:
        signal, sample_rate = librosa.load(audio_path, sr=sr)
    except Exception:
        # Convert non-WAV formats (WebM, Ogg, etc.) to WAV first
        wav_path = _convert_to_wav(audio_path)
        signal, sample_rate = librosa.load(wav_path, sr=sr)
        os.remove(wav_path)
    return signal, sample_rate


def detect_silence_segments(signal: np.ndarray, sr: int = 16000,
                            threshold_db: float = -40) -> list:
    """Detect segments of silence in audio."""
    intervals = librosa.effects.split(signal, top_db=abs(threshold_db))
    return intervals


def compute_silence_ratio(signal: np.ndarray, sr: int = 16000) -> float:
    """Compute ratio of silence to total audio duration."""
    intervals = detect_silence_segments(signal, sr)
    if len(intervals) == 0:
        return 1.0

    speech_frames = sum(end - start for start, end in intervals)
    total_frames = len(signal)
    return 1.0 - (speech_frames / total_frames)


def count_hesitations(signal: np.ndarray, sr: int = 16000,
                      min_pause_sec: float = 1.5) -> int:
    """Count number of pauses longer than min_pause_sec."""
    intervals = detect_silence_segments(signal, sr)
    if len(intervals) <= 1:
        return 0

    hesitations = 0
    for i in range(1, len(intervals)):
        gap_frames = intervals[i][0] - intervals[i - 1][1]
        gap_sec = gap_frames / sr
        if gap_sec >= min_pause_sec:
            hesitations += 1

    return hesitations


def estimate_reading_speed(signal: np.ndarray, sr: int = 16000,
                           expected_word_count: int = 10) -> float:
    """Estimate reading speed in words per minute."""
    duration_sec = len(signal) / sr
    if duration_sec == 0:
        return 0.0

    duration_min = duration_sec / 60.0
    return expected_word_count / duration_min
