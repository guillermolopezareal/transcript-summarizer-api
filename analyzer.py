import json
from openai import OpenAI
from dotenv import load_dotenv
from models import TranscriptAnalysis, SentimentLevel, RiskLevel
from chunker import chunk_transcript

load_dotenv()
client = OpenAI()

SYSTEM_PROMPT = """You are an AI analyst specialized in customer support quality assurance.

Given a customer support transcript, you must respond with a JSON object containing exactly these fields:

- summary: A 1-3 sentence summary of what the conversation was about and how it was resolved.
- sentiment: The overall customer sentiment. Must be one of: "positive", "neutral", "negative".
- risk_level: The risk of churn or escalation based on tone and outcome. Must be one of: "low", "medium", "high".
- action_items: A JSON array of strings. Each string is a specific follow-up action the support team should take. If none, return an empty array.

Respond ONLY with valid JSON. No explanation, no markdown, no code blocks."""

MERGE_SUMMARY_PROMPT = """You are an AI analyst. You are given partial summaries of consecutive sections of a single customer support transcript.
Combine them into one coherent 1-3 sentence summary of the full conversation and its resolution.
Respond with ONLY the summary text. No JSON, no markdown, no code blocks."""

# Lower index = higher priority (worse outcome wins)
_SENTIMENT_RANK = {SentimentLevel.negative: 0, SentimentLevel.neutral: 1, SentimentLevel.positive: 2}
_RISK_RANK = {RiskLevel.high: 0, RiskLevel.medium: 1, RiskLevel.low: 2}


def _analyze_single(text: str) -> TranscriptAnalysis:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Transcript:\n\n{text}"},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    data = json.loads(response.choices[0].message.content)
    return TranscriptAnalysis(**data)


def _merge_analyses(analyses: list[TranscriptAnalysis]) -> TranscriptAnalysis:
    # Worst-case sentiment and risk across all chunks
    sentiment = min(analyses, key=lambda a: _SENTIMENT_RANK[a.sentiment]).sentiment
    risk_level = min(analyses, key=lambda a: _RISK_RANK[a.risk_level]).risk_level

    # Deduplicated union of action items preserving order
    seen: set[str] = set()
    action_items: list[str] = []
    for analysis in analyses:
        for item in analysis.action_items:
            if item not in seen:
                seen.add(item)
                action_items.append(item)

    # LLM call to produce a single coherent summary from chunk summaries
    partial_summaries = "\n\n".join(
        f"Part {i + 1}: {a.summary}" for i, a in enumerate(analyses)
    )
    merge_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": MERGE_SUMMARY_PROMPT},
            {"role": "user", "content": partial_summaries},
        ],
        temperature=0.2,
    )
    summary = merge_response.choices[0].message.content.strip()

    return TranscriptAnalysis(
        summary=summary,
        sentiment=sentiment,
        risk_level=risk_level,
        action_items=action_items,
    )


def analyze_transcript(transcript: str, chunk_size_words: int = 500) -> TranscriptAnalysis:
    chunks = chunk_transcript(transcript, chunk_size=chunk_size_words)

    if len(chunks) == 1:
        result = _analyze_single(transcript)
        result.was_chunked = False
        result.chunks_processed = 1
        return result

    analyses = [_analyze_single(chunk) for chunk in chunks]
    result = _merge_analyses(analyses)
    result.was_chunked = True
    result.chunks_processed = len(chunks)
    return result
