# Changelog

All notable changes to the **Bangla Language Foundation (BLF)** project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added - Phase 0.1 Source Integrity Recovery & Evidence Hardening
- **Source Integrity Auditor**: Implemented `scripts/audit_sources.py` providing deterministic cross-identifier verification (ACL Anthology IDs, arXiv IDs, UD repository canonical names, and field-level evidence requirements).
- **Source Audit Ledger**: Established `sources/registry/source-audit.jsonl` tracking corrections and quarantine rationale for historical candidate misattributions.
- **Field-Level Verification Schema**: Upgraded `schemas/v0_1/source.schema.json` and `sources/registry/sources.json` to require explicit `verification` blocks with primary evidence URLs, access dates, and verified field tuples.
- **Regression Test Suite**: Added `tests/test_source_audit.py` guaranteeing automated detection and rejection of known false identifier signatures (e.g. arXiv:2206.14051, ACL 2021.wnut-1.14, ACL 2022.findings-emnlp.319).
- **Hardened Source Registry**: 16 fully verified primary sources across Tier A, B, and D, 1 partially verified source (`BPCC-BENGALI-2023`), and 4 quarantined historical candidate entries.
- **Epistemic Anti-Slop Expansion**: Updated `docs/research-writing-policy.md` and `.ai/checks/anti-ai-slop.md` with explicit definitions and prohibitions against Epistemic AI Slop (identifier fabrication, blended metadata, invented statistics, circular LLM verification).
- **Calibrated Gap Analysis**: Updated `research/gap-analysis/phase-0-gap-analysis.md` with explicit epistemic status tags (`[SUPPORTED]`, `[PARTIALLY_SUPPORTED]`, `[NOT_YET_VERIFIED]`).

---

## [0.1.0] - 2026-08-27

### Added
- **Repository Architecture & Tooling**: Initial project directory layout spanning `data/`, `ontology/`, `schemas/`, `sources/`, `research/`, `scripts/`, `src/`, `tests/`, and `docs/` (Software and research scaffolding; no public dataset release).
- **JSON Schemas (v0.1 Draft)**: Draft JSON Schema specifications for `utterance`, `sentence_family`, `source`, and `synthetic_provenance`.
- **Python Core Library (`src/blf/`)**:
  - `blf.linguistics.normalizer`: Bengali Unicode NFC normalization, Dari mapping, and character range validation.
  - `blf.linguistics.tags`: Enums for register, dialect, code-switching type, quality tier, and validation status.
  - `blf.core.models`: Typed dataclasses for core linguistic entities.
  - `blf.core.quality`: Quality tier invariant enforcement functions.
  - `blf.provenance.tracker`: Cryptographic SHA-256 and prompt hash tracking.
  - `blf.validation.validators`: Self-contained JSON schema validator.
- **Verification Scripts**:
  - `scripts/validate_schemas.py`: Verifies JSON schemas and test fixtures.
  - `scripts/validate_sources.py`: Validates `sources/registry/sources.json` entries.
  - `scripts/check_anti_slop.py`: Scans documentation for AI filler and canned phrasing.
  - `scripts/unicode_normalizer.py`: CLI for Unicode normalization.
- **Source Registry**: Seeded `sources/registry/sources.json` with initial verified records from Bangla Academy, Suniti Kumar Chatterji, and Universal Dependencies.
- **Automated Test Suite**: 13 unit tests covering normalization, schema invariants, source registry format, and anti-slop detection.
- **Research Documentation**: Comprehensive guides for architecture, research methodology, data quality model, provenance and licensing, reproducibility, and research writing.
