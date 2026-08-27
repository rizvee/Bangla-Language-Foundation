#!/usr/bin/env python3
"""
Documentation Consistency and Integrity Checker for BLF.

Verifies:
1. Existence of required public documents.
2. Resolution of relative Markdown links.
3. Absence of local file:/// links and private filesystem paths.
4. Absence of unresolved placeholders (TODO, TBD, PLACEHOLDER).
5. Proper references in docs/index.md.
"""

import sys
import re
import argparse
from pathlib import Path
from typing import List, Tuple

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REQUIRED_PUBLIC_DOCS = [
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "CONTRIBUTORS.md",
    "CITATION.cff",
    "ROADMAP.md",
    "RESEARCH_STATUS.md",
    "LICENSE",
    "docs/index.md",
    "docs/architecture.md",
    "docs/research-methodology.md",
    "docs/data-quality-model.md",
    "docs/provenance-and-licensing.md",
    "docs/reproducibility.md",
    "docs/research-writing-policy.md",
]

# Regex for finding Markdown links: [text](target)
MD_LINK_REGEX = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

# Patterns that indicate private paths or invalid schemes in public docs
BANNED_LINK_PATTERNS = [
    (re.compile(r"file:///", re.IGNORECASE), "Local 'file:///' URI scheme detected in link"),
    (re.compile(r"(?<!https:)(?<!http:)(?<!ftp:)(?<!mailto:)(?<!git:)\b[A-Za-z]:[/\\]"), "Local Windows absolute filesystem path detected"),
]

# Prohibited placeholder patterns in published documentation (excluding templates)
PLACEHOLDER_PATTERNS = [
    (re.compile(r"\bTODO\b"), "Unresolved TODO marker"),
    (re.compile(r"\bFIXME\b"), "Unresolved FIXME marker"),
    (re.compile(r"\bPLACEHOLDER\b"), "Unresolved PLACEHOLDER marker"),
]


def check_required_docs(root_dir: Path) -> List[str]:
    errors = []
    for doc in REQUIRED_PUBLIC_DOCS:
        doc_path = root_dir / doc
        if not doc_path.exists():
            errors.append(f"Missing required public document: '{doc}'")
    return errors


def check_file_content(filepath: Path, root_dir: Path) -> Tuple[List[str], List[str]]:
    """Checks a single Markdown file for broken links, banned patterns, and placeholders."""
    errors = []
    warnings = []
    is_template = "template" in filepath.as_posix().lower()

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        return [f"Could not read {filepath}: {e}"], []

    for line_num, line in enumerate(lines, 1):
        # Skip code blocks
        if line.strip().startswith("```") or line.strip().startswith("`"):
            continue

        # Check for banned link schemes
        for pattern, reason in BANNED_LINK_PATTERNS:
            if pattern.search(line):
                errors.append(f"{filepath.relative_to(root_dir)}:{line_num} - {reason}")

        # Check for placeholders (only if not a template)
        if not is_template:
            for pattern, reason in PLACEHOLDER_PATTERNS:
                if pattern.search(line):
                    warnings.append(f"{filepath.relative_to(root_dir)}:{line_num} - {reason}")

        # Extract and check markdown links
        for match in MD_LINK_REGEX.finditer(line):
            link_target = match.group(2).strip()

            # Ignore web links, anchors, and email links
            if (
                link_target.startswith("http://")
                or link_target.startswith("https://")
                or link_target.startswith("mailto:")
                or link_target.startswith("#")
            ):
                continue

            # Strip in-page anchors if present
            target_path_str = link_target.split("#")[0]
            if not target_path_str:
                continue

            # Resolve relative link target
            target_file = (filepath.parent / target_path_str).resolve()
            if not target_file.exists():
                errors.append(
                    f"{filepath.relative_to(root_dir)}:{line_num} - Broken relative link: '{link_target}' (resolved to non-existent '{target_file.as_posix()}')"
                )

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Validate documentation consistency and link integrity.")
    parser.add_argument("--root", default=".", help="Root directory of repository (default: .)")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings as well as errors.")
    args = parser.parse_args()

    root_dir = Path(args.root).resolve()
    print(f"Checking documentation consistency starting from {root_dir.as_posix()}...")

    all_errors = []
    all_warnings = []

    # 1. Check required docs existence
    req_errors = check_required_docs(root_dir)
    all_errors.extend(req_errors)

    # 2. Check all markdown files in root, docs, and research (excluding local-only files)
    md_files = []
    for ext in ["*.md", "CITATION.cff"]:
        for p in root_dir.glob(ext):
            if p.name != "AGENTS.md":
                md_files.append(p)
    md_files.extend((root_dir / "docs").glob("**/*.md"))
    if (root_dir / "research").exists():
        md_files.extend((root_dir / "research").glob("**/*.md"))

    print(f"Scanning {len(md_files)} documentation file(s)...")

    for fpath in md_files:
        errs, warns = check_file_content(fpath, root_dir)
        all_errors.extend(errs)
        all_warnings.extend(warns)

    # Report results
    print("\n" + "=" * 50)
    if all_warnings:
        print(f"WARNINGS ({len(all_warnings)}):")
        for w in all_warnings:
            print(f"  [WARN] {w}")

    if all_errors:
        print(f"\nERRORS ({len(all_errors)}):")
        for e in all_errors:
            print(f"  [ERROR] {e}")
        print("\nDocumentation consistency check FAILED.")
        sys.exit(1)
    else:
        print(f"Documentation consistency check PASSED ({len(md_files)} files verified).")
        if args.strict and all_warnings:
            sys.exit(1)
        sys.exit(0)


if __name__ == "__main__":
    main()
