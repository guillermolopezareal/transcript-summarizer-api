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


class TranscriptAnalysis(BaseModel):
    summary: str = Field(..., description="Brief summary of the conversation")
    sentiment: SentimentLevel = Field(..., description="Overall customer sentiment")
    risk_level: RiskLevel = Field(..., description="Risk level for churn or escalation")
    action_items: list[str] = Field(..., description="List of follow-up actions identified")
