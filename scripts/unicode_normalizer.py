#!/usr/bin/env python3
"""
CLI utility to normalize Bengali text files or strings to Unicode NFC.
"""

import sys
import argparse
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from blf.linguistics.normalizer import normalize_bangla_text, get_bengali_character_ratio


def main():
    parser = argparse.ArgumentParser(description="Normalize Bengali text to Unicode NFC and canonical punctuation.")
    parser.add_argument("--text", help="Direct text string to normalize.")
    parser.add_argument("--file", help="Path to text file to normalize.")
    parser.add_argument("--output", help="Optional output file path.")
    args = parser.parse_args()

    if args.text:
        normalized = normalize_bangla_text(args.text)
        ratio = get_bengali_character_ratio(normalized)
        print(f"Normalized: {normalized}")
        print(f"Bengali char ratio: {ratio:.2%}")
    elif args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        normalized = normalize_bangla_text(content)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(normalized)
            print(f"Normalized output written to: {args.output}")
        else:
            print(normalized)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
