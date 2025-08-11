FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg git git-lfs python3 python3-pip python3-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip

WORKDIR /workspace

COPY app/requirements.txt /workspace/requirements.txt
RUN pip install -r /workspace/requirements.txt

COPY app /workspace/app

ENV HF_HOME=/workspace/.cache/huggingface
ENV TRANSFORMERS_CACHE=/workspace/.cache/huggingface/transformers
ENV HF_TOKEN=${HF_TOKEN}

EXPOSE 8000

CMD ["uvicorn", "app.main:api", "--host", "0.0.0.0", "--port", "8000"]
