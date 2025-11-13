"""Discovery engine orchestrating plugin phases and normalization."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

from ..models import RawArtifact, CommandDefinition
from .base import DiscoveryPlugin
from .confidence import filter_by_confidence
from .normalization import normalize_artifacts


@dataclass
class DiscoveryResult:
    raw_artifacts: List[RawArtifact]
    commands: List[CommandDefinition]


class DiscoveryEngine:
    """Run multiple plugins through the discovery pipeline."""

    def __init__(self, plugins: Sequence[DiscoveryPlugin]):
        self._plugins = list(plugins)

    def run(self, project_root: Path) -> DiscoveryResult:
        collected: List[RawArtifact] = []
        # Scan phase
        for p in self._plugins:
            for artifact in p.scan(project_root):
                collected.append(artifact)
        # Classify / Extract phases
        enriched: List[RawArtifact] = []
        for p in self._plugins:
            interim: List[RawArtifact] = []
            for a in collected:
                b = p.classify(a)
                if b is None:
                    continue
                c = p.extract(b)
                if c is None:
                    continue
                interim.append(c)
            # Plugin-level normalization override (rare) before global
            interim = p.normalize(interim)
            enriched.extend(interim)
        # Confidence filtering
        filtered = list(filter_by_confidence(enriched))
        # Global normalization to CommandDefinition
        commands = normalize_artifacts(filtered)
        return DiscoveryResult(raw_artifacts=filtered, commands=commands)
