# Changelog

All notable changes to the **Bangla Language Foundation (BLF)** project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added - Phase 0.3 Artifact-Specific License, Authorship & Bibliographic Consistency Audit
- **Artifact-Specific License Schema**: Upgraded `schemas/v0_1/source.schema.json` to model individual resource artifacts (`PAPER`, `CODE`, `DATASET`, `MODEL`, `CORPUS`, `RULEBOOK`, `DICTIONARY`) with distinct licenses, copyright states, locators, and redistribution rights.
- **BanglaBERT License & Artifact Hardening**: Aligned `BANGLA2B-2022` primary repository and model license to `CC-BY-NC-SA-4.0` (matching canonical `csebuetnlp/banglabert` LICENSE) and added separate paper (`CC-BY-4.0` open access) and web crawl corpus artifacts.
- **BanglaNMT Authorship & License Correction**: Replaced blended author metadata with verified canonical author list (*Tahmid Hasan, Abhik Bhattacharjee, Kazi Samin, Md Saiful Islam, M. Sohel Rahman, and Rifat Shahriyar*, EMNLP 2020, pp. 2612–2623) and verified `CC-BY-NC-SA-4.0` repository license.
- **BnSentMix Repository License Correction**: Corrected declared license of `BNSENTMIX-2025` from MIT to `Apache-2.0` (matching canonical `Nishita2000/BnSentMix` repo) and calibrated redistribution of social media text to `restricted_or_requires_review`.
- **Bangla Academy Locators Cleanup**: Eliminated synthetic locator strings, binding `BA-SPELL-2016` to ISBN `984-07-5531-5` and `BA-REGDICT-1965` to LoC LCCN `74930105`.
- **Auditor & Test Expansion**: Enhanced `scripts/audit_sources.py` with canonical author overlap checking and added 2 regression tests in `tests/test_source_audit.py` (total 25 unit tests, 100% passing).
- **Refrozen Phase 0.3 Manifest**: Generated `research/phase-0-manifest.json` sealing the Phase 0.3 baseline with fresh SHA-256 hashes.

### Added - Phase 0.2 Claim-Level Evidence Verification & Final Source Freeze
- **Frozen Evidence Baseline**: Created `research/phase-0-manifest.json` sealing the Phase 0 research foundation with cryptographic SHA-256 checksums across all core registries, schemas, and matrices.
- **Claim-Level Evidence Architecture**: Upgraded `schemas/v0_1/source.schema.json` and `sources/registry/sources.json` to bind individual field assertions (`title`, `year`, `edition`, `license`, `size`) to specific primary evidence objects and locators.
- **Semantic Identifier Matching**: Extended `scripts/audit_sources.py` with deterministic semantic title token similarity and author matching to reject false identifier attributions (e.g. offensive-span detection cited as BanglaBERT).
- **BanglaBERT Publication Correction**: Resolved canonical BanglaBERT identifiers to ACL: `2022.findings-naacl.98` (DOI: `10.18653/v1/2022.findings-naacl.98`, arXiv: `2101.00204`), correcting false reference `2022.naacl-main.185`.
- **Bangla Academy Grammar Correction**: Resolved canonical reference to *Pramita Bangla Bhashar Byakaran* (`BA-GRAM-2011`, 2011, 2 vols, LCCN 2012323386) edited by Rafiqul Islam and Pabitra Sarkar, correcting conflated 2012 3-volume record.
- **Explicit Legal Status Separation**: Decoupled `copyright_status`, `license`, and `redistribution_permission` across all sources to prevent unwarranted assumption of open licenses on printed monographs.
- **Expanded Regression Tests**: Added tests in `tests/test_source_audit.py` proving semantic rejection of false ACL/arXiv identifiers and refusal of generic homepages without locators.

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
