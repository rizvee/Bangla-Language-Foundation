#!/usr/bin/env python3
"""
BLF Blinded Human Review Pack Generator & Candidate Randomizer.

Generates reviewer-specific blinded evaluation packages with seeded candidate
permutations. Guarantees zero leakage of system hypotheses, source authorities,
or internal confidence metrics to Stage 1 native evaluators.

Saves the secret reverse permutation lookup table in:
    data/review_queue/pilot_40_randomization_mapping.json

Emits reviewer-facing blinded packages into:
    data/review_queue/blinded_packs/pilot_40_blinded_<REVIEWER_ID>.json
    data/review_queue/blinded_packs/pilot_40_blinded_<REVIEWER_ID>.md

Usage:
    python scripts/generate_blinded_pilot.py
"""

import json
import random
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
REVIEW_DIR = ROOT_DIR / "data" / "review_queue"
BLINDED_DIR = REVIEW_DIR / "blinded_packs"
BLINDED_DIR.mkdir(parents=True, exist_ok=True)

CANONICAL_PILOT_PATH = REVIEW_DIR / "human_review_pilot_40.json"
MAPPING_OUT_PATH = REVIEW_DIR / "pilot_40_randomization_mapping.json"

REVIEWER_CONFIGS = [
    {
        "reviewer_id": "REV-LINGUIST-01",
        "role": "NATIVE_LINGUIST",
        "seed": 101,
        "description": "Primary native linguist reviewer pack",
    },
    {
        "reviewer_id": "REV-NATIVE-02",
        "role": "NATIVE_EDUCATED_SPEAKER",
        "seed": 202,
        "description": "Independent native educated speaker reviewer pack",
    },
]


def load_canonical_pilot() -> List[Dict[str, Any]]:
    if not CANONICAL_PILOT_PATH.is_file():
        raise FileNotFoundError(f"Canonical pilot file not found: {CANONICAL_PILOT_PATH}")
    with open(CANONICAL_PILOT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("items", [])


def generate_blinded_pack(
    canonical_items: List[Dict[str, Any]],
    reviewer_id: str,
    seed: int,
) -> tuple:
    blinded_items = []
    mapping_dict = {}

    for idx, item in enumerate(canonical_items, start=1):
        item_id = item["pilot_id"]
        category = item.get("category", "GENERAL")
        context = item["context"]
        meaning = item["intended_meaning"]

        # Gather available candidate options
        raw_candidates = [("CAND_A", item["candidate_a"]), ("CAND_B", item["candidate_b"])]
        if item.get("candidate_c"):
            raw_candidates.append(("CAND_C", item["candidate_c"]))

        # Seeded deterministic shuffle per item
        rng = random.Random(seed * 1000 + idx)
        permuted = list(raw_candidates)
        rng.shuffle(permuted)

        displayed_labels = ["A", "B", "C"][:len(permuted)]
        displayed_candidates = {}
        disp_to_canonical = {}
        canonical_to_disp = {}

        for lbl, (can_id, text) in zip(displayed_labels, permuted):
            displayed_candidates[f"candidate_{lbl.lower()}"] = text
            disp_to_canonical[lbl] = can_id
            canonical_to_disp[can_id] = lbl

        mapping_dict[item_id] = {
            "displayed_to_canonical": disp_to_canonical,
            "canonical_to_displayed": canonical_to_disp,
        }

        # Human-facing blinded record (strictly omitting hypotheses and sources)
        blinded_item = {
            "display_id": f"BLIND-{idx:03d}",
            "item_id": item_id,
            "category": category,
            "context": context,
            "intended_meaning": meaning,
            "candidate_a": displayed_candidates.get("candidate_a"),
            "candidate_b": displayed_candidates.get("candidate_b"),
            "candidate_c": displayed_candidates.get("candidate_c", None),
            "judgment_options": [
                "NATURAL_STANDARD",
                "NATURAL_COLLOQUIAL",
                "MARKED_BUT_VALID",
                "UNNATURAL",
                "UNGRAMMATICAL",
                "MEANING_DIFFERS",
                "NEEDS_CONTEXT",
                "UNSURE",
            ],
            "instructions": "Select preferred candidate (A, B, C, or NONE) and provide categorical acceptability rating for standard/colloquial BDSB.",
        }
        blinded_items.append(blinded_item)

    return blinded_items, mapping_dict


def write_blinded_markdown(items: List[Dict[str, Any]], reviewer_id: str, out_path: Path):
    lines = [
        f"# BLF Controlled Human Review Pilot (Blinded Package — {reviewer_id})",
        "",
        f"**Reviewer ID**: `{reviewer_id}`",
        f"**Total Items**: {len(items)}",
        "**Evaluation Stage**: Stage 1 (Blinded Independent Native Judgment)",
        "",
        "> [!IMPORTANT]",
        "> **Instructions for Evaluator**:",
        "> 1. Please read the **Context** and **Intended Meaning** for each item.",
        "> 2. Evaluate the presented Bangla sentence candidates (**A**, **B**, and **C** if present).",
        "> 3. Select your **Preferred Candidate** and assign a **Categorical Judgment**.",
        "> 4. If none of the forms are natural, provide an optional **Correction** in standard Bangla spelling.",
        "",
        "---",
        "",
    ]

    for it in items:
        lines.append(f"### Item `{it['display_id']}` (`{it['category']}`)")
        lines.append(f"- **Context**: {it['context']}")
        lines.append(f"- **Intended Meaning**: *\"{it['intended_meaning']}\"*")
        lines.append(f"- **[A]**: `{it['candidate_a']}`")
        lines.append(f"- **[B]**: `{it['candidate_b']}`")
        if it.get("candidate_c"):
            lines.append(f"- **[C]**: `{it['candidate_c']}`")
        lines.append("")
        lines.append("- **Preferred Choice**: `[ A / B / C / NONE ]`")
        lines.append("- **Judgment**: `[ NATURAL_STANDARD / NATURAL_COLLOQUIAL / MARKED_BUT_VALID / UNNATURAL / UNGRAMMATICAL / MEANING_DIFFERS / NEEDS_CONTEXT / UNSURE ]`")
        lines.append("- **Certainty**: `[ VERY_SURE / SURE / SOMEWHAT_UNCERTAIN / GUESSING ]`")
        lines.append("- **Correction / Comments (Optional)**: `________________________________`")
        lines.append("")
        lines.append("---")
        lines.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    print("==================================================")
    print("BLF Blinded Pilot & Randomization Generator")
    print("==================================================")

    canonical_items = load_canonical_pilot()
    print(f"Loaded {len(canonical_items)} canonical pilot items.")

    master_mapping = {
        "version": "1.0.0",
        "pilot_id": "BLF-PILOT-40",
        "total_items": len(canonical_items),
        "reviewers": {},
    }

    for cfg in REVIEWER_CONFIGS:
        rid = cfg["reviewer_id"]
        seed = cfg["seed"]
        blinded_items, mapping = generate_blinded_pack(canonical_items, rid, seed)

        master_mapping["reviewers"][rid] = {
            "seed": seed,
            "role": cfg["role"],
            "item_mappings": mapping,
        }

        # Write blinded JSON pack
        json_out = BLINDED_DIR / f"pilot_40_blinded_{rid}.json"
        blinded_payload = {
            "title": f"BLF Blinded Human Review Pilot ({rid})",
            "reviewer_id": rid,
            "total_items": len(blinded_items),
            "evaluation_stage": "STAGE_1_BLINDED_NATIVE_JUDGMENT",
            "items": blinded_items,
        }
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(blinded_payload, f, ensure_ascii=False, indent=2)

        # Write blinded Markdown pack
        md_out = BLINDED_DIR / f"pilot_40_blinded_{rid}.md"
        write_blinded_markdown(blinded_items, rid, md_out)
        print(f"Generated blinded package for {rid} -> {json_out.name} and {md_out.name}")

    # Write secret reverse mapping file
    with open(MAPPING_OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(master_mapping, f, ensure_ascii=False, indent=2)
    print(f"Saved secret reverse permutation mapping -> {MAPPING_OUT_PATH.name}")
    print("SUCCESS: Stage 1 blinded packages generated with zero source/hypothesis leakage.")


if __name__ == "__main__":
    main()
