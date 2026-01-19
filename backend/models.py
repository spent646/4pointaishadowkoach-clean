"""Data models for AI Shadow Coach v1."""

from dataclasses import dataclass
from typing import List, Literal, Optional
from datetime import datetime


@dataclass
class TranscriptEvent:
    """A single transcript event from stream A (mic) or B (loopback)."""
    ts: float  # Unix timestamp
    stream: Literal["A", "B"]  # "A" = microphone, "B" = loopback
    text: str
    is_final: bool  # True for final transcript, False for interim

    def to_dict(self):
        return {
            "ts": self.ts,
            "stream": self.stream,
            "text": self.text,
            "is_final": self.is_final
        }


@dataclass
class CoachMessage:
    """A message in the coach chat."""
    role: Literal["user", "assistant"]
    text: str
    ts: float  # Unix timestamp

    def to_dict(self):
        return {
            "role": self.role,
            "text": self.text,
            "ts": self.ts
        }


@dataclass
class CoachSignal:
    """A Socratic coaching signal."""
    id: str
    kind: Literal["reasoning", "accountability", "language", "drift"]
    confidence: float
    title: str
    detail: str
    evidence: List[dict]
    suggested: dict
    status: Literal["active", "parked", "resolved"]
    ts: float

    def to_dict(self):
        return {
            "id": self.id,
            "kind": self.kind,
            "confidence": self.confidence,
            "title": self.title,
            "detail": self.detail,
            "evidence": self.evidence,
            "suggested": self.suggested,
            "status": self.status,
            "ts": self.ts,
        }
