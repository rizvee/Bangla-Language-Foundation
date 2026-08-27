#!/usr/bin/env python3
"""
Anti-AI-Slop and Writing Integrity Checker for BLF.

Scans Markdown and text files for canned AI phrases, excessive padding,
and empty rhetorical framing.
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

# Patterns strictly banned or heavily flagged when used as rhetorical filler
SLOP_PATTERNS = [
    (re.compile(r"\bdelve\b|\bdelving\b", re.IGNORECASE), "Banned canned verb: 'delve' / 'delving'"),
    (re.compile(r"\bleveraging\b|\bleverage\b", re.IGNORECASE), "Banned corporate/LLM buzzword: 'leverage' / 'leveraging'"),
    (re.compile(r"\bgroundbreaking\b", re.IGNORECASE), "Unsubstantiated superlative: 'groundbreaking'"),
    (re.compile(r"\brevolutionize\b|\brevolutionizing\b", re.IGNORECASE), "Unsubstantiated superlative: 'revolutionize'"),
    (re.compile(r"\bunlock\s+(?:the\s+)?(?:potential|power|future)\b", re.IGNORECASE), "Marketing cliché: 'unlock the potential/power'"),
    (re.compile(r"\btestament to\b", re.IGNORECASE), "Canned LLM formula: 'testament to'"),
    (re.compile(r"\bplays a (?:crucial|pivotal|vital|key) role\b", re.IGNORECASE), "Empty transition: 'plays a crucial/pivotal role'"),
    (re.compile(r"\bit is (?:important|crucial|vital|worth noting) to note\b", re.IGNORECASE), "Throat-clearing filler: 'it is important to note'"),
    (re.compile(r"\bin today'?s (?:rapidly evolving|dynamic|fast-paced)\b", re.IGNORECASE), "Generic introductory cliché: 'in today's rapidly evolving...'"),
    (re.compile(r"\bmultifaceted\b", re.IGNORECASE), "Canned adjective: 'multifaceted'"),
    (re.compile(r"\bintricate\b", re.IGNORECASE), "Canned adjective: 'intricate' (verify if genuine technical use)"),
    (re.compile(r"\bnot only\b.*?\bbut also\b", re.IGNORECASE), "Formulaic parallel symmetry: 'not only ... but also'"),
]


def scan_file(filepath: Path) -> List[Tuple[int, str, str]]:
    """Scans a file line by line for slop patterns. Returns list of (line_num, line_text, reason)."""
    violations = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                # Skip markdown code blocks / quotes if needed, or scan all
                stripped = line.strip()
                if stripped.startswith("`") or stripped.startswith("$"):
                    continue
                for pattern, reason in SLOP_PATTERNS:
                    if pattern.search(line):
                        violations.append((line_num, stripped, reason))
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
    return violations


def main():
    parser = argparse.ArgumentParser(description="Scan BLF documentation and research notes for AI slop.")
    parser.add_argument("--path", default="docs", help="Directory or file to scan (default: docs)")
    parser.add_argument("--strict", action="store_true", help="Fail with non-zero code on any violation.")
    args = parser.parse_args()

    target_path = Path(args.path)
    if not target_path.exists():
        print(f"Target path does not exist: {target_path}")
        sys.exit(0)

    files_to_scan = []
    if target_path.is_file():
        files_to_scan.append(target_path)
    else:
        files_to_scan.extend(target_path.glob("**/*.md"))
        files_to_scan.extend(target_path.glob("**/*.txt"))

    total_violations = 0
    print(f"Scanning {len(files_to_scan)} file(s) for AI slop and writing artifacts...")

    for filepath in files_to_scan:
        # Skip the policy documents themselves which mention the banned words as examples!
        if filepath.name in ["anti-ai-slop.md", "research-writing-policy.md", "check_anti_slop.py"]:
            continue

        violations = scan_file(filepath)
        if violations:
            total_violations += len(violations)
            print(f"\n[FLAGGED] {filepath.as_posix()}:")
            for line_num, text, reason in violations:
                print(f"  Line {line_num}: {reason}")
                print(f"    Snippet: \"{text[:100]}\"")

    print("\n" + "=" * 50)
    if total_violations == 0:
        print("OK: No AI slop patterns detected. Writing passes integrity standards.")
        sys.exit(0)
    else:
        print(f"WARNING: Found {total_violations} potential AI slop violation(s).")
        if args.strict:
            sys.exit(1)
        sys.exit(0)


if __name__ == "__main__":
    main()
