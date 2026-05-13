# Transcript Summarizer API

A lightweight, production-style REST API that uses an LLM to automatically analyze customer support transcripts.

Instead of a human reading thousands of conversations manually, this tool processes them instantly and returns structured, actionable data — regardless of transcript length.

---

## What It Does

Send a support transcript to the API and receive:

| Field | Description |
|---|---|
| `summary` | A concise summary of the conversation |
| `sentiment` | Overall customer sentiment (`positive`, `neutral`, `negative`) |
| `risk_level` | Risk of churn or escalation (`low`, `medium`, `high`) |
| `action_items` | List of specific follow-up actions identified |
| `was_chunked` | Whether the transcript was split into chunks for processing |
| `chunks_processed` | Number of chunks the transcript was split into |

---

## Transcript Chunking Pipeline

LLMs have context window limits. Long transcripts become expensive, reduce output quality, and can exceed those limits entirely.

This API solves that with an automatic chunking pipeline:

```
Transcript
   ↓
Split into overlapping chunks (default: 500 words, 50-word overlap)
   ↓
Analyze all chunks in parallel (asyncio.gather)
   ↓
Merge results:
  - Summary    → LLM combines partial summaries into one
  - Sentiment  → worst-case across all chunks
  - Risk level → highest risk across all chunks
  - Actions    → deduplicated union across all chunks
```

Short transcripts skip chunking entirely and go through a single LLM call. The `was_chunked` field in the response tells you which path was taken.

Chunk analysis runs with `asyncio.gather` — all chunks are sent to the OpenAI API simultaneously, so total latency equals the slowest single chunk rather than the sum of all of them.

---

## Tech Stack

- **Python** — core language
- **FastAPI** — REST API framework
- **OpenAI API** — GPT-4o-mini for transcript analysis
- **Pydantic** — request/response validation and typed models
- **Uvicorn** — ASGI server

---

## Project Structure

```
Transcript Summarizer API/
├── main.py           # FastAPI app — defines routes
├── analyzer.py       # OpenAI integration, chunking orchestration, merge logic
├── chunker.py        # Word-based transcript splitter with overlap
├── models.py         # Pydantic models for request/response
├── requirements.txt  # Python dependencies
├── .env.example      # Environment variable template
└── .gitignore
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/guillermolopezareal/transcript-summarizer-api.git
cd transcript-summarizer-api
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your environment variables

```bash
cp .env.example .env
```

Open `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-...your key here...
```

> You can get an API key at https://platform.openai.com/api-keys

### 5. Start the server

```bash
uvicorn main:app --reload
```

The API will be running at `http://localhost:8000`.

---

## API Endpoints

### `GET /health`

Health check — confirms the server is running.

**Response:**
```json
{ "status": "ok" }
```

---

### `POST /analyze`

Analyzes a customer support transcript. Automatically chunks long transcripts.

**Request body:**
```json
{
  "transcript": "Agent: Hello, how can I help you today?...",
  "chunk_size_words": 500
}
```

| Field | Type | Default | Description |
|---|---|---|---|
| `transcript` | string | required | The full text of the support transcript |
| `chunk_size_words` | integer | `500` | Max words per chunk (range: 10–2000) |

**Response:**
```json
{
  "summary": "The customer contacted support regarding a delayed order and a duplicate charge. Both issues were resolved — a replacement was shipped and a refund was issued.",
  "sentiment": "negative",
  "risk_level": "high",
  "action_items": [
    "Send express replacement with tracking number",
    "Process refund for duplicate charge within 3-5 business days"
  ],
  "was_chunked": true,
  "chunks_processed": 3
}
```

---

## Example Tests

### PowerShell — short transcript (no chunking)

```powershell
$body = @{
    transcript = "Agent: Hello how can I help you today? Customer: My reimbursement has been delayed for two weeks and I want to cancel my policy. Agent: I apologize. I will escalate this immediately."
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/analyze" -Method Post -ContentType "application/json" -Body $body
```

### PowerShell — force chunking

```powershell
$body = @{
    chunk_size_words = 30
    transcript = "Agent: Hello how can I help you today? Customer: My reimbursement has been delayed for two weeks and I want to cancel my policy. Agent: I apologize. I will escalate this immediately and follow up within 24 hours. Customer: Also I was charged twice this month. Agent: I can see that duplicate charge and will issue a refund within 3 to 5 business days. Customer: Thank you. Agent: Is there anything else I can help with? Customer: No that is all. Agent: Have a great day."
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/analyze" -Method Post -ContentType "application/json" -Body $body
```

---

## Interactive Docs

FastAPI generates automatic documentation at:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## Real-World Use Cases

- Insurance claim call analysis
- Bank support quality assurance
- Technical support escalation detection
- CRM integration for churn risk flagging
