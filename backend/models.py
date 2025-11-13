"""Core Pydantic models for mycli artifact & configuration layer.

This file originally only contained cloud integration config models. It now
adds foundational data structures specified in the v2 PRD: ParameterDefinition,
CommandDefinition, RepoStats, RawArtifact, Origin enum, plus a stable hashing
utility. These models intentionally avoid business logic beyond light
validation so they remain portable for future LLM enrichment and persistence.
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any, Literal, Sequence
from enum import Enum
import hashlib
import re

from pydantic import BaseModel, Field, model_validator

# ---------------------------------------------------------------------------
# Cloud provider configuration (legacy / still supported)
# ---------------------------------------------------------------------------


class VercelConfig(BaseModel):
    """Vercel cloud configuration."""
    project_slug: str
    team_id: Optional[str] = None
    token: Optional[str] = None


class SupabaseConfig(BaseModel):
    """Supabase cloud configuration."""
    api_url: str
    api_health_check: str


class RailwayConfig(BaseModel):
    """Railway cloud configuration."""
    project_id: str
    environment_id: str
    token: Optional[str] = None


class ProjectConfig(BaseModel):
    """Project configuration model."""
    name: str
    workspace: str
    dev_dir: str
    task_start: str
    apps: List[str]
    urls: List[str]
    vercel: Optional[VercelConfig] = None
    supabase: Optional[SupabaseConfig] = None
    railway: Optional[RailwayConfig] = None


# ---------------------------------------------------------------------------
# Core artifact & discovery models
# ---------------------------------------------------------------------------

class Origin(str, Enum):
    """Enumerated origin of discovered commands.

    Centralizing origin strings prevents drift across parsers and ensures
    consistent filtering / tagging in registries and UI layers.
    """

    TASKFILE = "taskfile"
    PACKAGE_SCRIPT = "package_script"
    PYTHON = "python"
    POWERSHELL = "powershell"
    SHELL = "shell"
    DOCKER = "docker"
    LANGGRAPH = "langgraph"
    TEMPLATE = "template"
    OTHER = "other"


ParameterType = Literal[
    "string",
    "integer",
    "float",
    "boolean",
    "enum",
    "path",
]


class ParameterDefinition(BaseModel):
    """Definition of a single command parameter.

    Fields chosen for future extensibility; `meta` allows plugins / future
    enrichment layers to attach arbitrary structured data without schema
    changes.
    """

    name: str = Field(
        ..., min_length=1, description="Parameter name (identifier)"
    )
    type: ParameterType = Field(
        ..., description="Normalized type classification for dialog rendering"
    )
    description: Optional[str] = Field(
        None, description="Human friendly description or help text"
    )
    required: bool = Field(
        False, description="If True must be provided by user before execution"
    )
    default: Optional[Any] = Field(
        None, description="Optional default value if not supplied"
    )
    enum: Optional[List[str]] = Field(
        None,
        description="Allowed values (only if type == 'enum')",
    )
    min: Optional[float] = Field(
        None, description="Minimum numeric value (int/float types only)"
    )
    max: Optional[float] = Field(
        None, description="Maximum numeric value (int/float types only)"
    )
    regex: Optional[str] = Field(
        None, description="Regex pattern string for validation (string type)"
    )
    examples: Optional[List[str]] = Field(
        None, description="Example values for UX hints"
    )
    meta: Dict[str, Any] = Field(
        default_factory=dict, description="Extensible plugin-specific metadata"
    )

    @model_validator(mode="after")
    def _validate_constraints(self) -> "ParameterDefinition":
        # enum only valid with type=='enum' and must be non-empty
        if self.enum is not None:
            if self.type != "enum":
                raise ValueError("'enum' provided but type is not 'enum'")
            if len(self.enum) == 0:
                raise ValueError("'enum' list cannot be empty")

        # numeric bounds only valid for integer/float types
        if (
            self.min is not None or self.max is not None
        ) and self.type not in {"integer", "float"}:
            raise ValueError("'min'/'max' only valid for numeric types")

        # regex only for strings; also validate the pattern compiles
        if self.regex is not None:
            if self.type != "string":
                raise ValueError("'regex' only valid when type == 'string'")
            try:
                re.compile(self.regex)
            except re.error as e:  # pragma: no cover - pydantic surfaces error
                raise ValueError(f"Invalid regex pattern: {e}") from e

        # required must not define a default value
        if self.required and self.default is not None:
            raise ValueError(
                "Required parameters must not define a default value"
            )

        return self


def stable_command_id(parts: Sequence[str]) -> str:
    """Return truncated stable SHA256 hex for the given identifying parts.

    Parts are joined with '\x1f' (unit separator) to reduce accidental
    vs simple concatenation when names contain path fragments.
    """

    h = hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()
    return h[:16]  # 16 hex (~64 bits) sufficient for local uniqueness


class CommandDefinition(BaseModel):
    """Normalized command definition produced by discovery pipeline."""

    id: str = Field(..., description="Stable truncated hash for identity")
    name: str = Field(
        ..., min_length=1, description="Display / invocation name"
    )
    source_path: str = Field(..., description="File path or entry reference")
    origin: Origin = Field(..., description="Parser origin classification")
    description: Optional[str] = Field(None, description="Human readable help")
    parameters: List[ParameterDefinition] = Field(
        default_factory=list, description="Ordered parameter definitions"
    )
    tags: List[str] = Field(
        default_factory=list, description="Arbitrary tagging"
    )
    estimated_runtime_seconds: Optional[float] = Field(
        None, description="Heuristic or historical runtime estimate"
    )
    invocation: Dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Strategy data (adapter selection, args template, env overrides)"
        ),
    )
    meta: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extensible plugin/LLM enrichment data",
    )

    @classmethod
    def create(
        cls,
        name: str,
        source_path: str,
        origin: Origin,
        **kwargs: Any,
    ) -> "CommandDefinition":
        """Factory computing stable id from name + source path + origin."""
        cmd_id = stable_command_id([origin.value, source_path, name])
        return cls(
            id=cmd_id,
            name=name,
            source_path=source_path,
            origin=origin,
            **kwargs,
        )


class RepoStats(BaseModel):
    """Repository structural & health metrics collected by X-ray scanner."""

    total_files: int
    total_lines: int
    total_size_bytes: int
    language_breakdown: Dict[str, int] = Field(
        default_factory=dict, description="Mapping language -> line count"
    )
    largest_files: List[Dict[str, Any]] = Field(
        default_factory=list, description="Top-N largest files metadata"
    )
    comment_density_pct: Optional[float] = Field(
        None, description="Percentage of comment lines vs total lines"
    )
    directory_tree: Dict[str, Any] = Field(
        default_factory=dict, description="Truncated depth directory structure"
    )
    file_length_histogram: Dict[str, int] = Field(
        default_factory=dict, description="Bucket label -> file count"
    )
    health_index: Optional[float] = Field(
        None, description="Composite quality metric (0..100)"
    )

    @staticmethod
    def compute_health_index(
        total_files: int,
        comment_density_pct: Optional[float],
        largest_file_bytes: Optional[int],
    ) -> float:
        """Simple heuristic health index.

        Weight factors (subject to tuning): comment density (up to +40), file
        size penalty (up to -30), file count scaling (up to -30). Normalized to
        0..100 then clamped.
        """
        score = 100.0
        if comment_density_pct is not None:
            # Assume ideal ~25-30%; heavy penalty if <5%
            if comment_density_pct < 5:
                score -= 25
            elif comment_density_pct < 15:
                score -= 10
            else:
                score += 5  # modest reward for decent documentation
        if largest_file_bytes is not None:
            if largest_file_bytes > 200_000:  # >200 KB large
                score -= 30
            elif largest_file_bytes > 100_000:
                score -= 15
        if total_files > 1500:
            score -= 30
        elif total_files > 800:
            score -= 15
        return max(0.0, min(100.0, score))


class RawArtifact(BaseModel):
    """Intermediate discovery output before normalization.

    The discovery engine converts this into a CommandDefinition via
    normalization plugins.
    """

    type: str
    path: str
    content_snippet: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)
    confidence: Optional[float] = Field(
        None, description="Parser confidence score (0..1)"
    )

