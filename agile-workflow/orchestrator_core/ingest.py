from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
FILENAME_RE = re.compile(r"^(\d+|tech-debt|bug|task|spike)-[a-z0-9-]+$")


@dataclass(frozen=True)
class ArtifactRecord:
    type: str
    title: str
    body: str
    story_points: float | None
    parent_id: int | None
    source: str
    filename: str | None
    azure_id: int | None
    frontmatter: dict[str, Any] = field(default_factory=dict)
    raw: str = ""


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    fm_block = match.group(1)
    body = text[match.end() :]
    frontmatter: dict[str, Any] = {}
    for line in fm_block.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            frontmatter[key] = [v.strip() for v in inner.split(",") if v.strip()] if inner else []
        elif value.isdigit():
            frontmatter[key] = int(value)
        else:
            try:
                frontmatter[key] = float(value)
            except ValueError:
                frontmatter[key] = value.strip("\"'")
    return frontmatter, body


def extract_title(body: str, frontmatter: dict[str, Any]) -> str:
    match = TITLE_RE.search(body)
    if match:
        return match.group(1).strip()
    for key in ("title", "System.Title"):
        if key in frontmatter:
            return str(frontmatter[key])
    return ""


def normalize_work_item_type(value: str | None) -> str | None:
    if not value:
        return None
    normalized = value.strip().lower()
    mapping = {
        "user story": "User Story",
        "story": "User Story",
        "feature": "Feature",
        "epic": "Epic",
        "bug": "User Story",
        "tech debt": "User Story",
        "spike": "User Story",
    }
    return mapping.get(normalized, value.strip())


def ingest_from_text(text: str, *, filename: str | None = None) -> ArtifactRecord:
    frontmatter, body = parse_frontmatter(text)
    artifact_type = normalize_work_item_type(
        str(frontmatter.get("work_item_type") or frontmatter.get("type") or "User Story")
    )
    if artifact_type == "ticket":
        artifact_type = normalize_work_item_type(str(frontmatter.get("work_item_type", "User Story")))
    title = extract_title(body, frontmatter)
    story_points = frontmatter.get("story_points")
    if isinstance(story_points, str) and story_points.replace(".", "", 1).isdigit():
        story_points = float(story_points)
    return ArtifactRecord(
        type=artifact_type or "User Story",
        title=title,
        body=body,
        story_points=float(story_points) if isinstance(story_points, (int, float)) else None,
        parent_id=None,
        source="vault",
        filename=filename,
        azure_id=None,
        frontmatter=frontmatter,
        raw=text,
    )


def ingest_vault_file(path: Path) -> ArtifactRecord:
    raw = path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(raw)
    artifact_type = normalize_work_item_type(
        str(frontmatter.get("work_item_type") or frontmatter.get("type") or "")
    )
    if artifact_type == "ticket":
        artifact_type = normalize_work_item_type(str(frontmatter.get("work_item_type", "User Story")))
    title = extract_title(body, frontmatter)
    story_points = frontmatter.get("story_points")
    if isinstance(story_points, str) and story_points.replace(".", "", 1).isdigit():
        story_points = float(story_points)
    azure_id = frontmatter.get("azure_id")
    if isinstance(azure_id, str) and azure_id.isdigit():
        azure_id = int(azure_id)
    parent = frontmatter.get("parent_feature") or frontmatter.get("parent_epic")
    parent_id = int(parent) if isinstance(parent, (int, str)) and str(parent).isdigit() else None
    return ArtifactRecord(
        type=artifact_type or "User Story",
        title=title,
        body=body,
        story_points=float(story_points) if isinstance(story_points, (int, float)) else None,
        parent_id=parent_id,
        source="vault",
        filename=path.stem,
        azure_id=int(azure_id) if isinstance(azure_id, int) else None,
        frontmatter=frontmatter,
        raw=raw,
    )


def ingest_azure_record(
    *,
    work_item_type: str,
    title: str,
    description: str,
    story_points: float | None,
    parent_id: int | None,
    azure_id: int,
) -> ArtifactRecord:
    return ArtifactRecord(
        type=normalize_work_item_type(work_item_type) or work_item_type,
        title=title,
        body=description or "",
        story_points=story_points,
        parent_id=parent_id,
        source="azure",
        filename=None,
        azure_id=azure_id,
        frontmatter={},
        raw=description or "",
    )
