# runpod-asr-stack
Runpod ASR Stack
Denne applikation kører en dansk ASR-pipeline på Runpod Secure Cloud.

Funktioner
VAD (Voice Activity Detection) til at finde tale-segmenter
ASR (Automatic Speech Recognition) med modellen syvai/hviske-v3-conversation
API med FastAPI, endpoint /transcribe
Miljøvariabler
HF_TOKEN: Hugging Face Read Token
ASR_MODEL_ID: Modelnavn (default: syvai/hviske-v3-conversation)
MAX_DURATION_SECONDS: Maksimal varighed på lydfil (sekunder)
Start (på Runpod)
Byg image fra dette repository
Kør container med port 8000 åbnet
POST en lydfil til /transcribe for at få JSON-output
