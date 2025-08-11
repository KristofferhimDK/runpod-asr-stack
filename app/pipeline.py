import os
import tempfile
import os as _os

from .utils_audio import (
    run_ffmpeg_to_wav,
    vad_segments,
    get_duration_seconds,
    extract_segment,
)
from .models import load_asr

MAX_DURATION_SECONDS = int(os.getenv("MAX_DURATION_SECONDS", 120))


def transcribe_file(input_path: str):
    # 1) Normalize to mono 16 kHz WAV
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
        wav_path = tmp_wav.name
    run_ffmpeg_to_wav(input_path, wav_path)

    # 2) Duration guard
    duration = get_duration_seconds(wav_path)
    if duration > MAX_DURATION_SECONDS:
        raise ValueError(
            f"File duration {duration:.1f}s exceeds limit {MAX_DURATION_SECONDS}s"
        )

    # 3) VAD segments
    segments = vad_segments(wav_path)

    # 4) ASR per VAD segment (now slicing audio correctly)
    asr = load_asr()
    results = []
    temp_paths = []

    try:
        for (s, e) in segments:
            seg_wav = extract_segment(wav_path, s, e)
            temp_paths.append(seg_wav)

            out = asr(
                seg_wav,
                return_timestamps=True,
                chunk_length_s=30,
                stride_length_s=5,
            )
            text = out["text"] if isinstance(out, dict) else str(out)

            results.append(
                {
                    "start": float(s),
                    "end": float(e),
                    "speaker": "SPEAKER_00",  # will be real IDs in Milestone B
                    "text": text,
                }
            )
    finally:
        # cleanup temp segment files
        for p in temp_paths:
            try:
                _os.remove(p)
            except Exception:
                pass
        try:
            _os.remove(wav_path)
        except Exception:
            pass

    return {
        "duration_s": float(duration),
        "language": "da",
        "segments": results,
    }
