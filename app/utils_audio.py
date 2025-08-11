import subprocess
import wave
import contextlib
import webrtcvad
import numpy as np
import soundfile as sf

TARGET_SR = 16000
TARGET_CHANNELS = 1

def run_ffmpeg_to_wav(in_path: str, out_path: str, sr: int = TARGET_SR):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", in_path,
        "-ac", str(TARGET_CHANNELS),
        "-ar", str(sr),
        out_path,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def get_duration_seconds(path: str) -> float:
    with contextlib.closing(wave.open(path, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        return frames / float(rate)

def read_wav_mono_16k(path: str):
    audio, sr = sf.read(path)
    if sr != TARGET_SR:
        raise ValueError(f"Expected {TARGET_SR} Hz, got {sr}")
    if audio.ndim > 1:
        audio = audio[:, 0]
    audio_int16 = (audio * 32767).astype(np.int16)
    return audio_int16, sr

def frame_generator(frame_ms, audio, sr):
    n = int(sr * (frame_ms / 1000.0))
    offset = 0
    byte_data = audio.tobytes()
    bytes_per_sample = 2
    frame_size = n * bytes_per_sample
    while offset + frame_size <= len(byte_data):
        yield byte_data[offset:offset + frame_size]
        offset += frame_size

def vad_segments(wav_path: str, aggressiveness: int = 2, frame_ms: int = 30, padding_ms: int = 300):
    vad = webrtcvad.Vad(aggressiveness)
    audio, sr = read_wav_mono_16k(wav_path)
    frames = list(frame_generator(frame_ms, audio, sr))
    num_padding = int(padding_ms / frame_ms)

    voiced_flags = [vad.is_speech(f, sr) for f in frames]
    segments = []
    start = None
    voiced_countdown = 0

    for i, is_voiced in enumerate(voiced_flags):
        t = i * (frame_ms / 1000.0)
        if is_voiced:
            if start is None:
                start = t
            voiced_countdown = num_padding
        else:
            if start is not None:
                if voiced_countdown > 0:
                    voiced_countdown -= 1
                else:
                    end = t
                    segments.append((start, end))
                    start = None

    if start is not None:
        end = len(frames) * (frame_ms / 1000.0)
        segments.append((start, end))

    merged = []
    for seg in segments:
        if not merged:
            merged.append(list(seg))
        else:
            prev = merged[-1]
            if seg[0] - prev[1] < 0.2:
                prev[1] = seg[1]
            else:
                merged.append(list(seg))

    return [(float(s), float(e)) for s, e in merged]
