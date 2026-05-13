from pydantic import BaseModel, Field
from enum import Enum


class SentimentLevel(str, Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TranscriptRequest(BaseModel):
    transcript: str = Field(..., min_length=20, description="The full text of the support transcript")
    chunk_size_words: int = Field(
        default=500,
        ge=10,
        le=2000,
        description="Max words per chunk when splitting long transcripts",
    )


class TranscriptAnalysis(BaseModel):
    summary: str = Field(..., description="Brief summary of the conversation")
    sentiment: SentimentLevel = Field(..., description="Overall customer sentiment")
    risk_level: RiskLevel = Field(..., description="Risk level for churn or escalation")
    action_items: list[str] = Field(..., description="List of follow-up actions identified")
    was_chunked: bool = Field(default=False, description="Whether the transcript was split into chunks for processing")
    chunks_processed: int = Field(default=1, description="Number of chunks the transcript was split into")
