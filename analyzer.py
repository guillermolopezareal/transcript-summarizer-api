import json
from openai import OpenAI
from dotenv import load_dotenv
from models import TranscriptAnalysis

load_dotenv()
client = OpenAI()

SYSTEM_PROMPT = """You are an AI analyst specialized in customer support quality assurance.

Given a customer support transcript, you must respond with a JSON object containing exactly these fields:

- summary: A 1-3 sentence summary of what the conversation was about and how it was resolved.
- sentiment: The overall customer sentiment. Must be one of: "positive", "neutral", "negative".
- risk_level: The risk of churn or escalation based on tone and outcome. Must be one of: "low", "medium", "high".
- action_items: A JSON array of strings. Each string is a specific follow-up action the support team should take. If none, return an empty array.

Respond ONLY with valid JSON. No explanation, no markdown, no code blocks."""


def analyze_transcript(transcript: str) -> TranscriptAnalysis:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Transcript:\n\n{transcript}"},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )

    raw = response.choices[0].message.content
    data = json.loads(raw)
    return TranscriptAnalysis(**data)
