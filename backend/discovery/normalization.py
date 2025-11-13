"""Normalization helpers converting RawArtifact objects to
CommandDefinition.
"""
from __future__ import annotations

from typing import List

from ..models import (
    RawArtifact,
    CommandDefinition,
    Origin,
    ParameterDefinition,
)


def _extract_parameters(raw_cmd: str | None) -> list[ParameterDefinition]:
    """Heuristic parameter extraction from a raw command string.

    - --flag => boolean parameter (default False)
    - --key=value => string parameter with default
    - <name> => required string positional
    """
    if not raw_cmd or not isinstance(raw_cmd, str):
        return []
    params: list[ParameterDefinition] = []
    seen: set[str] = set()
    tokens = raw_cmd.strip().split()
    for tok in tokens:
        if tok.startswith("--"):
            body = tok[2:]
            if not body:
                continue
            if "=" in body:
                key, val = body.split("=", 1)
                key = key.strip().replace("-", "_")
                if key and key not in seen:
                    params.append(
                        ParameterDefinition(
                            name=key,
                            type="string",
                            required=False,
                            default=val,
                            description=(
                                f"Flag --{key.replace('_', '-')} value"
                            ),
                        )
                    )
                    seen.add(key)
            else:
                key = body.strip().replace("-", "_")
                if key and key not in seen:
                    params.append(
                        ParameterDefinition(
                            name=key,
                            type="boolean",
                            required=False,
                            default=False,
                            description=(
                                f"Toggle --{key.replace('_', '-')}"
                            ),
                        )
                    )
                    seen.add(key)
        elif tok.startswith("<") and tok.endswith(">") and len(tok) > 2:
            key = tok[1:-1].strip().replace("-", "_")
            if key and key not in seen:
                params.append(
                    ParameterDefinition(
                        name=key,
                        type="string",
                        required=True,
                        description=f"Positional parameter {tok}",
                        meta={"positional": True},
                    )
                )
                seen.add(key)
    return params


def normalize_artifacts(
    artifacts: List[RawArtifact],
) -> List[CommandDefinition]:
    """Very early placeholder normalization.

    For scaffolding we map artifact path + last path segment to a command name.
    Real implementation will parse content snippets & metadata for parameters.
    """
    cmds: list[CommandDefinition] = []
    for a in artifacts:
        name = a.meta.get("task_name") or a.path.split("/")[-1]
        origin_value = a.meta.get("origin") or "other"
        try:
            origin = Origin(origin_value)
        except ValueError:  # fallback if unknown
            origin = Origin.OTHER
        invocation = {}
        if origin == Origin.TASKFILE:
            # Provide a simple adapter hint to enable execution helpers
            invocation = {"adapter": "taskfile", "task_name": name}
        elif origin == Origin.PACKAGE_SCRIPT:
            pm = a.meta.get("package_manager") or "npm"
            script_name = a.meta.get("script_name") or name
            invocation = {
                "adapter": "npm",
                "package_manager": pm,
                "script_name": script_name,
            }
        # Attach cwd if provided (for monorepo subprojects)
        cwd = a.meta.get("cwd")
        if cwd:
            invocation["cwd"] = cwd

        # Basic parameter inference from raw command where available
        params = _extract_parameters(a.meta.get("raw_cmd"))

        cmd = CommandDefinition.create(
            name=name,
            source_path=a.path,
            origin=origin,
            description=a.meta.get("description"),
            parameters=params,
            tags=a.meta.get("tags", []),
            invocation=invocation,
            meta={"raw_meta": a.meta},
        )
        cmds.append(cmd)
    return cmds
