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
| **Verified Sources in Registry** | 15 references | Tier A (4), Tier B (5), Tier D (6) |
| **Evidence Matrix Entries** | 15 resources | Machine-readable in `research/dataset-landscape/evidence-matrix.json` |
| **Test Fixtures** | 2 fixtures | 1 Gold BDSB Canonical, 1 Synthetic Sylheti Variant |
| **Automated Tests** | 17 unit tests | 100% passing across normalizer, schemas, sources, docs, anti-slop |
| **Dataset Scale** | 0 production records | In research & development (Phase 0 complete; no dataset released) |
| **Dataset License** | Undecided | Pending source-license and redistribution audit |

---

## 3. Active Components & Verification

- **Evidence Matrix & Landscape**: Implemented in `research/dataset-landscape/evidence-matrix.json` and `landscape.md`.
- **Literature & Grammar Survey**: Implemented in `research/literature-review/bangla-academy-map.md` and `linguistic-sources.md`.
- **Multi-Dimensional Gap Analysis**: Implemented in `research/gap-analysis/phase-0-gap-analysis.md`.
- **Unicode Normalization**: Implemented in `src/blf/linguistics/normalizer.py` with NFC normalization, Bengali punctuation mapping, and character ratio verification.
- **Source Registry**: Implemented in `sources/registry/sources.json` and validated by `scripts/validate_sources.py`.
- **Anti-AI-Slop Checker**: Implemented in `scripts/check_anti_slop.py` scanning documentation for rhetorical padding and canned formulas.
- **Data Quality Invariants**: Implemented in `src/blf/core/quality.py` enforcing strict metadata and tier isolation.

---

## 4. Known Limitations & Research Gaps

1. **Source Coverage**: Phase 0 baseline catalog contains 15 verified primary sources; Phase 1 will expand linguistic knowledge maps for specific verb classes and regional clitics.
2. **Ontology Depth**: Semantic frames and construction catalogues are drafted in schema format but await formal frame catalog entries in Phase 2.
3. **Dialect Representations**: Dialectal markers for Sylheti and Chatgaya are mapped theoretically; empirical spoken audio transcriptions will be ingested in Phase 3/4.
