"""Signal engine for generating coach signals from transcripts."""

from collections import deque
from threading import Lock
from typing import Dict, List, Optional
import time
import uuid

from backend.models import CoachSignal, TranscriptEvent


class SignalEngine:
    """Maintain signals and generate new ones from transcript events."""

    def __init__(
        self,
        coach,
        buffer_size: int = 40,
        dedupe_window_seconds: float = 60.0,
        global_cooldown_seconds: float = 2.5,
        kind_cooldown_seconds: float = 10.0,
    ):
        self.coach = coach
        self.buffer = deque(maxlen=buffer_size)
        self.dedupe_window_seconds = dedupe_window_seconds
        self.global_cooldown_seconds = global_cooldown_seconds
        self.kind_cooldown_seconds = kind_cooldown_seconds
        self.signals: List[CoachSignal] = []
        self.last_global_ts = 0.0
        self.last_kind_ts: Dict[str, float] = {}
        self.last_refresh_ts = 0.0
        self.lock = Lock()

    def add_event(self, event: TranscriptEvent) -> None:
        """Add a transcript event and potentially generate signals."""
        if not event.is_final:
            return

        with self.lock:
            self.buffer.append(event)

        self._maybe_generate(force=False)

    def refresh(self) -> List[CoachSignal]:
        """Force a refresh (light throttle still applies)."""
        now = time.time()
        if now - self.last_refresh_ts < 1.5:
            return self.get_signals()

        self.last_refresh_ts = now
        self._maybe_generate(force=True, light=True)
        return self.get_signals()

    def get_signals(self) -> List[CoachSignal]:
        """Return current signals sorted by status and confidence."""
        with self.lock:
            signals = list(self.signals)

        def sort_key(signal: CoachSignal):
            status_rank = 0 if signal.status == "active" else 1
            return (status_rank, -signal.confidence, -signal.ts)

        return sorted(signals, key=sort_key)

    def park_signal(self, signal_id: str) -> bool:
        return self._update_status(signal_id, "parked")

    def resolve_signal(self, signal_id: str) -> bool:
        return self._update_status(signal_id, "resolved")

    def _update_status(self, signal_id: str, status: str) -> bool:
        with self.lock:
            for signal in self.signals:
                if signal.id == signal_id:
                    signal.status = status
                    return True
        return False

    def _maybe_generate(self, force: bool = False, light: bool = False) -> None:
        now = time.time()
        if not force:
            if now - self.last_global_ts < self.global_cooldown_seconds:
                return
        elif light:
            if now - self.last_global_ts < 1.0:
                return

        with self.lock:
            if not self.buffer:
                return
            transcript_events = list(self.buffer)
            prior_signals = [signal.to_dict() for signal in self.signals][-10:]

        try:
            raw_signals = self.coach.generate_signals(transcript_events, prior_signals)
        except Exception as exc:
            print(f"Signal generation failed: {exc}")
            return

        self.last_global_ts = now
        self._ingest_signals(raw_signals, now)

    def _ingest_signals(self, raw_signals: List[Dict], now: float) -> None:
        if not raw_signals:
            return

        for raw_signal in raw_signals:
            normalized = self._normalize_signal(raw_signal, now)
            if not normalized:
                continue
            if self._is_deduped(normalized, now):
                continue
            last_kind_ts = self.last_kind_ts.get(normalized.kind, 0.0)
            if now - last_kind_ts < self.kind_cooldown_seconds:
                continue
            self.last_kind_ts[normalized.kind] = now

            with self.lock:
                self.signals.append(normalized)
                if len(self.signals) > 200:
                    self.signals = self.signals[-200:]

    def _normalize_signal(self, raw_signal: Dict, now: float) -> Optional[CoachSignal]:
        if not isinstance(raw_signal, dict):
            return None

        kind = raw_signal.get("kind")
        if kind not in {"reasoning", "accountability", "language", "drift"}:
            return None

        confidence = raw_signal.get("confidence", 0.0)
        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = 0.0
        confidence = max(0.0, min(1.0, confidence))

        title = str(raw_signal.get("title", "")).strip()
        detail = str(raw_signal.get("detail", "")).strip()

        evidence = raw_signal.get("evidence")
        if not isinstance(evidence, list):
            evidence = []
        cleaned_evidence = []
        for item in evidence:
            if not isinstance(item, dict):
                continue
            stream = item.get("stream") if item.get("stream") in {"A", "B"} else None
            quote = str(item.get("quote", "")).strip()
            ts = item.get("ts")
            try:
                ts = float(ts) if ts is not None else None
            except (TypeError, ValueError):
                ts = None
            if quote:
                cleaned_evidence.append({"stream": stream, "quote": quote, "ts": ts})

        suggested = raw_signal.get("suggested")
        if not isinstance(suggested, dict):
            suggested = {}

        status = raw_signal.get("status", "active")
        if status not in {"active", "parked", "resolved"}:
            status = "active"

        return CoachSignal(
            id=str(raw_signal.get("id") or uuid.uuid4()),
            kind=kind,
            confidence=confidence,
            title=title or "Signal",
            detail=detail or "",
            evidence=cleaned_evidence,
            suggested=suggested,
            status=status,
            ts=float(raw_signal.get("ts", now)),
        )

    def _is_deduped(self, signal: CoachSignal, now: float) -> bool:
        primary_quote = None
        if signal.evidence:
            primary_quote = signal.evidence[0].get("quote")

        if not primary_quote:
            return False

        with self.lock:
            for existing in self.signals:
                if existing.kind != signal.kind:
                    continue
                if now - existing.ts > self.dedupe_window_seconds:
                    continue
                if not existing.evidence:
                    continue
                if existing.evidence[0].get("quote") == primary_quote:
                    return True

        return False
