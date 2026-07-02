from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from .ingest import FILENAME_RE, ArtifactRecord

STORY_SECTIONS = (
    "🎯 O quê",
    "💡 Por quê",
    "📋 Comportamento esperado",
    "✅ Critérios de Aceite",
    "🔧 Notas Técnicas",
    "📊 Complexidade",
    "📄 Descrição Original",
)

COMPLEXITY_DRIVERS = ("Escopo", "Incerteza", "Integrações", "Dados", "QA", "Rollout")
MACHINE_PATH_RE = re.compile(r"(/home/|/Users/|C:\\|D:\\)")
META_PROSE_RE = re.compile(r"\b(TBD|to be defined|a definir)\b", re.I)


def _has_meta_prose_outside_todo(body: str) -> re.Match | None:
    for line in body.splitlines():
        if "@TODO" in line:
            continue
        match = META_PROSE_RE.search(line)
        if match:
            return match
    return None


@dataclass(frozen=True)
class CheckResult:
    name: str
    result: str
    detail: str = ""
    category: str = ""


def _section_present(body: str, label: str) -> bool:
    pattern = rf"(?im)^#{{1,3}}\s+{re.escape(label)}\s*$"
    return bool(re.search(pattern, body))


def _section_content(body: str, label: str) -> str:
    pattern = rf"(?im)^#{{1,3}}\s+{re.escape(label)}\s*$\n(.*?)(?=^#{1,3}\s|\Z)"
    match = re.search(pattern, body, re.DOTALL)
    return match.group(1).strip() if match else ""


def _word_count(text: str) -> int:
    return len([w for w in re.split(r"\s+", text.strip()) if w])


def validate_artifact(
    record: ArtifactRecord,
    *,
    hierarchy_parent_is_feature: bool | None = None,
) -> list[CheckResult]:
    """Rule-based validation mirroring validation-checks.md."""
    results: list[CheckResult] = []
    artifact_type = record.type

    if record.source == "vault":
        results.append(
            CheckResult(
                "frontmatter-type-present",
                "PASS" if record.frontmatter.get("type") else "FAIL",
                "" if record.frontmatter.get("type") else "`type:` key missing from frontmatter",
                "STRUCTURAL",
            )
        )
        results.append(
            CheckResult(
                "frontmatter-status-absent",
                "FAIL" if "status" in record.frontmatter else "PASS",
                "`status:` found in frontmatter" if "status" in record.frontmatter else "",
                "STRUCTURAL",
            )
        )
        if record.filename:
            ok = bool(FILENAME_RE.match(record.filename))
            results.append(
                CheckResult(
                    "filename-regex",
                    "PASS" if ok else "FAIL",
                    "" if ok else f"filename `{record.filename}` does not match required pattern",
                    "STRUCTURAL",
                )
            )
    else:
        for name in ("frontmatter-type-present", "frontmatter-status-absent", "filename-regex"):
            results.append(
                CheckResult(name, "SKIP", "source is Azure, not a vault draft", "STRUCTURAL")
            )

    if artifact_type == "User Story":
        missing_sections: list[str] = []
        for section in STORY_SECTIONS:
            if not _section_present(record.body, section):
                missing_sections.append(section)
                results.append(
                    CheckResult(
                        f"body-section-missing: {section}",
                        "FAIL",
                        f"section `{section}` absent",
                        "STRUCTURAL",
                    )
                )
        if not missing_sections:
            results.append(
                CheckResult(
                    "body-sections",
                    "PASS",
                    f"all {len(STORY_SECTIONS)} required sections present",
                    "STRUCTURAL",
                )
            )
    elif artifact_type in ("Feature", "Epic"):
        title_ok = bool(record.title.strip())
        desc_ok = bool(record.body.strip())
        results.append(
            CheckResult(
                "body-title-present",
                "PASS" if title_ok else "FAIL",
                "" if title_ok else "title is empty",
                "STRUCTURAL",
            )
        )
        results.append(
            CheckResult(
                "body-description-present",
                "PASS" if desc_ok else "FAIL",
                "" if desc_ok else "description is empty",
                "STRUCTURAL",
            )
        )

    if record.source == "vault" and record.azure_id is None:
        results.append(
            CheckResult(
                "hierarchy-skipped-no-azure-id",
                "WARN",
                "no azure_id in frontmatter, hierarchy checks skipped",
                "HIERARCHY",
            )
        )
        hierarchy_story_ok = None
    else:
        if artifact_type == "User Story":
            if hierarchy_parent_is_feature is True:
                results.append(
                    CheckResult(
                        "hierarchy-story-parent-is-feature",
                        "PASS",
                        "",
                        "HIERARCHY",
                    )
                )
                hierarchy_story_ok = True
            elif hierarchy_parent_is_feature is False:
                results.append(
                    CheckResult(
                        "hierarchy-story-parent-is-feature",
                        "FAIL",
                        "parent is not a Feature or is missing",
                        "HIERARCHY",
                    )
                )
                hierarchy_story_ok = False
            else:
                results.append(
                    CheckResult(
                        "hierarchy-story-parent-is-feature",
                        "SKIP",
                        "hierarchy not verified (no Azure MCP data)",
                        "HIERARCHY",
                    )
                )
                hierarchy_story_ok = None
        else:
            hierarchy_story_ok = None

    if artifact_type == "User Story":
        complexidade = _section_content(record.body, "📊 Complexidade")
        drivers_ok = complexidade and all(d in complexidade for d in COMPLEXITY_DRIVERS)
        results.append(
            CheckResult(
                "content-complexidade-breakdown",
                "PASS" if drivers_ok else "FAIL",
                "" if drivers_ok else "missing one or more driver keywords in Complexidade section",
                "CONTENT",
            )
        )
        sp = record.story_points
        sp_ok = sp is not None and sp > 0
        results.append(
            CheckResult(
                "content-story-points-set",
                "PASS" if sp_ok else "FAIL",
                f"{int(sp)} points" if sp_ok else "story_points not set or zero",
                "CONTENT",
            )
        )
        desc_orig = _section_content(record.body, "📄 Descrição Original")
        results.append(
            CheckResult(
                "content-descricao-original-present",
                "PASS" if desc_orig else "FAIL",
                "" if desc_orig else "Descrição Original section is empty",
                "CONTENT",
            )
        )

    path_match = MACHINE_PATH_RE.search(record.body)
    results.append(
        CheckResult(
            "content-no-machine-paths",
            "WARN" if path_match else "PASS",
            f"found: {path_match.group(0)}" if path_match else "",
            "CONTENT",
        )
    )
    meta_match = _has_meta_prose_outside_todo(record.body)
    results.append(
        CheckResult(
            "content-no-meta-prose",
            "WARN" if meta_match else "PASS",
            f"found: {meta_match.group(0)}" if meta_match else "",
            "CONTENT",
        )
    )

    title_words = _word_count(record.title)
    results.append(
        CheckResult(
            "dor-title-clear",
            "PASS" if title_words > 5 else "FAIL",
            f"{title_words} words" if title_words <= 5 else "",
            "DoR",
        )
    )
    results.append(
        CheckResult(
            "dor-description-present",
            "PASS" if record.body.strip() else "FAIL",
            "" if record.body.strip() else "body/description is empty",
            "DoR",
        )
    )
    if artifact_type == "User Story":
        sp = record.story_points
        sp_ok = sp is not None and sp > 0
        results.append(
            CheckResult(
                "dor-story-points-set",
                "PASS" if sp_ok else "FAIL",
                "" if sp_ok else "story points not set",
                "DoR",
            )
        )
        if hierarchy_story_ok is True:
            dor_link = "PASS"
            dor_detail = ""
        elif hierarchy_story_ok is False:
            dor_link = "FAIL"
            dor_detail = "hierarchy-story-parent-is-feature failed"
        else:
            dor_link = "SKIP"
            dor_detail = "hierarchy check skipped"
        results.append(
            CheckResult(
                "dor-linked-to-feature",
                dor_link,
                dor_detail,
                "DoR",
            )
        )

    return results


def critiques_from_results(results: Iterable[CheckResult]) -> list[str]:
    return [
        f"{r.name}: {r.detail}".rstrip(": ")
        for r in results
        if r.result in ("FAIL", "WARN") and (r.detail or r.name)
    ]


def outcome_from_results(results: Iterable[CheckResult]) -> str:
    return "FAIL" if any(r.result == "FAIL" for r in results) else "PASS"
