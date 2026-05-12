# Transcript Summarizer API

A lightweight, production-style REST API that uses an LLM to automatically analyze customer support transcripts.

Instead of a human reading thousands of conversations manually, this tool processes them instantly and returns structured, actionable data.

---

## What It Does

Send a support transcript to the API and receive:

| Field | Description |
|---|---|
| `summary` | A concise summary of the conversation |
| `sentiment` | Overall customer sentiment (`positive`, `neutral`, `negative`) |
| `risk_level` | Risk of churn or escalation (`low`, `medium`, `high`) |
| `action_items` | List of specific follow-up actions identified |

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
├── analyzer.py       # OpenAI integration and prompt logic
├── models.py         # Pydantic models for request/response
├── requirements.txt  # Python dependencies
├── .env.example      # Environment variable template
└── .gitignore
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/transcript-summarizer-api.git
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

Analyzes a customer support transcript.

**Request body:**
```json
{
  "transcript": "Agent: Hello, how can I help you today?..."
}
```

**Response:**
```json
{
  "summary": "The customer contacted support regarding a delayed reimbursement...",
  "sentiment": "negative",
  "risk_level": "high",
  "action_items": [
    "Escalate reimbursement case to finance team",
    "Follow up with customer within 24 hours"
  ]
}
```

---

## Example Test (PowerShell)

```powershell
$body = @{transcript = "Agent: Hello how can I help you today? Customer: My reimbursement has been delayed for two weeks and I want to cancel my policy. Agent: I apologize. I will escalate this immediately."} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/analyze" -Method Post -ContentType "application/json" -Body $body | ConvertTo-Json
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
