"""Compare two fingerprints produced by ``generate_fingerprint.py`` and report spec-relevant drift.

Usage::

    python conformance/compare_fingerprints.py fingerprints/baseline.json new.json [--markdown report.md]

Exit code 0: no drift. 1: drift found (the report lists every changed path). 2: usage error.
The ``environment`` section is reported but never counts as drift.

Licensed under BSD-3-Clause like the rest of the repository tooling.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SECTION_TITLES = {
    "format_module": "spatialdata._io.format (versions, compatibility, defaults)",
    "on_disk": "On-disk metadata (Zarr attributes, array shapes/dtypes, Parquet schemas)",
    "python_api": "Python in-memory model (exports, models, element layout)",
    "python_api_after_read": "Python in-memory model after reading back from disk",
}

SPEC_PAGES = {
    "format_module": ["spec/on-disk/versions.md", "spec/on-disk/images.md"],
    "on_disk.container_current": ["spec/on-disk/*.md (current-version tabs)"],
    "on_disk.container_0.1": ["spec/on-disk/*.md (Zarr v2 tabs)", "spec/on-disk/versions.md"],
    "python_api": ["spec/in-memory/python/*.md"],
    "python_api_after_read": ["spec/in-memory/python/elements.md"],
}


def diff(a: Any, b: Any, path: str, out: list[tuple[str, str, Any, Any]]) -> None:
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(set(a) | set(b)):
            sub = f"{path}.{key}" if path else str(key)
            if key not in a:
                out.append(("added", sub, None, b[key]))
            elif key not in b:
                out.append(("removed", sub, a[key], None))
            else:
                diff(a[key], b[key], sub, out)
    elif isinstance(a, list) and isinstance(b, list):
        if a != b:
            if all(not isinstance(x, dict | list) for x in a + b):
                out.append(("changed", path, a, b))
            else:
                for i in range(max(len(a), len(b))):
                    sub = f"{path}[{i}]"
                    if i >= len(a):
                        out.append(("added", sub, None, b[i]))
                    elif i >= len(b):
                        out.append(("removed", sub, a[i], None))
                    else:
                        diff(a[i], b[i], sub, out)
    elif a != b:
        out.append(("changed", path, a, b))


def _fmt(value: Any) -> str:
    text = json.dumps(value, sort_keys=True)
    return text if len(text) <= 160 else text[:157] + "..."


def pages_for(path: str) -> list[str]:
    best = ""
    for prefix in SPEC_PAGES:
        if path.startswith(prefix) and len(prefix) > len(best):
            best = prefix
    return SPEC_PAGES.get(best, [])


def build_report(baseline: dict[str, Any], new: dict[str, Any]) -> tuple[str, bool]:
    lines: list[str] = []
    env_a, env_b = baseline.get("environment", {}), new.get("environment", {})
    lines.append("# Spec drift report")
    lines.append("")
    lines.append(f"Baseline: spatialdata {env_a.get('spatialdata')} · New: spatialdata {env_b.get('spatialdata')}")
    dep_changes = [
        f"{k} {env_a.get('dependencies', {}).get(k)} → {v}"
        for k, v in env_b.get("dependencies", {}).items()
        if env_a.get("dependencies", {}).get(k) != v
    ]
    if dep_changes:
        lines.append("Dependency versions differ (informational): " + ", ".join(dep_changes))
    lines.append("")

    drift = False
    for section, title in SECTION_TITLES.items():
        changes: list[tuple[str, str, Any, Any]] = []
        diff(baseline.get(section, {}), new.get(section, {}), section, changes)
        lines.append(f"## {title}")
        lines.append("")
        if not changes:
            lines.append("No differences.")
            lines.append("")
            continue
        drift = True
        touched_pages = sorted({p for c in changes for p in pages_for(c[1])})
        if touched_pages:
            lines.append("Spec pages to check: " + ", ".join(f"`{p}`" for p in touched_pages))
            lines.append("")
        lines.append("| Change | Path | Baseline | New |")
        lines.append("|--------|------|----------|-----|")
        for kind, path, old, newv in changes[:200]:
            lines.append(f"| {kind} | `{path}` | `{_fmt(old)}` | `{_fmt(newv)}` |")
        if len(changes) > 200:
            lines.append(f"| … | {len(changes) - 200} more | | |")
        lines.append("")

    lines.append("## Verdict")
    lines.append("")
    lines.append(
        "DRIFT: the specification may need an update; review the pages listed above."
        if drift
        else "No spec-relevant drift detected."
    )
    return "\n".join(lines) + "\n", drift


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("new", type=Path)
    parser.add_argument("--markdown", type=Path, help="also write the report to this file")
    args = parser.parse_args()
    try:
        baseline = json.loads(args.baseline.read_text())
        new = json.loads(args.new.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read fingerprints: {exc}", file=sys.stderr)
        sys.exit(2)
    report, drift = build_report(baseline, new)
    print(report)
    if args.markdown:
        args.markdown.write_text(report)
    sys.exit(1 if drift else 0)


if __name__ == "__main__":
    main()
