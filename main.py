from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from models import TranscriptRequest, TranscriptAnalysis
from analyzer import analyze_transcript

load_dotenv()

app = FastAPI(
    title="Transcript Summarizer API",
    description="Analyzes customer support transcripts using AI.",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=TranscriptAnalysis)
def analyze(request: TranscriptRequest):
    try:
        result = analyze_transcript(request.transcript)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
