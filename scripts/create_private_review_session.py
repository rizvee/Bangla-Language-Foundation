#!/usr/bin/env python3
"""
BLF Private Human Review Session Creator — Phase 2A.2d.

Generates uncompromised private review session packages in .blf-private/:
- Enforces Consent Gate (REAL sessions require pre-existing machine-readable consent).
- Uses strong 128-bit private randomness (secrets.randbits(128)) for seed generation.
- Never prints active seeds to stdout.
- Disallows output targeting tracked public repository directories.
- Randomizes BOTH item order and candidate order independently per reviewer.
- Assigns opaque per-reviewer display item IDs (e.g. BLIND-R1-A7K4).
- Prepends de-primed practice items for calibration.
- Generates clean submission templates (submission_template_<reviewer>.json).
- Stores secret reverse mappings inside .blf-private/ (gitignored).

Usage:
    # DEMO mode (software test fixtures only):
    python scripts/create_private_review_session.py --mode DEMO --session-id SESS-DEMO-01

    # REAL mode (requires pre-recorded consent in .blf-private/consent/):
    python scripts/create_private_review_session.py --mode REAL --session-id SESS-PILOT-01 --reviewer-a REV-LINGUIST-01 --reviewer-b REV-NATIVE-02
"""

import argparse
import hashlib
import json
import random
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
CANONICAL_PILOT_PATH = ROOT_DIR / "data" / "review_queue" / "human_review_pilot_40.json"
PRACTICE_ITEMS_PATH = ROOT_DIR / "data" / "review_queue" / "practice_items.json"
PRIVATE_BASE_DIR = ROOT_DIR / ".blf-private" / "review_sessions"
CONSENT_BASE_DIR = ROOT_DIR / ".blf-private" / "consent"


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


def load_consent_record(reviewer_pseudonym: str, consent_dir: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Loads a private machine-readable consent record for a reviewer if it exists."""
    c_dir = consent_dir or CONSENT_BASE_DIR
    if not c_dir.is_dir():
        return None
    for c_file in c_dir.glob("*.json"):
        try:
            with open(c_file, "r", encoding="utf-8") as f:
                rec = json.load(f)
            if rec.get("reviewer_pseudonym") == reviewer_pseudonym and rec.get("withdrawal_status") == "ACTIVE":
                if rec.get("consent_confirmed") is True and rec.get("consent_to_anonymized_research_use") is True:
                    return rec
        except Exception:
            continue
    return None


def create_reviewer_blinded_pack(
    canonical_items: List[Dict[str, Any]],
    practice_items: List[Dict[str, Any]],
    session_id: str,
    reviewer_id: str,
    reviewer_short_tag: str,
    seed: int,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
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


def create_submission_template(
    blinded_items: List[Dict[str, Any]],
    session_id: str,
    reviewer_id: str,
    consent_record_id: str,
    pilot_version: str = "1.0.0",
) -> Dict[str, Any]:
    """
    Generates a clean submission template matching schemas/v0_1/reviewer_submission_bundle.schema.json.
    Withholds canonical item IDs, categories, rules, and source IDs.
    """
    reviews = []
    for it in blinded_items:
        cand_judg = {
            "A": {"acceptability": "", "certainty": ""},
            "B": {"acceptability": "", "certainty": ""},
        }
        if it.get("candidate_c"):
            cand_judg["C"] = {"acceptability": "", "certainty": ""}

        reviews.append({
            "opaque_item_id": it["display_id"],
            "candidate_judgments": cand_judg,
            "preferred_candidates": [],
            "correction": None,
            "comments": None,
        })

    return {
        "bundle_id": f"REV-BUNDLE-{reviewer_id}-{session_id}",
        "session_id": session_id,
        "reviewer_pseudonym": reviewer_id,
        "pilot_version": pilot_version,
        "consent_record_id": consent_record_id,
        "submitted_at": "",
        "reviews": reviews,
    }


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
        lines.append(f"- **Calibration Goal**: *{p.get('interface_concept_taught', 'Rate candidates independently and select preferred candidate(s).')}*")
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
    parser.add_argument("--mode", type=str, choices=["REAL", "DEMO"], default="REAL", help="Execution mode (REAL requires verified consent; DEMO creates software test fixtures)")
    parser.add_argument("--session-id", type=str, default=None, help="Unique session ID (e.g. SESS-PILOT-01)")
    parser.add_argument("--reviewer-a", type=str, default="REV-LINGUIST-01", help="Reviewer A Pseudonym")
    parser.add_argument("--reviewer-b", type=str, default="REV-NATIVE-02", help="Reviewer B Pseudonym")
    parser.add_argument("--seed-a", type=int, default=None, help="Explicit seed for Reviewer A (auto-generated if None)")
    parser.add_argument("--seed-b", type=int, default=None, help="Explicit seed for Reviewer B (auto-generated if None)")
    parser.add_argument("--output-dir", type=str, default=None, help="Custom output directory (default: .blf-private/review_sessions/<SESSION_ID>)")
    parser.add_argument("--consent-dir", type=str, default=None, help="Custom consent directory (default: .blf-private/consent)")
    args = parser.parse_args()

    # Determine session ID
    session_id = args.session_id or (f"SESS-DEMO-{secrets.randbelow(10000):04d}" if args.mode == "DEMO" else f"SESS-PILOT-{secrets.randbelow(10000):04d}")

    # Determine and validate output directory
    out_dir = Path(args.output_dir) if args.output_dir else PRIVATE_BASE_DIR / session_id

    # Security invariant: REAL mode cannot output to tracked git directories
    if args.mode == "REAL":
        resolved_out = out_dir.resolve()
        resolved_root = ROOT_DIR.resolve()
        if resolved_out == resolved_root or (resolved_out.is_relative_to(resolved_root) and not str(resolved_out).startswith(str(ROOT_DIR / ".blf-private"))):
            raise PermissionError(
                f"Security violation: REAL mode cannot output private session mappings or packs to tracked directory '{out_dir}'. Must be within .blf-private/."
            )

    out_dir.mkdir(parents=True, exist_ok=True)

    # Consent verification gate
    consent_dir = Path(args.consent_dir) if args.consent_dir else CONSENT_BASE_DIR
    consent_a = None
    consent_b = None

    if args.mode == "REAL":
        consent_a = load_consent_record(args.reviewer_a, consent_dir)
        if not consent_a:
            raise PermissionError(
                f"Consent gate failure: No active verified consent record found for Reviewer A '{args.reviewer_a}'. "
                "Current reviewer status is UNKNOWN/NOT YET PROVIDED. Review sessions cannot be created without explicit consent."
            )
        consent_b = load_consent_record(args.reviewer_b, consent_dir)
        if not consent_b:
            raise PermissionError(
                f"Consent gate failure: No active verified consent record found for Reviewer B '{args.reviewer_b}'. "
                "Current reviewer status is UNKNOWN/NOT YET PROVIDED. Review sessions cannot be created without explicit consent."
            )
    else:
        # DEMO mode: Synthetic consent fixtures
        consent_a = {
            "consent_record_id": f"CONSENT-DEMO-{args.reviewer_a}",
            "reviewer_pseudonym": args.reviewer_a,
            "session_id": session_id,
            "information_sheet_version": "2.0.0",
            "consent_confirmed": True,
            "consent_confirmed_at": datetime.now(timezone.utc).isoformat(),
            "consent_to_anonymized_research_use": True,
            "consent_to_anonymized_public_release": True,
            "withdrawal_status": "ACTIVE",
            "notes": "SYNTHETIC_SOFTWARE_TEST_ONLY",
        }
        consent_b = {
            "consent_record_id": f"CONSENT-DEMO-{args.reviewer_b}",
            "reviewer_pseudonym": args.reviewer_b,
            "session_id": session_id,
            "information_sheet_version": "2.0.0",
            "consent_confirmed": True,
            "consent_confirmed_at": datetime.now(timezone.utc).isoformat(),
            "consent_to_anonymized_research_use": True,
            "consent_to_anonymized_public_release": True,
            "withdrawal_status": "ACTIVE",
            "notes": "SYNTHETIC_SOFTWARE_TEST_ONLY",
        }

    # Cryptographically strong 128-bit private seeds
    seed_a = args.seed_a if args.seed_a is not None else secrets.randbits(128)
    seed_b = args.seed_b if args.seed_b is not None else secrets.randbits(128)

    canonical_items = load_canonical_items()
    practice_items = load_practice_items()

    print("==================================================")
    print("BLF Private Review Session Creator")
    print(f"Mode: {args.mode}")
    print(f"Session ID: {session_id}")
    print(f"Target Directory: {out_dir} (Private / Ignored)")
    print("==================================================")

    session_mapping = {
        "session_id": session_id,
        "mode": args.mode,
        "status": "ACTIVE_PRIVATE_SESSION",
        "created_timestamp": datetime.now(timezone.utc).isoformat(),
        "session_generator_version": "2.0.0",
        "pilot_version": "1.0.0",
        "practice_version": "2.0.0",
        "schema_version": "v0.1",
        "total_canonical_items": len(canonical_items),
        "reviewers": {
            args.reviewer_a: {
                "short_tag": "R1",
                "seed": seed_a,
                "consent_record_id": consent_a["consent_record_id"],
            },
            args.reviewer_b: {
                "short_tag": "R2",
                "seed": seed_b,
                "consent_record_id": consent_b["consent_record_id"],
            },
        },
        "item_mappings": {},
    }

    # Generate Reviewer A pack & template
    pack_a, map_a = create_reviewer_blinded_pack(
        canonical_items, practice_items, session_id, args.reviewer_a, "R1", seed_a
    )
    dir_a = out_dir / args.reviewer_a
    dir_a.mkdir(parents=True, exist_ok=True)
    with open(dir_a / f"review_pack_{args.reviewer_a}.json", "w", encoding="utf-8") as f:
        json.dump({"session_id": session_id, "reviewer_id": args.reviewer_a, "practice_items": practice_items, "items": pack_a}, f, ensure_ascii=False, indent=2)
    write_reviewer_markdown(practice_items, pack_a, session_id, args.reviewer_a, dir_a / f"review_pack_{args.reviewer_a}.md")
    template_a = create_submission_template(pack_a, session_id, args.reviewer_a, consent_a["consent_record_id"])
    with open(dir_a / f"submission_template_{args.reviewer_a}.json", "w", encoding="utf-8") as f:
        json.dump(template_a, f, ensure_ascii=False, indent=2)
    session_mapping["item_mappings"][args.reviewer_a] = map_a

    # Generate Reviewer B pack & template
    pack_b, map_b = create_reviewer_blinded_pack(
        canonical_items, practice_items, session_id, args.reviewer_b, "R2", seed_b
    )
    dir_b = out_dir / args.reviewer_b
    dir_b.mkdir(parents=True, exist_ok=True)
    with open(dir_b / f"review_pack_{args.reviewer_b}.json", "w", encoding="utf-8") as f:
        json.dump({"session_id": session_id, "reviewer_id": args.reviewer_b, "practice_items": practice_items, "items": pack_b}, f, ensure_ascii=False, indent=2)
    write_reviewer_markdown(practice_items, pack_b, session_id, args.reviewer_b, dir_b / f"review_pack_{args.reviewer_b}.md")
    template_b = create_submission_template(pack_b, session_id, args.reviewer_b, consent_b["consent_record_id"])
    with open(dir_b / f"submission_template_{args.reviewer_b}.json", "w", encoding="utf-8") as f:
        json.dump(template_b, f, ensure_ascii=False, indent=2)
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
