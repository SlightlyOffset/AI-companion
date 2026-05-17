import torch
import os
import shutil
import uuid
from typing import List
from TTS.api import TTS
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import uvicorn
import io

os.environ["COQUI_TOS_AGREED"] = "1"

SPEAKERS_DIR = "speakers"
os.makedirs(SPEAKERS_DIR, exist_ok=True)

print("-> Loading XTTS v2 model... (This may take a minute)")
device = "cuda" if torch.cuda.is_available() else "cpu"
tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
print("✅ Model Loaded.")

app = FastAPI()

@app.get("/check_speaker/{speaker_id}")
async def check_speaker(speaker_id: str):
    speaker_path = os.path.join(SPEAKERS_DIR, speaker_id)
    if os.path.exists(speaker_path) and os.listdir(speaker_path):
        return {"exists": True, "speaker_id": speaker_id}
    return {"exists": False, "speaker_id": speaker_id}

@app.post("/upload_speaker")
async def upload_speaker(
    speaker_id: str = Form(...),
    files: List[UploadFile] = File(...)
):
    speaker_path = os.path.join(SPEAKERS_DIR, speaker_id)
    os.makedirs(speaker_path, exist_ok=True)

    # Clear existing files for this speaker
    for f in os.listdir(speaker_path):
        try: os.remove(os.path.join(speaker_path, f))
        except: pass

    for upload in files:
        file_path = os.path.join(speaker_path, upload.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload.file, buffer)

    print(f"✅ Speaker '{speaker_id}' registered with {len(files)} samples.")
    return {"status": "success", "speaker_id": speaker_id}

@app.post("/generate_tts")
async def generate_tts_endpoint(
    text: str = Form(...),
    language: str = Form("en"),
    speaker_id: str = Form(None)
):
    if not speaker_id:
        raise HTTPException(status_code=400, detail="speaker_id is required")

    speaker_path = os.path.join(SPEAKERS_DIR, speaker_id)
    if not os.path.exists(speaker_path):
        raise HTTPException(status_code=404, detail=f"Speaker '{speaker_id}' not found.")

    # Robustly find all audio samples (case-insensitive extension check)
    speaker_wavs = [
        os.path.join(speaker_path, f) 
        for f in os.listdir(speaker_path) 
        if f.lower().endswith((".wav", ".flac", ".mp3"))
    ]
    
    print(f"-> Generating TTS for '{speaker_id}' using {len(speaker_wavs)} samples.")
    if not speaker_wavs:
        print(f"❌ ERROR: No audio files found in {speaker_path}")
        print(f"   Directory contents: {os.listdir(speaker_path)}")
        raise HTTPException(status_code=400, detail=f"No valid audio samples found for speaker '{speaker_id}'")

    # Streaming generator
    def stream_audio():
        import numpy as np
        try:
            # 1. Pre-calculate conditioning latents from the speaker wavs
            gpt_cond_latent, speaker_embedding = tts_model.synthesizer.tts_model.get_conditioning_latents(audio_path=speaker_wavs)

            # 2. Start the stream using the pre-calculated latents
            chunks = tts_model.synthesizer.tts_model.inference_stream(
                text=text,
                language=language,
                gpt_cond_latent=gpt_cond_latent,
                speaker_embedding=speaker_embedding,
                stream_chunk_size=20
            )
            for chunk in chunks:
                # Convert float32 tensor to int16 for standard WAV compatibility
                chunk = chunk.cpu().numpy()
                chunk = (chunk * 32767).astype(np.int16)
                yield chunk.tobytes()
        except Exception as e:
            print(f"❌ ERROR during TTS generation: {str(e)}")
            import traceback
            traceback.print_exc()
            yield b"" # Yield empty bytes to close stream on error

    return StreamingResponse(stream_audio(), media_type="audio/l16; rate=24000")

def run_server(public_url):
    print("="*50)
    print(f"\n🚀 XTTS BRIDGE ONLINE!\n")
    print(f"URL: {public_url}\n")
    print("="*50)
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info", timeout_keep_alive=75)
