# Transcript Summarizer API — Interview Documentation

## What I Built

A production-style REST API that uses a Large Language Model (LLM) to automatically analyze customer support transcripts. The API receives raw conversation text and returns structured, actionable data: a summary, sentiment classification, risk level, and a list of follow-up action items.

The goal was to simulate a real-world AI tool that a company could plug into their support operations to replace — or assist — manual quality assurance review.

---

## The Problem It Solves

Large companies (insurance, banking, telecom, healthcare) handle thousands of customer support calls and chats every day. These conversations are recorded and transcribed, but most companies can only review a small fraction of them manually.

This tool acts as an AI analyst. It reads transcripts automatically and returns structured data that can be:

- Stored in a database for reporting
- Used to flag high-risk customers before they churn
- Fed into a CRM like Salesforce to trigger follow-up workflows
- Used to evaluate agent performance at scale

Instead of a team of analysts reading conversations, the API processes them instantly.

---

## Tech Stack — What I Used and Why

### Python
The standard language for AI and backend API development. Fast to iterate, rich ecosystem, and the OpenAI SDK is Python-first.

### FastAPI
A modern Python web framework for building REST APIs. I chose it over Flask because:
- It has **automatic data validation** via Pydantic built in
- It auto-generates **interactive API documentation** (Swagger UI) at `/docs`
- It is **asynchronous by design**, making it production-ready and performant
- It enforces typed inputs and outputs, which reduces bugs

### OpenAI API (GPT-4o-mini)
The LLM that does the actual analysis. I used `gpt-4o-mini` specifically because:
- It is fast and cost-efficient — ideal for high-volume API calls
- It supports **JSON mode**, which forces the model to return valid JSON only
- It is capable enough to understand nuance, tone, and context in conversations

### Pydantic
A Python library for data validation using type annotations. It is used in two places:
1. **Request validation** — if the input transcript is missing or too short, FastAPI rejects it automatically before it ever reaches the LLM
2. **Response modeling** — the API response is defined as a typed Pydantic model with enums, so the output is always predictable and consistent

### Uvicorn
An ASGI server that runs the FastAPI application. It is the industry standard for serving FastAPI apps in development and production.

### python-dotenv
Loads environment variables from a `.env` file. This keeps secrets (like the OpenAI API key) out of the codebase and is a standard security practice.

---

## Project Architecture

```
Request (transcript text)
        │
        ▼
   FastAPI (main.py)
   - Receives POST /analyze
   - Validates request via Pydantic
        │
        ▼
   Analyzer (analyzer.py)
   - Builds the prompt
   - Calls OpenAI API with JSON mode
   - Parses the response
        │
        ▼
   Pydantic Model (models.py)
   - Validates the LLM output
   - Enforces enum values (sentiment, risk_level)
        │
        ▼
   Structured JSON Response
```

---

## File-by-File Breakdown

### `main.py` — The API Layer
This is the entry point of the application. It defines two endpoints:

- `GET /health` — a simple health check that returns `{"status": "ok"}`. This is a standard production pattern used by load balancers and monitoring tools to confirm the service is alive.
- `POST /analyze` — the core endpoint. It accepts a `TranscriptRequest` (validated by Pydantic), passes the transcript to the analyzer, and returns a `TranscriptAnalysis` object.

It also calls `load_dotenv()` at startup to load the OpenAI API key from the `.env` file.

### `analyzer.py` — The AI Layer
This is where the intelligence lives. It contains:

**The system prompt** — a carefully engineered instruction that tells the LLM exactly what role to play, what fields to return, what values are valid, and that it must respond in pure JSON only. This is called **prompt engineering**.

**The OpenAI API call** — configured with:
- `model="gpt-4o-mini"` — fast, cheap, capable
- `response_format={"type": "json_object"}` — JSON mode, forces valid JSON output
- `temperature=0.2` — low temperature means more consistent, deterministic responses (important for a production tool — you want reliable outputs, not creative ones)

**Response parsing** — the raw JSON string from the LLM is parsed and passed into the Pydantic model, which validates it before returning.

### `models.py` — The Data Layer
Defines three things:

- `SentimentLevel` — an enum with values `positive`, `neutral`, `negative`
- `RiskLevel` — an enum with values `low`, `medium`, `high`
- `TranscriptRequest` — the input model. Has one field: `transcript` (string, minimum 20 characters)
- `TranscriptAnalysis` — the output model. Has four fields: `summary` (string), `sentiment` (SentimentLevel), `risk_level` (RiskLevel), `action_items` (list of strings)

Using enums means the API will reject any response from the LLM that doesn't match the expected values — adding a layer of reliability.

---

## Key Concepts Demonstrated

### 1. Prompt Engineering
The system prompt in `analyzer.py` is not just a question — it is a precise instruction set. It tells the model:
- What role to play (AI quality assurance analyst)
- Exactly what fields to return and what they mean
- What valid values are for each field
- How to format the response (pure JSON, no markdown, no explanation)

The quality of the output depends entirely on the quality of the prompt. A vague prompt produces vague results. A precise prompt produces structured, reliable results.

### 2. Structured Outputs
Rather than asking the LLM to "describe" the transcript in free text, the API forces a structured JSON response. This is critical for production systems because:
- The output can be stored in a database
- It can be consumed by other systems programmatically
- It is predictable — the shape of the response never changes

JSON mode in the OpenAI API guarantees the response is always valid JSON, preventing parsing errors.

### 3. Input Validation
FastAPI + Pydantic automatically validate the incoming request. If someone sends an empty transcript, a number instead of a string, or a malformed request body, the API returns a clear `422 Unprocessable Entity` error before the LLM is ever called. This saves cost and prevents unnecessary API calls.

### 4. Environment Variable Management
The OpenAI API key is stored in a `.env` file which is excluded from version control via `.gitignore`. The `.env.example` file is committed as a safe template showing what variables are needed. This is a standard security practice — secrets never live in the codebase.

### 5. Production-Oriented Thinking
Several small decisions reflect production awareness:
- `/health` endpoint for monitoring
- Low temperature for consistent outputs
- Enums for constrained, predictable values
- Separation of concerns: routing (main.py), AI logic (analyzer.py), data models (models.py)
- Auto-generated API documentation at `/docs`

---

## How the API Call Works (Step by Step)

1. A client sends a `POST` request to `/analyze` with a JSON body containing the transcript text
2. FastAPI receives the request and Pydantic validates it against the `TranscriptRequest` model
3. The validated transcript is passed to `analyze_transcript()` in `analyzer.py`
4. The function constructs a chat completion request to OpenAI with the system prompt + the transcript
5. OpenAI processes the request and returns a JSON string
6. The JSON string is parsed and loaded into a `TranscriptAnalysis` Pydantic model
7. FastAPI serializes the model back to JSON and sends it as the HTTP response

---

## Why This Is Not Traditional NLP

Traditional NLP tools (like VADER, spaCy, or NLTK) work by:
- Matching keywords and patterns
- Applying statistical rules
- Counting word frequencies

They are fast and cheap but brittle — they miss context, sarcasm, and nuance.

This API uses a Large Language Model, which understands language the way a human does. It can infer that a customer saying *"I guess it's fine"* is not actually satisfied, or that a calm tone in a complaint about a two-week delay still represents high churn risk. That level of contextual reasoning is not possible with traditional NLP.

---

## Potential Extensions (If Asked in an Interview)

| Feature | How |
|---|---|
| Authentication | API key header middleware in FastAPI |
| Database storage | SQLAlchemy + PostgreSQL to log every analysis |
| Batch processing | Accept multiple transcripts in one request |
| Async processing | Background tasks for long transcripts |
| Deployment | Docker + Railway, Render, or AWS Lambda |
| Monitoring | Log token usage and response times per request |
| Caching | Cache repeated transcripts to reduce OpenAI cost |

---

## What I Learned

- How to design and build a REST API from scratch using FastAPI
- How to engineer prompts to produce reliable, structured LLM outputs
- How to use Pydantic for both input validation and output modeling
- How to securely manage API keys using environment variables
- How to version control a project with Git and publish it to GitHub
- The difference between traditional NLP and LLM-based language understanding
- How production-oriented thinking shapes small architectural decisions
