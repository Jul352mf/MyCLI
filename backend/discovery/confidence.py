"""Confidence filtering utilities for RawArtifacts."""
from __future__ import annotations

from typing import Iterable

from ..models import RawArtifact

DEFAULT_CONFIDENCE_THRESHOLD = 0.35  # initial heuristic


def filter_by_confidence(
    artifacts: Iterable[RawArtifact], threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
):
    """Yield artifacts whose confidence is >= threshold or confidence unknown.

    Missing confidence is treated as pass-through to avoid early loss; later stages
    can down-rank or discard.
    """
    for a in artifacts:
        if a.confidence is None or a.confidence >= threshold:
            yield a
