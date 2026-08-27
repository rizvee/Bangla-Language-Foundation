# Research & Dataset Status — BLF

Last Updated: 2026-08-28

---

## 1. Project Phase
- **Current Phase**: Phase 1B — Morphosyntactic & Inflectional Paradigm Engine (Complete)
- **Milestone State**: Phase 1B Operational Morphology Engine & Verified Paradigm Catalogs
- **Primary Branch**: `main`

---

## 2. Quantitative Metrics (Verifiable State)

| Metric | Current Value | Notes |
|---|---|---|
| **Schemas Authoring** | 9 schemas (`v0.1-draft-1.1`) | Utterance, Sentence Family, Source, Synthetic Provenance, Linguistic Evidence, Linguistic Claim, Linguistic Rule, Linguistic Example, Inflectional Paradigm |
| **Verified Sources in Registry** | 16 references | Tier A (4), Tier B (4), Tier D (8) with artifact breakdowns |
| **Partially Verified Sources** | 1 reference | BPCC Bengali Parallel Component |
| **Quarantined Sources** | 4 references | Recorded in `sources/registry/source-audit.jsonl` |
| **Linguistic Evidence Items** | 21 items | 100% verified against primary sources (`ontology/evidence/pilot_evidence.json`) |
| **Atomic Linguistic Claims** | 36 claims | 100% evidence-grounded across 5 levels (`ontology/claims/pilot_claims.json`) |
| **Declarative Linguistic Rules** | 20 rules | 100% claim-supported (`ontology/rules/pilot_rules.json`) |
| **Provenance-Backed Examples** | 22 examples | Source-cited and verified (`ontology/examples/pilot_examples.json`) |
| **Inflectional Paradigms** | 13 paradigms | Nouns (4), Pronouns (5), Verbs (4) (`ontology/paradigms/`) |
| **Morphology Engine Coverage** | 100% Deterministic | Nominal Declension, Pronominal Matrix, Verbal Conjugator (`src/blf/linguistics/morphology/`) |
| **Terminology Mappings** | 14 mappings | Aligned across 5 frameworks (`terminology-crosswalk.json`) |
| **Framework Conflict Relations** | 3 relations | Resolved with canonical BLF modeling (`conflicts.json`) |
| **Test Fixtures** | 2 fixtures | 1 Gold BDSB Canonical, 1 Synthetic Sylheti Variant |
| **Automated Tests** | 44 unit tests | 100% passing across normalizer, schemas, sources, knowledge layer, morphology engine, docs, anti-slop |
| **Dataset Scale** | 0 production records | In research & knowledge modeling (no mass generation) |
| **Dataset License** | Undecided | Pending source-license and redistribution audit |

---

## 3. Active Components & Verification

- **Frozen Evidence Baseline**: Implemented in `research/phase-0-manifest.json` (Phase 0.3) with cryptographic SHA-256 checksums across all core registries and schemas.
- **Claim-Level & Artifact-Specific Source Auditor**: Implemented in `scripts/audit_sources.py` and `sources/registry/source-audit.jsonl` enforcing semantic identifier matching, author list validation, and artifact license precision.
- **Artifact-Specific License Modeling**: Implemented in `schemas/v0_1/source.schema.json` supporting separate `artifacts` arrays for Paper, Code, Dataset, and Model components.
- **Evidence Matrix & Landscape**: Implemented in `research/dataset-landscape/evidence-matrix.json` and `landscape.md`.
- **Literature & Grammar Survey**: Implemented in `research/literature-review/bangla-academy-map.md` and `linguistic-sources.md`.
- **Multi-Dimensional Gap Analysis**: Implemented in `research/gap-analysis/phase-0-gap-analysis.md` with explicit epistemic status tags (`[SUPPORTED]`, `[NOT_YET_VERIFIED]`).
- **Unicode Normalization**: Implemented in `src/blf/linguistics/normalizer.py` with NFC normalization, Bengali punctuation mapping, and character ratio verification.
- **Source Registry**: Implemented in `sources/registry/sources.json` with claim-level evidence bindings and validated by `scripts/validate_sources.py`.
- **Anti-AI-Slop Checker**: Implemented in `scripts/check_anti_slop.py` scanning documentation for rhetorical padding and canned formulas.
- **Data Quality Invariants**: Implemented in `src/blf/core/quality.py` enforcing strict metadata and tier isolation.

---

## 4. Known Limitations & Research Gaps

1. **Source Coverage**: Phase 0.3 frozen catalog contains 16 verified primary sources; Phase 1 will expand linguistic knowledge maps for specific verb classes and regional clitics.
2. **Ontology Depth**: Semantic frames and construction catalogues are drafted in schema format but await formal frame catalog entries in Phase 2.
3. **Dialect Representations**: Dialectal markers for Sylheti are grounded in SOAS field documentation (Simard et al., 2014) and Shahidullah (1965); empirical spoken audio transcriptions will be ingested in Phase 3/4.
