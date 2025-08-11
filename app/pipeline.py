import os
import tempfile
from .utils_audio import run_ffmpeg_to_wav, vad_segments, get_duration_seconds
from .models import load_asr

MAX_DURATION_SECONDS = int(os.getenv("MAX_DURATION_SECONDS", 120))

def transcribe_file(input_path: str):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
        wav_path = tmp_wav.name
    run_ffmpeg_to_wav(input_path, wav_path)

    duration = get_duration_seconds(wav_path)
    if duration > MAX_DURATION_SECONDS:
        raise ValueError(f"File duration {duration:.1f}s exceeds limit {MAX_DURATION_SECONDS}s")

    segments = vad_segments(wav_path)

    asr = load_asr()
    results = []
    for (s, e) in segments:
        out = asr(wav_path, return_timestamps=True, chunk_length_s=30, stride_length_s=5)
        text = out["text"] if isinstance(out, dict) else str(out)
        results.append({
            "start": float(s),
            "end": float(e),
            "speaker": "SPEAKER_00",
            "text": text,
        })

    return {
        "duration_s": float(duration),
        "language": "da",
        "segments": results,
    }
