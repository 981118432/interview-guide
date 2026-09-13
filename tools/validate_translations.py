#!/usr/bin/env python3
"""Validate Markdown translation pairs without comparing translated prose."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path


def heading_levels(text: str) -> list[int]:
    return [len(match.group(1)) for match in re.finditer(r"^(#{1,6})\s+", text, re.M)]


def fence_signatures(text: str) -> list[str]:
    return [line.strip() for line in re.findall(r"^(```[^\n]*)$", text, re.M)]


def table_shape(text: str) -> list[tuple[int, bool]]:
    rows = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("|"):
            rows.append((len(line.strip("|").split("|")), bool(re.fullmatch(r"[|:\-\s]+", line))))
    return rows


def link_targets(text: str) -> Counter[str]:
    return Counter(match.group(2) for match in re.finditer(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)", text))


def raw_urls(text: str) -> Counter[str]:
    return Counter(re.findall(r"https?://[^\s)>]+", text))


def horizontal_rules(text: str) -> Counter[str]:
    return Counter(
        line.strip()
        for line in text.splitlines()
        if re.fullmatch(r"\s{0,3}([-*_])(?:\s*\1){2,}\s*", line)
    )


def code_blocks(text: str) -> Counter[str]:
    blocks: list[str] = []
    current: list[str] = []
    inside = False
    for line in text.splitlines():
        if line.startswith("```"):
            if inside:
                blocks.append("\n".join(item.rstrip() for item in current).strip())
                current = []
            inside = not inside
        elif inside:
            current.append(line)
    return Counter(blocks)


def source_docs(directory: Path) -> list[Path]:
    return sorted(
        path
        for path in directory.glob("*.md")
        if not path.name.endswith((".zh.md", ".summary.md"))
    )


def validate(directory: Path) -> list[str]:
    errors: list[str] = []
    for source in source_docs(directory):
        zh = source.with_name(source.stem + ".zh.md")
        summary = source.with_name(source.stem + ".summary.md")
        if not zh.exists():
            errors.append(f"{source.name}: missing {zh.name}")
            continue
        if not summary.exists():
            errors.append(f"{source.name}: missing {summary.name}")
        english = source.read_text()
        chinese = zh.read_text()
        checks = [
            ("heading-levels", heading_levels(english), heading_levels(chinese)),
            ("fence-signatures", fence_signatures(english), fence_signatures(chinese)),
            ("table-shape", table_shape(english), table_shape(chinese)),
            ("link-targets", link_targets(english), link_targets(chinese)),
            ("raw-urls", raw_urls(english), raw_urls(chinese)),
            ("horizontal-rules", horizontal_rules(english), horizontal_rules(chinese)),
            ("code-blocks", code_blocks(english), code_blocks(chinese)),
        ]
        for name, expected, actual in checks:
            if expected != actual:
                errors.append(f"{source.name}: {name} mismatch")
        if summary.exists():
            summary_text = summary.read_text().strip()
            if not summary_text:
                errors.append(f"{source.name}: empty summary")
            chinese_title = next(
                (line[2:].strip() for line in chinese.splitlines() if line.startswith("# ")), ""
            )
            first_summary_line = summary_text.splitlines()[0] if summary_text else ""
            if chinese_title and chinese_title not in first_summary_line:
                base_title = re.sub(r"（[^）]*）$", "", chinese_title)
                if base_title not in first_summary_line:
                    errors.append(f"{source.name}: summary title mismatch")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directories", nargs="+", type=Path)
    args = parser.parse_args()
    total = 0
    errors: list[str] = []
    for directory in args.directories:
        directory_errors = validate(directory)
        count = len(source_docs(directory))
        total += count
        errors.extend(f"{directory}/{item}" for item in directory_errors)
    print(f"validated_docs={total}")
    print(f"errors={len(errors)}")
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
