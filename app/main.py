import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from .pipeline import transcribe_file

api = FastAPI(title="Runpod ASR Stack", version="0.1.0")

@api.get("/health")
def health():
    return {"status": "ok"}

@api.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    try:
        suffix = "." + (file.filename.split(".")[-1] if "." in file.filename else "bin")
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_in:
            content = await file.read()
            tmp_in.write(content)
            in_path = tmp_in.name
        result = transcribe_file(in_path)
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
