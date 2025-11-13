"""Base interfaces for discovery plugins.

Plugins participate in a four-phase pipeline:
1. scan(project_root) -> Iterable[RawArtifact]
2. classify(artifact) -> RawArtifact (optional enrichment / discard)
3. extract(artifact) -> RawArtifact (structured metadata extraction)
4. normalize(artifacts) handled centrally converting to CommandDefinition

Each plugin may implement only relevant phases; missing methods are skipped.
"""
from __future__ import annotations

from typing import Iterable, Protocol
from pathlib import Path

from ..models import RawArtifact

class DiscoveryPlugin(Protocol):
    """Protocol all discovery plugins must follow."""

    name: str  # human readable name
    origins: list[str]  # origin enum string values produced

    def scan(
        self, project_root: Path
    ) -> Iterable[RawArtifact]:  # pragma: no cover
        """Produce initial RawArtifacts.

        Lightweight pass; avoid heavy IO.
        """
        raise NotImplementedError

    def classify(
        self, artifact: RawArtifact
    ) -> RawArtifact | None:  # pragma: no cover
        """Optional filtering / enrichment. Return None to discard."""
        return artifact

    def extract(
        self, artifact: RawArtifact
    ) -> RawArtifact | None:  # pragma: no cover
        """Optional structured metadata extraction. Return None to discard."""
        return artifact

    def normalize(
        self, artifacts: list[RawArtifact]
    ) -> list[RawArtifact]:  # pragma: no cover
        """Optional plugin-level normalization before global step."""
        return artifacts
