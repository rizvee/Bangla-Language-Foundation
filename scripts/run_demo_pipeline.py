#!/usr/bin/env python3
"""
BLF End-to-End Synthetic DEMO Pipeline Runner — Phase 2A.2d.

Executes a complete synthetic end-to-end verification run:
1. Generates DEMO session with synthetic consent in .blf-private/demo_pipeline/
2. Populates 2 complete 40-item synthetic submission bundles using generated templates
3. Runs fail-closed raw bundle validation
4. Decodes raw submissions with SHA-256 immutability hashes
5. Validates decoded records against decoded_review_record.schema.json
6. Evaluates dual-target IAA under enforce_official_completeness=True
7. Exports disagreement queue for Stage 2 adjudication

ALL ARTIFACTS ARE LABELED: SYNTHETIC_SOFTWARE_TEST_ONLY
NOT HUMAN EVIDENCE. NOT GOLD DATA.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
DEMO_DIR = ROOT_DIR / ".blf-private" / "demo_pipeline"


def run_command(cmd_list: list) -> None:
    print(f"Executing: {' '.join(cmd_list)}")
    res = subprocess.run(cmd_list, capture_output=True, text=True, encoding="utf-8")
    if res.stdout:
        print(res.stdout)
    if res.returncode != 0:
        print(f"Error output: {res.stderr}", file=sys.stderr)
        raise RuntimeError(f"Command failed with exit code {res.returncode}: {' '.join(cmd_list)}")


def main():
    print("==================================================")
    print("BLF End-to-End Synthetic DEMO Pipeline")
    print("STATUS: SYNTHETIC_SOFTWARE_TEST_ONLY (NOT HUMAN EVIDENCE)")
    print("==================================================")

    if DEMO_DIR.exists():
        shutil.rmtree(DEMO_DIR)
    DEMO_DIR.mkdir(parents=True, exist_ok=True)

    session_id = "SESS-DEMO-E2E"
    rev_a = "REV-SYNTH-01"
    rev_b = "REV-SYNTH-02"
    sess_dir = DEMO_DIR / "session"

    # Step 1: Create private DEMO session
    print("\n[Step 1/5] Creating private DEMO session with synthetic consent...")
    run_command([
        sys.executable,
        str(ROOT_DIR / "scripts" / "create_private_review_session.py"),
        "--mode", "DEMO",
        "--session-id", session_id,
        "--reviewer-a", rev_a,
        "--reviewer-b", rev_b,
        "--output-dir", str(sess_dir),
    ])

    mapping_path = sess_dir / "session_mapping.json"
    template_a_path = sess_dir / rev_a / f"submission_template_{rev_a}.json"
    template_b_path = sess_dir / rev_b / f"submission_template_{rev_b}.json"

    # Step 2: Populate synthetic complete submissions
    print("\n[Step 2/5] Populating complete 40-item synthetic submissions from templates...")
    with open(template_a_path, "r", encoding="utf-8") as f:
        sub_a = json.load(f)
    with open(template_b_path, "r", encoding="utf-8") as f:
        sub_b = json.load(f)

    now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sub_a["submitted_at"] = now_ts
    sub_b["submitted_at"] = now_ts

    # Fill review items
    for idx, (item_a, item_b) in enumerate(zip(sub_a["reviews"], sub_b["reviews"]), start=1):
        # Reviewer A ratings
        for k in item_a["candidate_judgments"].keys():
            item_a["candidate_judgments"][k]["acceptability"] = "NATURAL_STANDARD" if k == "A" else "UNGRAMMATICAL"
            item_a["candidate_judgments"][k]["certainty"] = "VERY_SURE"
        item_a["preferred_candidates"] = ["A"]

        # Reviewer B ratings (introduce 2 minor disagreements at items 10 and 20)
        for k in item_b["candidate_judgments"].keys():
            if idx in (10, 20) and k == "B":
                item_b["candidate_judgments"][k]["acceptability"] = "MARKED_BUT_VALID"
            else:
                item_b["candidate_judgments"][k]["acceptability"] = "NATURAL_STANDARD" if k == "A" else "UNGRAMMATICAL"
            item_b["candidate_judgments"][k]["certainty"] = "SURE"
        item_b["preferred_candidates"] = ["A"]

    subs_dir = DEMO_DIR / "submissions"
    subs_dir.mkdir(parents=True, exist_ok=True)
    raw_sub_a_path = subs_dir / f"raw_submission_{rev_a}.json"
    raw_sub_b_path = subs_dir / f"raw_submission_{rev_b}.json"

    with open(raw_sub_a_path, "w", encoding="utf-8") as f:
        json.dump(sub_a, f, ensure_ascii=False, indent=2)
    with open(raw_sub_b_path, "w", encoding="utf-8") as f:
        json.dump(sub_b, f, ensure_ascii=False, indent=2)

    # Step 3: Decode submissions with fail-closed validation
    print("\n[Step 3/5] Decoding raw submissions with fail-closed integrity checks...")
    decoded_dir = DEMO_DIR / "decoded"
    decoded_dir.mkdir(parents=True, exist_ok=True)
    dec_a_path = decoded_dir / f"decoded_{rev_a}.json"
    dec_b_path = decoded_dir / f"decoded_{rev_b}.json"

    run_command([
        sys.executable,
        str(ROOT_DIR / "scripts" / "decode_review_submissions.py"),
        "--session-mapping", str(mapping_path),
        "--submission", str(raw_sub_a_path),
        "--output-decoded", str(dec_a_path),
    ])

    run_command([
        sys.executable,
        str(ROOT_DIR / "scripts" / "decode_review_submissions.py"),
        "--session-mapping", str(mapping_path),
        "--submission", str(raw_sub_b_path),
        "--output-decoded", str(dec_b_path),
    ])

    # Step 4: Compute dual IAA under official completeness gate
    print("\n[Step 4/5] Computing dual-target IAA under enforce_official_completeness...")
    report_path = DEMO_DIR / "iaa_report.json"
    disagreements_path = DEMO_DIR / "disagreements.json"

    run_command([
        sys.executable,
        str(ROOT_DIR / "scripts" / "compute_iaa.py"),
        "--input-decoded-a", str(dec_a_path),
        "--input-decoded-b", str(dec_b_path),
        "--reviewer-a", rev_a,
        "--reviewer-b", rev_b,
        "--enforce-completeness",
        "--output-report", str(report_path),
        "--output-disagreements", str(disagreements_path),
    ])

    # Step 5: Verify results
    print("\n[Step 5/5] Verifying DEMO execution outputs...")
    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    assert report["completeness_report"]["is_official_study_complete"] is True
    assert report["common_evaluated_items"] == 40
    assert report["candidate_acceptability"]["total_candidate_pairs"] == 120
    assert report["preferred_candidates"]["total_items"] == 40

    print("==================================================")
    print("DEMO PIPELINE VERIFICATION SUCCESSFUL")
    print(f"Evaluated Pairs: {report['candidate_acceptability']['total_candidate_pairs']} candidate observations")
    print(f"Cohen's Kappa (κ): {report['candidate_acceptability']['cohens_kappa']:.3f}")
    print(f"Preferred Match Rate: {report['preferred_candidates']['exact_match_rate'] * 100:.1f}%")
    print("Integrity: All artifacts verified in .blf-private/demo_pipeline/")
    print("STATUS CONFIRMED: SYNTHETIC_SOFTWARE_TEST_ONLY")
    print("==================================================")


if __name__ == "__main__":
    main()
