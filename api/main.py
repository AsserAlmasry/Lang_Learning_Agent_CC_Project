from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Depends, Security
from fastapi.security import APIKeyHeader
import secrets as secrets_mod
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import time
import os
import io
import datetime
from dotenv import load_dotenv
from gtts import gTTS
import easyocr
from PIL import Image
import numpy as np
from groq import Groq
import tempfile


# Load env vars before importing agent
load_dotenv()

from core.agent import EnhancedLanguageLearningAgent
from utils.email_helper import send_feedback_email
from utils.email_templates import get_premium_report_html, get_quiz_report_html

app = FastAPI(title="Language Learning Agent API")

# ─── API Key Authentication ─────────────────────────────────────────────────
# The frontend must send this key in the X-API-Key header.
# Generate a strong key: python -c "import secrets; print(secrets.token_urlsafe(32))"
API_KEY = os.getenv("API_SECRET_KEY", "lang-agent-default-key-CHANGE-ME")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Validates the API key from the request header."""
    if not api_key or not secrets_mod.compare_digest(api_key, API_KEY):
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return api_key

# Initialize Prometheus Instrumentation
Instrumentator().instrument(app).expose(app)

# Allow requests from the Next.js frontend (local dev + Docker + Production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://lang-agent-asser.duckdns.org",
        "http://localhost:3000",
        "http://localhost",
        "http://frontend-ui:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store (Session ID -> Agent Instance)
sessions: Dict[str, EnhancedLanguageLearningAgent] = {}
start_times: Dict[str, float] = {}
SESSION_TTL_SECONDS = 3600  # 1 hour

def _cleanup_expired_sessions():
    """Remove sessions older than SESSION_TTL_SECONDS to prevent memory exhaustion."""
    now = time.time()
    expired = [sid for sid, t in start_times.items() if now - t > SESSION_TTL_SECONDS]
    for sid in expired:
        sessions.pop(sid, None)
        start_times.pop(sid, None)

# OCR Reader (singleton)
reader = easyocr.Reader(['en'], gpu=False)

class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=5000)
    intent_override: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float

class EmailQuizRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    score: int = Field(..., ge=0, le=100)
    total: int = Field(..., ge=1, le=100)

class EmailStatsRequest(BaseModel):
    session_id: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Language Learning Agent API is running."}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, _key: str = Depends(verify_api_key)):
    _cleanup_expired_sessions()
    if req.session_id not in sessions:
        sessions[req.session_id] = EnhancedLanguageLearningAgent()
        start_times[req.session_id] = time.time()
    
    agent = sessions[req.session_id]
    
    try:
        result = agent.process_query(req.message, intent_override=req.intent_override)
        return ChatResponse(
            response=result["response"],
            intent=result.get("intent", "unknown"),
            confidence=result.get("confidence", 0.0)
        )
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Failed to process your query. Please try again.")

@app.post("/api/tts")
async def tts(request: Request, _key: str = Depends(verify_api_key)):
    data = await request.json()
    text = data.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    
    try:
        tts_obj = gTTS(text=text, lang='en', slow=False)
        fp = io.BytesIO()
        tts_obj.write_to_fp(fp)
        fp.seek(0)
        return StreamingResponse(fp, media_type="audio/mpeg")
    except Exception as e:
        print(f"TTS Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate audio.")

@app.post("/api/ocr")
async def ocr(file: UploadFile = File(...), _key: str = Depends(verify_api_key)):
    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}")
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        image_np = np.array(image)
        
        ocr_results = reader.readtext(image_np, detail=1, paragraph=False)
        ocr_results.sort(key=lambda x: x[0][0][1])
        
        lines = []
        current_line = []
        last_y = -1
        y_threshold = 20
        
        for res in ocr_results:
            bbox, text, prob = res
            y = bbox[0][1]
            if last_y == -1 or abs(y - last_y) < y_threshold:
                current_line.append((bbox[0][0], text))
            else:
                current_line.sort(key=lambda x: x[0])
                lines.append(" ".join([t for x, t in current_line]))
                current_line = [(bbox[0][0], text)]
            last_y = y
        
        if current_line:
            current_line.sort(key=lambda x: x[0])
            lines.append(" ".join([t for x, t in current_line]))
            
        return {"transcript": "\n".join(lines)}
    except Exception as e:
        print(f"OCR Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process image.")

@app.post("/api/email/quiz")
async def email_quiz(req: EmailQuizRequest, _key: str = Depends(verify_api_key)):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    percentage = (req.score / req.total) * 100
    body = get_quiz_report_html("Student", req.score, req.total, percentage)
    
    success, msg = send_feedback_email(f"Interactive Quiz Results [{timestamp}]", body)
    if not success:
        print(f"Email Error: {msg}")
        raise HTTPException(status_code=500, detail="Failed to send email.")
    return {"status": "sent"}

@app.post("/api/email/stats")
async def email_stats(req: EmailStatsRequest, _key: str = Depends(verify_api_key)):
    if req.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    agent = sessions[req.session_id]
    start_time = start_times.get(req.session_id, time.time())
    duration = round((time.time() - start_time) / 60, 1)
    
    from collections import Counter
    # Extract intents from history
    intents = [m.get("intent", "CONVERSATION").upper() for m in agent.session_history if m.get("role") == "assistant"]
    counts = Counter(intents)
    
    total_queries = len([m for m in agent.session_history if m.get("role") == "user"])
    avg_confidence = 0.85 # Mocking confidence aggregation for now
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    body = get_premium_report_html("Student", duration, total_queries, avg_confidence, dict(counts))
    
    success, msg = send_feedback_email(f"Learning Session Summary [{timestamp}]", body)
    if not success:
        print(f"Email Error: {msg}")
        raise HTTPException(status_code=500, detail="Failed to send email.")
    return {"status": "sent"}

@app.post("/api/session/reset")
async def reset_session(req: Request, _key: str = Depends(verify_api_key)):
    data = await req.json()
    session_id = data.get("session_id")
    if session_id in sessions:
        sessions[session_id] = EnhancedLanguageLearningAgent()
        start_times[session_id] = time.time()
    return {"status": "reset"}
@app.post("/api/stt")
async def speech_to_text(file: UploadFile = File(...), _key: str = Depends(verify_api_key)):
    """Transcribes audio using Groq's Whisper model."""
    try:
        # Save uploaded file to a temporary file
        ext = os.path.splitext(file.filename)[1]
        if not ext:
            ext = ".webm"
            
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Initialize Groq client
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # Transcribe
        with open(tmp_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(tmp_path, audio_file.read()),
                model="whisper-large-v3",
                response_format="json",
                language="en",
                temperature=0.0,
                prompt="Transcribe the following English speech. The speech may be empty or contain background noise. Do not hallucinate."
            )
        
        file_size = os.path.getsize(tmp_path)
        print(f"STT DEBUG: Received audio file size: {file_size} bytes, extension: {ext}")
        
        # Cleanup
        os.unlink(tmp_path)
        
        text = transcription.text.strip()
        print(f"STT DEBUG: Raw Whisper transcription: '{text}'")
        
        return {"text": text}
    except Exception as e:
        print(f"STT Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to transcribe audio.")
