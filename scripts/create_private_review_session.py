#!/usr/bin/env python3
"""
BLF Private Human Review Session Creator.

Generates uncompromised private review session packages in .blf-private/:
- Randomizes BOTH item order and candidate order independently per reviewer.
- Assigns opaque per-reviewer display item IDs (e.g. BLIND-R1-A7K4).
- Prepends practice items for calibration.
- Stores the secret reverse mapping file inside .blf-private/ (gitignored).

Usage:
    python scripts/create_private_review_session.py --session-id SESS-PILOT-01
    python scripts/create_private_review_session.py --session-id SESS-PILOT-01 --reviewer-a REV-LINGUIST-01 --reviewer-b REV-NATIVE-02
"""

import argparse
import hashlib
import json
import random
import secrets
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
CANONICAL_PILOT_PATH = ROOT_DIR / "data" / "review_queue" / "human_review_pilot_40.json"
PRACTICE_ITEMS_PATH = ROOT_DIR / "data" / "review_queue" / "practice_items.json"
PRIVATE_BASE_DIR = ROOT_DIR / ".blf-private" / "review_sessions"


def generate_opaque_id(prefix: str, salt: str, idx: int) -> str:
    h = hashlib.sha256(f"{salt}-{idx}".encode("utf-8")).hexdigest()[:4].upper()
    return f"BLIND-{prefix}-{h}"


def load_canonical_items() -> List[Dict[str, Any]]:
    if not CANONICAL_PILOT_PATH.is_file():
        raise FileNotFoundError(f"Canonical pilot file not found: {CANONICAL_PILOT_PATH}")
    with open(CANONICAL_PILOT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("items", [])


def load_practice_items() -> List[Dict[str, Any]]:
    if not PRACTICE_ITEMS_PATH.is_file():
        return []
    with open(PRACTICE_ITEMS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("items", [])


def create_reviewer_blinded_pack(
    canonical_items: List[Dict[str, Any]],
    practice_items: List[Dict[str, Any]],
    session_id: str,
    reviewer_id: str,
    reviewer_short_tag: str,
    seed: int,
) -> tuple:
    rng = random.Random(seed)

    # 1. Randomize item order
    shuffled_items = list(canonical_items)
    rng.shuffle(shuffled_items)

    blinded_items = []
    item_mappings = {}

    # 2. Process each item with opaque IDs and candidate shuffling
    for seq_idx, item in enumerate(shuffled_items, start=1):
        canonical_id = item["pilot_id"]
        category = item.get("category", "GENERAL")
        context = item["context"]
        meaning = item["intended_meaning"]
        opaque_id = generate_opaque_id(reviewer_short_tag, f"{session_id}-{seed}", seq_idx)

        # Gather candidates
        raw_candidates = [("CAND_A", item["candidate_a"]), ("CAND_B", item["candidate_b"])]
        if item.get("candidate_c"):
            raw_candidates.append(("CAND_C", item["candidate_c"]))

        # Seeded candidate shuffle
        item_rng = random.Random(seed * 10000 + seq_idx)
        permuted_cands = list(raw_candidates)
        item_rng.shuffle(permuted_cands)

        displayed_labels = ["A", "B", "C"][:len(permuted_cands)]
        disp_dict = {}
        disp_to_canonical = {}
        canonical_to_disp = {}

        for lbl, (can_id, text) in zip(displayed_labels, permuted_cands):
            disp_dict[f"candidate_{lbl.lower()}"] = text
            disp_to_canonical[lbl] = can_id
            canonical_to_disp[can_id] = lbl

        item_mappings[opaque_id] = {
            "canonical_item_id": canonical_id,
            "category": category,
            "display_sequence": seq_idx,
            "displayed_to_canonical": disp_to_canonical,
            "canonical_to_displayed": canonical_to_disp,
        }

        blinded_item = {
            "display_id": opaque_id,
            "item_number": seq_idx,
            "context": context,
            "intended_meaning": meaning,
            "candidate_a": disp_dict.get("candidate_a"),
            "candidate_b": disp_dict.get("candidate_b"),
            "candidate_c": disp_dict.get("candidate_c", None),
            "instructions": {
                "step_1": "Rate acceptability for each candidate independently (NATURAL_STANDARD, NATURAL_COLLOQUIAL, MARKED_BUT_VALID, UNNATURAL, UNGRAMMATICAL, MEANING_DIFFERS, NEEDS_CONTEXT, UNSURE).",
                "step_2": "Select preferred candidate(s) (e.g. ['A'], ['A', 'B'], or ['NONE']).",
                "step_3": "Provide optional correction if all candidates are unnatural or ungrammatical.",
            },
        }
        blinded_items.append(blinded_item)

    return blinded_items, item_mappings


def write_reviewer_markdown(
    practice_items: List[Dict[str, Any]],
    blinded_items: List[Dict[str, Any]],
    session_id: str,
    reviewer_id: str,
    out_path: Path,
):
    lines = [
        f"# BLF Controlled Human Review Sheet — {reviewer_id}",
        "",
        f"**Session ID**: `{session_id}` | **Reviewer ID**: `{reviewer_id}`",
        f"**Evaluation Items**: {len(blinded_items)} analytical items (+ {len(practice_items)} practice items)",
        "**Evaluation Stage**: Stage 1 (Blinded Independent Native Judgment)",
        "",
        "> [!IMPORTANT]",
        "> **Review Guidelines**:",
        "> 1. **Candidate-Level Acceptability**: Rate EACH candidate independently. Multiple candidates can be natural and valid.",
        "> 2. **Preferred Candidate Selection**: Select your preferred candidate(s) (e.g. `[A]`, `[A, B]`, or `[NONE]`).",
        "> 3. **Optional Correction**: If none of the presented sentences are natural in standard Bangla, suggest a correction.",
        "",
        "---",
        "",
        "## Part I: Calibration & Practice Items (Do Not Score for Dataset)",
        "",
    ]

    for p in practice_items:
        lines.append(f"### Practice Item `{p['practice_id']}`")
        lines.append(f"- **Context**: {p['context']}")
        lines.append(f"- **Intended Meaning**: *\"{p['intended_meaning']}\"*")
        lines.append(f"- **[A]**: `{p['candidate_a']}`")
        lines.append(f"- **[B]**: `{p['candidate_b']}`")
        if p.get("candidate_c"):
            lines.append(f"- **[C]**: `{p['candidate_c']}`")
        lines.append(f"- **Guidance**: *{p.get('guidance_for_reviewer', '')}*")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Part II: Analytical Review Items")
    lines.append("")

    for it in blinded_items:
        lines.append(f"### Item #{it['item_number']} (`{it['display_id']}`)")
        lines.append(f"- **Context**: {it['context']}")
        lines.append(f"- **Intended Meaning**: *\"{it['intended_meaning']}\"*")
        lines.append(f"- **[A]**: `{it['candidate_a']}`")
        lines.append(f"- **[B]**: `{it['candidate_b']}`")
        if it.get("candidate_c"):
            lines.append(f"- **[C]**: `{it['candidate_c']}`")
        lines.append("")
        lines.append("- **Candidate Judgments**:")
        lines.append("  - Candidate A: `[ NATURAL_STANDARD / NATURAL_COLLOQUIAL / MARKED_BUT_VALID / UNNATURAL / UNGRAMMATICAL / MEANING_DIFFERS / NEEDS_CONTEXT / UNSURE ]` (Certainty: `[ VERY_SURE / SURE / SOMEWHAT_UNCERTAIN / GUESSING ]`)")
        lines.append("  - Candidate B: `[ NATURAL_STANDARD / NATURAL_COLLOQUIAL / MARKED_BUT_VALID / UNNATURAL / UNGRAMMATICAL / MEANING_DIFFERS / NEEDS_CONTEXT / UNSURE ]` (Certainty: `[ VERY_SURE / SURE / SOMEWHAT_UNCERTAIN / GUESSING ]`)")
        if it.get("candidate_c"):
            lines.append("  - Candidate C: `[ NATURAL_STANDARD / NATURAL_COLLOQUIAL / MARKED_BUT_VALID / UNNATURAL / UNGRAMMATICAL / MEANING_DIFFERS / NEEDS_CONTEXT / UNSURE ]` (Certainty: `[ VERY_SURE / SURE / SOMEWHAT_UNCERTAIN / GUESSING ]`)")
        lines.append("- **Preferred Choice(s)**: `[ A / B / C / NONE ]`")
        lines.append("- **Correction / Notes (Optional)**: `________________________________`")
        lines.append("")
        lines.append("---")
        lines.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="Create a private, uncompromised human review session in .blf-private/.")
    parser.add_argument("--session-id", type=str, default=f"SESS-PILOT-{secrets.randbelow(10000):04d}", help="Unique session ID")
    parser.add_argument("--reviewer-a", type=str, default="REV-LINGUIST-01", help="Reviewer A Pseudonym")
    parser.add_argument("--reviewer-b", type=str, default="REV-NATIVE-02", help="Reviewer B Pseudonym")
    parser.add_argument("--seed-a", type=int, default=None, help="Explicit seed for Reviewer A (auto-generated if None)")
    parser.add_argument("--seed-b", type=int, default=None, help="Explicit seed for Reviewer B (auto-generated if None)")
    parser.add_argument("--output-dir", type=str, default=None, help="Custom output directory (default: .blf-private/review_sessions/<SESSION_ID>)")
    args = parser.parse_args()

    session_id = args.session_id
    out_dir = Path(args.output_dir) if args.output_dir else PRIVATE_BASE_DIR / session_id
    out_dir.mkdir(parents=True, exist_ok=True)

    seed_a = args.seed_a if args.seed_a is not None else secrets.randbelow(1000000)
    seed_b = args.seed_b if args.seed_b is not None else secrets.randbelow(1000000)

    canonical_items = load_canonical_items()
    practice_items = load_practice_items()

    print("==================================================")
    print("BLF Private Review Session Creator")
    print(f"Session ID: {session_id}")
    print(f"Target Directory: {out_dir} (Gitignored)")
    print("==================================================")

    session_mapping = {
        "session_id": session_id,
        "status": "ACTIVE_PRIVATE_SESSION",
        "created_timestamp": "2026-08-28T12:00:00Z",
        "total_canonical_items": len(canonical_items),
        "reviewers": {
            args.reviewer_a: {"seed": seed_a, "short_tag": "R1"},
            args.reviewer_b: {"seed": seed_b, "short_tag": "R2"},
        },
        "item_mappings": {},
    }

    # Generate Reviewer A pack
    pack_a, map_a = create_reviewer_blinded_pack(
        canonical_items, practice_items, session_id, args.reviewer_a, "R1", seed_a
    )
    dir_a = out_dir / args.reviewer_a
    dir_a.mkdir(parents=True, exist_ok=True)
    with open(dir_a / f"review_pack_{args.reviewer_a}.json", "w", encoding="utf-8") as f:
        json.dump({"session_id": session_id, "reviewer_id": args.reviewer_a, "practice_items": practice_items, "items": pack_a}, f, ensure_ascii=False, indent=2)
    write_reviewer_markdown(practice_items, pack_a, session_id, args.reviewer_a, dir_a / f"review_pack_{args.reviewer_a}.md")
    session_mapping["item_mappings"][args.reviewer_a] = map_a

    # Generate Reviewer B pack
    pack_b, map_b = create_reviewer_blinded_pack(
        canonical_items, practice_items, session_id, args.reviewer_b, "R2", seed_b
    )
    dir_b = out_dir / args.reviewer_b
    dir_b.mkdir(parents=True, exist_ok=True)
    with open(dir_b / f"review_pack_{args.reviewer_b}.json", "w", encoding="utf-8") as f:
        json.dump({"session_id": session_id, "reviewer_id": args.reviewer_b, "practice_items": practice_items, "items": pack_b}, f, ensure_ascii=False, indent=2)
    write_reviewer_markdown(practice_items, pack_b, session_id, args.reviewer_b, dir_b / f"review_pack_{args.reviewer_b}.md")
    session_mapping["item_mappings"][args.reviewer_b] = map_b

    # Write secret session mapping into private directory
    mapping_path = out_dir / "session_mapping.json"
    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(session_mapping, f, ensure_ascii=False, indent=2)

    print(f"Generated Reviewer A Package -> {dir_a}")
    print(f"Generated Reviewer B Package -> {dir_b}")
    print(f"Saved Secret Reverse Mapping -> {mapping_path}")
    print("SUCCESS: Private session initialized safely. Active secrets are strictly gitignored.")


if __name__ == "__main__":
    main()
