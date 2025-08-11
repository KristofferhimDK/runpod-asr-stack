import os
from transformers import pipeline
from huggingface_hub import login

ASR_MODEL_ID = os.getenv("ASR_MODEL_ID", "syvai/hviske-v3-conversation")
HF_TOKEN = os.getenv("HF_TOKEN")

_asr_pipe = None

def load_asr():
    global _asr_pipe
    if _asr_pipe is not None:
        return _asr_pipe

    if HF_TOKEN:
        try:
            login(token=HF_TOKEN)
        except Exception:
            pass

    _asr_pipe = pipeline(
        task="automatic-speech-recognition",
        model=ASR_MODEL_ID,
        device_map="auto",
        chunk_length_s=30,
        stride_length_s=5,
        return_timestamps=True,
    )
    return _asr_pipe
