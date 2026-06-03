#!/usr/bin/env python3
"""
memory_auditor.py — Audit Claude Code memory directories for staleness,
orphaned files, broken MEMORY.md links, and oversized indexes.

Usage:
    python3 memory_auditor.py [memory_dir]

If no directory is given, scans all known project memory directories.
"""

import os
import re
import sys
from datetime import datetime, date
from pathlib import Path

KNOWN_DIRS = [
    Path.home() / ".claude" / "projects" / "C--Users-Stant" / "memory",
    Path.home() / ".claude" / "projects" / "C--Windows-system32" / "memory",
]

STALENESS_DAYS = {
    "project": 14,
    "feedback": 9999,
    "user": 90,
    "reference": 30,
}


def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm_text = text[4:end]
    data = {}
    for line in fm_text.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            data[k.strip()] = v.strip()
    return data


def audit_directory(memory_dir: Path):
    issues = {"orphans": [], "broken_links": [], "stale": [], "oversized_index": False}

    if not memory_dir.exists():
        print(f"  Directory not found: {memory_dir}")
        return issues

    index_path = memory_dir / "MEMORY.md"
    all_md = {f.name for f in memory_dir.glob("*.md") if f.name != "MEMORY.md"}

    linked = set()
    if index_path.exists():
        index_text = index_path.read_text(encoding="utf-8")
        index_lines = index_text.splitlines()
        issues["oversized_index"] = len(index_lines) > 180

        for line in index_lines:
            match = re.search(r"\[.*?\]\((.+?\.md)\)", line)
            if match:
                linked.add(match.group(1))

        for fname in linked:
            if fname not in all_md:
                issues["broken_links"].append(fname)
    else:
        issues["broken_links"].append("MEMORY.md is missing")

    issues["orphans"] = [f for f in all_md if f not in linked]

    today = date.today()
    for fname in all_md:
        fpath = memory_dir / fname
        text = fpath.read_text(encoding="utf-8", errors="ignore")
        fm = parse_frontmatter(text)
        mem_type = fm.get("type", "unknown")
        threshold = STALENESS_DAYS.get(mem_type, 30)
        updated_str = fm.get("updated", "")
        if updated_str:
            try:
                updated = datetime.strptime(updated_str, "%Y-%m-%d").date()
                age = (today - updated).days
                if age > threshold:
                    issues["stale"].append((fname, mem_type, updated_str, age))
            except ValueError:
                pass

    return issues


def main():
    dirs = [Path(sys.argv[1])] if len(sys.argv) > 1 else KNOWN_DIRS

    total_issues = 0
    for d in dirs:
        print(f"\n=== Auditing: {d} ===")
        issues = audit_directory(d)

        if issues["oversized_index"]:
            print("  WARNING: MEMORY.md approaching 200-line limit")
            total_issues += 1

        if issues["orphans"]:
            print(f"  Orphaned files ({len(issues['orphans'])}):")
            for f in issues["orphans"]:
                print(f"    - {f}")
            total_issues += len(issues["orphans"])

        if issues["broken_links"]:
            print(f"  Broken MEMORY.md links ({len(issues['broken_links'])}):")
            for f in issues["broken_links"]:
                print(f"    - {f}")
            total_issues += len(issues["broken_links"])

        if issues["stale"]:
            print(f"  Stale memories ({len(issues['stale'])}):")
            for fname, mem_type, updated, age in issues["stale"]:
                print(f"    - {fname} (type={mem_type}, updated={updated}, age={age}d)")
            total_issues += len(issues["stale"])

        if not any([issues["orphans"], issues["broken_links"], issues["stale"],
                    issues["oversized_index"]]):
            print("  All clear.")

    print(f"\nTotal issues found: {total_issues}")
    return 0 if total_issues == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
