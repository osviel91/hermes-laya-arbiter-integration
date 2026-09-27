#!/usr/bin/env python3
"""Validate repository structure and reject obvious secret leakage."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = [
    ROOT / "README.md",
    ROOT / "docs/hermes-mcp-configuration.md",
    ROOT / "docs/laya-deployment.md",
    ROOT / "docs/laya-usage.md",
    ROOT / "docs/security-and-confidence.md",
    ROOT / "examples/hermes-mcp-server.yaml",
    ROOT / "experiments/results.json",
    ROOT / "linkedin/article.md",
    ROOT / "skills/bounded-decision-arbiter/SKILL.md",
]
SECRET_PATTERNS = [
    re.compile(r"(?i)authorization\s*:\s*bearer\s+[A-Za-z0-9._-]{20,}"),
    re.compile(r"(?i)(?:LAYA_API_KEY|ARBITER_API_KEY)\s*=\s*['\"]?(?!\$|REPLACE)[A-Za-z0-9._-]{20,}"),
]


def main() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED if not path.exists()]
    if missing:
        raise SystemExit("missing files: " + ", ".join(missing))

    json.loads((ROOT / "experiments/results.json").read_text(encoding="utf-8"))
    violations: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                violations.append(str(path.relative_to(ROOT)))
                break
    if violations:
        raise SystemExit("possible secret leakage in: " + ", ".join(violations))

    print(f"validated_files={len(REQUIRED)}")
    print("json_valid=experiments/results.json")
    print("secret_scan=passed")


if __name__ == "__main__":
    main()
