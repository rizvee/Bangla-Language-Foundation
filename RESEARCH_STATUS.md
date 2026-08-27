# Research & Dataset Status — BLF

Last Updated: 2026-08-27

---

## 1. Project Phase
- **Current Phase**: Phase 0 — Research Source Landscape & Gap Analysis
- **Milestone State**: Bootstrap & Infrastructure Complete
- **Primary Branch**: `main`

---

## 2. Quantitative Metrics (Verifiable State)

| Metric | Current Value | Notes |
|---|---|---|
| **Schemas Authoring** | 4 schemas (`v0.1-draft`) | Utterance, Sentence Family, Source, Synthetic Provenance |
| **Verified Sources in Registry** | 4 references | Tier A (2), Tier B (1), Tier D (1) |
| **Test Fixtures** | 2 fixtures | 1 Gold BDSB Canonical, 1 Synthetic Sylheti Variant |
| **Automated Tests** | 13 unit tests | 100% passing across normalizer, schemas, sources, anti-slop |
| **Clean Documentation Files** | 10+ core docs | 0 AI-slop violations detected |
| **Dataset Scale** | 0 production records | Mass generation blocked until Phase 3/6 |

---

## 3. Active Components & Verification

- **Unicode Normalization**: Implemented in `src/blf/linguistics/normalizer.py` with NFC normalization, Bengali punctuation mapping, and character ratio verification.
- **Source Registry**: Implemented in `sources/registry/sources.json` and validated by `scripts/validate_sources.py`.
- **Anti-AI-Slop Checker**: Implemented in `scripts/check_anti_slop.py` scanning documentation for rhetorical padding and canned formulas.
- **Data Quality Invariants**: Implemented in `src/blf/core/quality.py` enforcing strict metadata and tier isolation.

---

## 4. Known Limitations & Research Gaps

1. **Source Coverage**: Registry currently contains 4 baseline sources; comprehensive literature survey is the primary task of Phase 0.
2. **Ontology Depth**: Semantic frames and construction catalogues are drafted in schema format but await formal frame catalog entries.
3. **Dialect Representations**: Dialectal markers require further empirical validation from regional audio transcripts and dialect dictionaries before scaling beyond test fixtures.
