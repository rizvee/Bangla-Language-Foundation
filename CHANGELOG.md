# Changelog

All notable changes to the **Bangla Language Foundation (BLF)** project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added - Phase 0 Research Source Landscape & Gap Analysis
- **Machine-Readable Evidence Matrix**: `research/dataset-landscape/evidence-matrix.json` covering 15 verified primary resources across Tier A, B, and D with fine-grained modality and licensing metadata.
- **Dataset Landscape Review**: `research/dataset-landscape/landscape.md` surveying existing monolingual, syntactic, parallel MT, speech, transliteration, and code-mixed corpora.
- **Bangla Academy Resource Map**: `research/literature-review/bangla-academy-map.md` cataloging official national grammar, orthography, dialect dictionary, and lexicographical publications.
- **Descriptive Linguistics Survey**: `research/literature-review/linguistic-sources.md` formalizing syntactic, morphological, and pro-drop models from Chatterji, Azad, Thompson, and Sarkar.
- **Multi-Dimensional Gap Analysis**: `research/gap-analysis/phase-0-gap-analysis.md` assessing 10 empirical gaps across semantics, sentence families, conversation, Banglish, and regional syntax.
- **Phase 0 Research Findings**: `research/findings/phase-0-findings.md` synthesizing discoveries, adversarial review results, and recommendations for Phase 1.
- **Expanded Source Registry**: `sources/registry/sources.json` expanded to 15 verified primary sources with exact citations and checksums.

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
